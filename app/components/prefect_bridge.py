"""
Pont entre DontREADME et Prefect pour utilisation directe
Ce module permet d'utiliser les workflows Prefect directement depuis l'application
"""

import asyncio
import os
from typing import Dict, Any, Optional
from pathlib import Path

# Import conditionnel de Prefect - Temporairement désactivé pour tests
try:
    # from workflows.batch_processing import batch_document_flow, process_folder_documents
    # from workflows.maintenance import database_maintenance_flow
    # from workflows.monitoring import health_check_flow, performance_monitoring_flow
    # from workflows.testing import smoke_testing_flow
    WORKFLOWS_AVAILABLE = False  # Temporaire pour tests
    print(" Workflows temporairement désactivés pour validation système")
except ImportError:
    WORKFLOWS_AVAILABLE = False
    print("[WARN] Workflows Prefect non disponibles")

class PrefectBridge:
    """Pont pour exécuter les workflows Prefect depuis l'interface"""
    
    def __init__(self):
        self.workflows_available = WORKFLOWS_AVAILABLE
        
    def is_available(self) -> bool:
        """Vérifier si les workflows sont disponibles"""
        return self.workflows_available
    
    async def process_documents_batch(self, 
                                    documents_folder: str,
                                    api_key: str,
                                    file_extensions: list = None,
                                    chunk_size: int = None) -> Dict[str, Any]:
        """Traiter des documents en lot via Prefect"""
        if not self.workflows_available:
            return {
                "status": "error",
                "message": "Workflows Prefect non disponibles"
            }
        
        try:
            result = await batch_document_flow(
                documents_folder=documents_folder,
                api_key=api_key,
                file_extensions=file_extensions or ['.pdf', '.docx', '.txt'],
                chunk_size=chunk_size,
                template_type="auto"
            )
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erreur traitement batch: {str(e)}"
            }
    
    async def check_system_health(self, alert_threshold: int = 70) -> Dict[str, Any]:
        """Vérifier la santé du système via Prefect"""
        if not self.workflows_available:
            return {
                "status": "error",
                "message": "Workflows Prefect non disponibles"
            }
        
        try:
            result = await health_check_flow(
                alert_threshold=alert_threshold
            )
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erreur vérification santé: {str(e)}"
            }
    
    async def run_maintenance(self, 
                            vacuum_database: bool = True,
                            backup_database: bool = True,
                            optimize_collections: bool = True) -> Dict[str, Any]:
        """Lancer une maintenance via Prefect"""
        if not self.workflows_available:
            return {
                "status": "error",
                "message": "Workflows Prefect non disponibles"
            }
        
        try:
            result = await database_maintenance_flow(
                vacuum_database=vacuum_database,
                backup_database=backup_database,
                optimize_collections=optimize_collections
            )
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erreur maintenance: {str(e)}"
            }
    
    async def run_smoke_tests(self, api_key: str) -> Dict[str, Any]:
        """Lancer les tests smoke via Prefect"""
        if not self.workflows_available:
            return {
                "status": "error",
                "message": "Workflows Prefect non disponibles"
            }
        
        try:
            result = await smoke_testing_flow(api_key=api_key)
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erreur tests smoke: {str(e)}"
            }
    
    async def monitor_performance(self, generate_detailed_report: bool = True) -> Dict[str, Any]:
        """Surveiller les performances via Prefect"""
        if not self.workflows_available:
            return {
                "status": "error",
                "message": "Workflows Prefect non disponibles"
            }
        
        try:
            result = await performance_monitoring_flow(
                generate_detailed_report=generate_detailed_report
            )
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erreur monitoring: {str(e)}"
            }
    
    def run_sync(self, coro) -> Dict[str, Any]:
        """Exécuter une coroutine de manière synchrone pour Gradio"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(coro)
            loop.close()
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erreur exécution: {str(e)}"
            }
    
    def batch_process_sync(self, 
                          documents_folder: str,
                          api_key: str,
                          file_extensions: list = None,
                          chunk_size: int = None) -> str:
        """Version synchrone pour Gradio du traitement batch"""
        result = self.run_sync(
            self.process_documents_batch(
                documents_folder, api_key, file_extensions, chunk_size
            )
        )
        return self._format_result_for_display(result, "Traitement par lot")
    
    def health_check_sync(self, alert_threshold: int = 70) -> str:
        """Version synchrone pour Gradio de la vérification santé"""
        result = self.run_sync(self.check_system_health(alert_threshold))
        return self._format_result_for_display(result, "Vérification santé")
    
    def maintenance_sync(self, 
                        vacuum_database: bool = True,
                        backup_database: bool = True,
                        optimize_collections: bool = True) -> str:
        """Version synchrone pour Gradio de la maintenance"""
        result = self.run_sync(
            self.run_maintenance(vacuum_database, backup_database, optimize_collections)
        )
        return self._format_result_for_display(result, "Maintenance")
    
    def smoke_tests_sync(self, api_key: str) -> str:
        """Version synchrone pour Gradio des tests smoke"""
        if not api_key.strip():
            return "[ERROR] Clé API Mistral requise pour les tests"
        
        result = self.run_sync(self.run_smoke_tests(api_key))
        return self._format_result_for_display(result, "Tests smoke")
    
    def performance_monitoring_sync(self, generate_detailed_report: bool = True) -> str:
        """Version synchrone pour Gradio du monitoring"""
        result = self.run_sync(self.monitor_performance(generate_detailed_report))
        return self._format_result_for_display(result, "Monitoring performance")
    
    def _format_result_for_display(self, result: Dict[str, Any], operation_name: str) -> str:
        """Formater le résultat pour affichage dans Gradio"""
        if not isinstance(result, dict):
            return f"[ERROR] Résultat invalide pour {operation_name}"
        
        status = result.get("status", "unknown")
        
        if status == "error":
            return f"""
