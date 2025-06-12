"""
Gestionnaire d'orchestration Prefect pour intégration Gradio
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

try:
    from prefect import get_client
    from prefect.client.schemas.filters import FlowFilter, FlowRunFilter
    from prefect.client.schemas.objects import FlowRun, Flow
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False
    print("⚠️ Prefect non disponible - Fonctions d'orchestration désactivées")

class OrchestrationManager:
    """Gestionnaire pour intégrer Prefect avec l'interface Gradio"""
    
    def __init__(self):
        self.prefect_available = PREFECT_AVAILABLE
        self.api_url = "http://localhost:4200/api"
        self.status_cache = {}
        self.last_update = None
        
    async def get_prefect_status(self) -> Dict[str, Any]:
        """Récupérer le statut général de Prefect"""
        if not self.prefect_available:
            return {
                "status": "disabled",
                "message": "Prefect non installé ou non configuré",
                "server_running": False,
                "flows_count": 0,
                "recent_runs": []
            }
        
        try:
            async with get_client() as client:
                # Vérifier la connexion au serveur
                health = await client.api_healthcheck()
                
                # Récupérer la liste des flows
                flows = await client.read_flows()
                
                # Récupérer les runs récents
                recent_runs = await client.read_flow_runs(
                    limit=10,
                    sort="EXPECTED_START_TIME_DESC"
                )
                
                return {
                    "status": "connected",
                    "message": "✅ Serveur Prefect connecté",
                    "server_running": True,
                    "api_url": self.api_url,
                    "flows_count": len(flows),
                    "recent_runs": [
                        {
                            "id": str(run.id),
                            "name": run.name,
                            "flow_name": run.flow_name,
                            "state": run.state.type if run.state else "Unknown",
                            "start_time": run.start_time.isoformat() if run.start_time else None,
                            "duration": self._calculate_duration(run)
                        }
                        for run in recent_runs[:5]
                    ],
                    "flows": [
                        {
                            "id": str(flow.id),
                            "name": flow.name,
                            "created": flow.created.isoformat()
                        }
                        for flow in flows[:10]
                    ]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Erreur connexion Prefect: {str(e)}",
                "server_running": False,
                "flows_count": 0,
                "recent_runs": []
            }
    
    async def trigger_workflow(self, workflow_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Déclencher un workflow Prefect"""
        if not self.prefect_available:
            return {
                "success": False,
                "message": "Prefect non disponible",
                "run_id": None
            }
        
        try:
            async with get_client() as client:
                # Trouver le déploiement
                deployments = await client.read_deployments()
                target_deployment = None
                
                for deployment in deployments:
                    if workflow_name in deployment.name:
                        target_deployment = deployment
                        break
                
                if not target_deployment:
                    return {
                        "success": False,
                        "message": f"Workflow '{workflow_name}' non trouvé",
                        "run_id": None
                    }
                
                # Déclencher l'exécution
                flow_run = await client.create_flow_run_from_deployment(
                    deployment_id=target_deployment.id,
                    parameters=parameters or {}
                )
                
                return {
                    "success": True,
                    "message": f"✅ Workflow '{workflow_name}' démarré",
                    "run_id": str(flow_run.id),
                    "deployment_name": target_deployment.name
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Erreur déclenchement: {str(e)}",
                "run_id": None
            }
    
    async def get_workflow_status(self, run_id: str) -> Dict[str, Any]:
        """Récupérer le statut d'un workflow spécifique"""
        if not self.prefect_available:
            return {"status": "unknown", "message": "Prefect non disponible"}
        
        try:
            async with get_client() as client:
                flow_run = await client.read_flow_run(run_id)
                
                return {
                    "status": flow_run.state.type if flow_run.state else "Unknown",
                    "message": flow_run.state.message if flow_run.state else "Aucun message",
                    "start_time": flow_run.start_time.isoformat() if flow_run.start_time else None,
                    "end_time": flow_run.end_time.isoformat() if flow_run.end_time else None,
                    "duration": self._calculate_duration(flow_run),
                    "flow_name": flow_run.flow_name,
                    "parameters": flow_run.parameters
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erreur récupération statut: {str(e)}"
            }
    
    def _calculate_duration(self, flow_run) -> Optional[float]:
        """Calculer la durée d'exécution d'un flow run"""
        if flow_run.start_time and flow_run.end_time:
            duration = flow_run.end_time - flow_run.start_time
            return duration.total_seconds()
        return None
    
    def format_status_for_display(self, status: Dict[str, Any]) -> str:
        """Formater le statut pour affichage dans Gradio"""
        if not status.get("server_running"):
            return f"""
## 🔴 Orchestration Prefect - Hors ligne

**Statut**: {status.get('message', 'Non connecté')}

### Actions recommandées:
1. Démarrer Prefect: `./scripts/start_prefect.sh`
2. Vérifier l'installation: `pip install prefect>=2.14.0`
3. Configurer l'API URL: `prefect config set PREFECT_API_URL="http://localhost:4200/api"`
            """.strip()
        
        flows_info = ""
        if status.get("flows"):
            flows_info = "### 🔄 Workflows disponibles:\n"
            for flow in status["flows"][:5]:
                flows_info += f"- **{flow['name']}** (créé: {flow['created'][:10]})\n"
        
        recent_runs_info = ""
        if status.get("recent_runs"):
            recent_runs_info = "### 📊 Exécutions récentes:\n"
            for run in status["recent_runs"][:3]:
                state_emoji = self._get_state_emoji(run['state'])
                duration_str = f" ({run['duration']:.1f}s)" if run['duration'] else ""
                recent_runs_info += f"- {state_emoji} **{run['name']}** - {run['state']}{duration_str}\n"
        
        return f"""
## 🟢 Orchestration Prefect - En ligne

**Serveur**: {status.get('api_url', 'localhost:4200')}
**Workflows**: {status.get('flows_count', 0)} disponibles

{flows_info}

{recent_runs_info}

**Dernière mise à jour**: {datetime.now().strftime('%H:%M:%S')}
        """.strip()
    
    def _get_state_emoji(self, state: str) -> str:
        """Retourner l'emoji correspondant à l'état"""
        state_emojis = {
            "COMPLETED": "✅",
            "RUNNING": "🏃",
            "PENDING": "⏳",
            "FAILED": "❌",
            "CANCELLED": "⚠️",
            "CRASHED": "💥"
        }
        return state_emojis.get(state, "❓")
    
    def get_available_workflows(self) -> List[Tuple[str, str]]:
        """Retourner la liste des workflows disponibles pour l'interface"""
        workflows = [
            ("health_check", "🩺 Vérification santé système"),
            ("batch_processing", "📄 Traitement par lot de documents"),
            ("database_maintenance", "🛠️ Maintenance base de données"),
            ("performance_monitoring", "📊 Surveillance performance"),
            ("smoke_tests", "🧪 Tests smoke"),
            ("cleanup_files", "🧹 Nettoyage fichiers anciens"),
            ("weekly_maintenance", "📅 Maintenance hebdomadaire"),
            ("automated_tests", "🔬 Tests automatisés complets")
        ]
        return workflows
    
    async def trigger_health_check(self) -> Dict[str, Any]:
        """Déclencher une vérification de santé"""
        return await self.trigger_workflow("health-monitoring", {
            "alert_threshold": 70
        })
    
    async def trigger_batch_processing(self, folder_path: str, api_key: str) -> Dict[str, Any]:
        """Déclencher un traitement par lot"""
        return await self.trigger_workflow("nightly-document-processing", {
            "watch_folder": folder_path,
            "api_key": api_key
        })
    
    async def trigger_maintenance(self) -> Dict[str, Any]:
        """Déclencher une maintenance"""
        return await self.trigger_workflow("database-maintenance", {
            "vacuum_database": True,
            "backup_database": True,
            "optimize_collections": True
        })
    
    async def trigger_smoke_tests(self, api_key: str) -> Dict[str, Any]:
        """Déclencher les tests smoke"""
        return await self.trigger_workflow("daily-smoke-tests", {
            "api_key": api_key
        })
    
    def create_workflow_parameters_form(self, workflow_type: str) -> Dict[str, Any]:
        """Créer un formulaire de paramètres pour un workflow"""
        forms = {
            "batch_processing": {
                "folder_path": {"type": "text", "label": "Dossier à traiter", "default": "./data/inbox"},
                "api_key": {"type": "password", "label": "Clé API Mistral", "required": True}
            },
            "health_check": {
                "alert_threshold": {"type": "number", "label": "Seuil d'alerte", "default": 70, "min": 0, "max": 100}
            },
            "maintenance": {
                "backup_database": {"type": "checkbox", "label": "Sauvegarder la base", "default": True},
                "optimize_collections": {"type": "checkbox", "label": "Optimiser les collections", "default": True}
            },
            "smoke_tests": {
                "api_key": {"type": "password", "label": "Clé API Mistral", "required": True}
            }
        }
        
        return forms.get(workflow_type, {})
    
    async def get_workflow_logs(self, run_id: str) -> List[Dict[str, Any]]:
        """Récupérer les logs d'un workflow"""
        if not self.prefect_available:
            return []
        
        try:
            async with get_client() as client:
                logs = await client.read_logs(run_id)
                return [
                    {
                        "timestamp": log.timestamp.isoformat(),
                        "level": log.level,
                        "message": log.message
                    }
                    for log in logs
                ]
        except Exception:
            return []
    
    def save_workflow_result(self, run_id: str, result: Dict[str, Any]) -> str:
        """Sauvegarder le résultat d'un workflow"""
        try:
            results_dir = Path("./data/workflow_results")
            results_dir.mkdir(exist_ok=True)
            
            result_file = results_dir / f"workflow_result_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
            return str(result_file)
        except Exception as e:
            return f"Erreur sauvegarde: {str(e)}"

# Instance globale pour utilisation dans Gradio
orchestration_manager = OrchestrationManager()