[ERROR] **Échec de {operation_name}**

**Erreur**: {result.get('message', 'Erreur inconnue')}

**Actions recommandées**:
- Vérifier que Prefect est démarré
- Vérifier les paramètres d'entrée
- Consulter les logs pour plus de détails
            """.strip()
        
        elif status in ["success", "completed"]:
            # Affichage selon le type d'opération
            if "batch" in operation_name.lower():
                return self._format_batch_result(result)
            elif "santé" in operation_name.lower() or "health" in operation_name.lower():
                return self._format_health_result(result)
            elif "maintenance" in operation_name.lower():
                return self._format_maintenance_result(result)
            elif "test" in operation_name.lower():
                return self._format_test_result(result)
            elif "monitoring" in operation_name.lower():
                return self._format_monitoring_result(result)
            else:
                return f"[OK] {operation_name} terminé avec succès"
        
        else:
            return f"""
[WARN] **{operation_name} - Statut: {status}**

**Message**: {result.get('message', 'Aucun message')}
**Démarré**: {result.get('started_at', 'N/A')}
            """.strip()
    
    def _format_batch_result(self, result: Dict[str, Any]) -> str:
        """Formater les résultats de traitement batch"""
        summary = result.get("summary", result)
        
        docs_processed = summary.get("documents_processed", 0)
        docs_failed = summary.get("documents_failed", 0)
        total_time = summary.get("total_processing_time", 0)
        success_rate = summary.get("success_rate", 0)
        
        return f"""
[OK] **Traitement par lot terminé**

 **Résultats**:
- Documents traités: {docs_processed}
- Échecs: {docs_failed}
- Taux de succès: {success_rate}%
- Temps total: {total_time:.1f}s

 **Terminé**: {result.get('completed_at', 'N/A')[:19]}
        """.strip()
    
    def _format_health_result(self, result: Dict[str, Any]) -> str:
        """Formater les résultats de vérification santé"""
        health_summary = result.get("health_summary", {})
        detailed_health = result.get("detailed_health", {})
        
        score = health_summary.get("score", detailed_health.get("health_score", 0))
        status = health_summary.get("status", detailed_health.get("overall_status", "unknown"))
        
        status_emoji = "" if status == "healthy" else "" if status == "degraded" else ""
        
        return f"""
{status_emoji} **Vérification de santé terminée**

 **Score de santé**: {score}/100
 **Statut**: {status.upper()}

 **Système**:
- CPU: {detailed_health.get('system', {}).get('cpu_percent', 0):.1f}%
- Mémoire: {detailed_health.get('system', {}).get('memory_percent', 0):.1f}%
- Disque: {detailed_health.get('system', {}).get('disk_percent', 0):.1f}%

 **ChromaDB**: {detailed_health.get('chromadb', {}).get('status', 'unknown')}

 **Vérifié**: {result.get('completed_at', 'N/A')[:19]}
        """.strip()
    
    def _format_maintenance_result(self, result: Dict[str, Any]) -> str:
        """Formater les résultats de maintenance"""
        operations = result.get("operations", {})
        duration = result.get("duration_seconds", 0)
        
        backup_status = operations.get("backup", {}).get("status", "unknown")
        optimization_status = operations.get("optimization", {}).get("status", "unknown")
        
        return f"""
[OK] **Maintenance terminée**

 **Opérations**:
- Sauvegarde: {'[OK]' if backup_status == 'success' else '[ERROR]'} {backup_status}
- Optimisation: {'[OK]' if optimization_status == 'success' else '[ERROR]'} {optimization_status}

 **Durée**: {duration:.1f} secondes
📅 **Terminé**: {result.get('completed_at', 'N/A')[:19]}

 **Amélioration santé**: {result.get('health_improvement', {}).get('improvement', 0):+.1f} points
        """.strip()
    
    def _format_test_result(self, result: Dict[str, Any]) -> str:
        """Formater les résultats de tests"""
        passed = result.get("passed_tests", 0)
        total = result.get("total_tests", 0)
        success_rate = result.get("success_rate", 0)
        duration = result.get("duration_seconds", 0)
        
        return f"""
 **Tests smoke terminés**

 **Résultats**:
- Tests réussis: {passed}/{total}
- Taux de succès: {success_rate}%
- Durée: {duration:.1f}s

[OK] **Système**: {'OK' if result.get('all_tests_passed', False) else 'KO'}

 **Terminé**: {result.get('completed_at', 'N/A')[:19]}
        """.strip()
    
    def _format_monitoring_result(self, result: Dict[str, Any]) -> str:
        """Formater les résultats de monitoring"""
        performance_score = result.get("performance_score", 0)
        anomalies = result.get("anomalies", [])
        
        return f"""
 **Monitoring performance terminé**

 **Score performance**: {performance_score}/100
🚨 **Anomalies détectées**: {len(anomalies)}

 **Analysé**: {result.get('completed_at', 'N/A')[:19]}

 **Rapport**: {result.get('performance_report', {}).get('report_file', 'Non généré')}
        """.strip()

# Instance globale
prefect_bridge = PrefectBridge()