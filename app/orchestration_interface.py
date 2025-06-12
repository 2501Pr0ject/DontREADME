"""
Interface Gradio pour l'orchestration Prefect
"""

import gradio as gr
import asyncio
import json
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from pathlib import Path

from app.components.orchestration_manager import orchestration_manager
from app.components.prefect_bridge import prefect_bridge

class OrchestrationInterface:
    """Interface Gradio pour gérer l'orchestration Prefect"""
    
    def __init__(self):
        self.manager = orchestration_manager
        self.current_runs = {}
        self.last_status_update = None
    
    def refresh_status(self) -> Tuple[str, str]:
        """Actualiser le statut de Prefect"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            status = loop.run_until_complete(self.manager.get_prefect_status())
            loop.close()
            
            self.last_status_update = datetime.now()
            formatted_status = self.manager.format_status_for_display(status)
            
            # Informations de connexion pour debug
            connection_info = f"""
**Statut connexion**: {'🟢 Connecté' if status.get('server_running') else '🔴 Déconnecté'}
**URL API**: {status.get('api_url', 'Non configuré')}
**Dernière vérification**: {self.last_status_update.strftime('%H:%M:%S')}
            """.strip()
            
            return formatted_status, connection_info
            
        except Exception as e:
            error_msg = f"""
## ❌ Erreur de connexion Prefect

**Erreur**: {str(e)}

### Actions de dépannage:
1. Vérifier que Prefect est démarré: `./scripts/start_prefect.sh`
2. Vérifier l'URL API: `prefect config view`
3. Tester la connexion: `curl http://localhost:4200/api/health`
            """.strip()
            
            return error_msg, f"❌ Erreur: {str(e)}"
    
    def trigger_workflow_action(self, workflow_type: str, **kwargs) -> Tuple[str, str]:
        """Déclencher une action de workflow"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if workflow_type == "health_check":
                result = loop.run_until_complete(self.manager.trigger_health_check())
            elif workflow_type == "batch_processing":
                folder_path = kwargs.get('folder_path', './data/inbox')
                api_key = kwargs.get('api_key', '')
                if not api_key:
                    return "❌ Clé API requise pour le traitement par lot", ""
                result = loop.run_until_complete(
                    self.manager.trigger_batch_processing(folder_path, api_key)
                )
            elif workflow_type == "maintenance":
                result = loop.run_until_complete(self.manager.trigger_maintenance())
            elif workflow_type == "smoke_tests":
                api_key = kwargs.get('api_key', '')
                if not api_key:
                    return "❌ Clé API requise pour les tests", ""
                result = loop.run_until_complete(
                    self.manager.trigger_smoke_tests(api_key)
                )
            else:
                return f"❌ Type de workflow inconnu: {workflow_type}", ""
            
            loop.close()
            
            if result.get('success'):
                run_id = result.get('run_id')
                self.current_runs[workflow_type] = run_id
                
                success_msg = f"""
✅ **Workflow démarré avec succès**

**Type**: {workflow_type}
**ID d'exécution**: {run_id}
**Déploiement**: {result.get('deployment_name', 'N/A')}
**Démarré à**: {datetime.now().strftime('%H:%M:%S')}

Vous pouvez suivre l'exécution dans l'interface web Prefect ou actualiser le statut.
                """.strip()
                
                return success_msg, run_id
            else:
                return f"❌ Échec du démarrage: {result.get('message')}", ""
                
        except Exception as e:
            return f"❌ Erreur lors du déclenchement: {str(e)}", ""
    
    def check_workflow_status(self, run_id: str) -> str:
        """Vérifier le statut d'un workflow en cours"""
        if not run_id:
            return "Aucun workflow sélectionné"
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            status = loop.run_until_complete(self.manager.get_workflow_status(run_id))
            loop.close()
            
            state_emoji = self.manager._get_state_emoji(status.get('status', 'UNKNOWN'))
            
            duration_info = ""
            if status.get('duration'):
                duration_info = f"**Durée**: {status['duration']:.1f} secondes\n"
            elif status.get('start_time'):
                start_time = datetime.fromisoformat(status['start_time'].replace('Z', '+00:00'))
                elapsed = (datetime.now() - start_time.replace(tzinfo=None)).total_seconds()
                duration_info = f"**Temps écoulé**: {elapsed:.1f} secondes\n"
            
            status_msg = f"""
{state_emoji} **Statut du workflow**

**État**: {status.get('status', 'UNKNOWN')}
**Flow**: {status.get('flow_name', 'N/A')}
**Message**: {status.get('message', 'Aucun message')}
{duration_info}
**Démarré**: {status.get('start_time', 'N/A')[:19] if status.get('start_time') else 'N/A'}
**Terminé**: {status.get('end_time', 'N/A')[:19] if status.get('end_time') else 'En cours'}
            """.strip()
            
            return status_msg
            
        except Exception as e:
            return f"❌ Erreur vérification statut: {str(e)}"
    
    def get_workflow_logs(self, run_id: str) -> str:
        """Récupérer les logs d'un workflow"""
        if not run_id:
            return "Aucun workflow sélectionné"
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logs = loop.run_until_complete(self.manager.get_workflow_logs(run_id))
            loop.close()
            
            if not logs:
                return "Aucun log disponible ou workflow en attente"
            
            log_lines = []
            for log in logs[-20:]:  # Derniers 20 logs
                timestamp = log['timestamp'][:19]  # Format YYYY-MM-DD HH:MM:SS
                level = log['level']
                message = log['message']
                log_lines.append(f"[{timestamp}] {level}: {message}")
            
            return "\n".join(log_lines)
            
        except Exception as e:
            return f"❌ Erreur récupération logs: {str(e)}"
    
    def create_orchestration_tab(self) -> gr.Tab:
        """Créer l'onglet d'orchestration Prefect"""
        
        with gr.Tab("🔄 Orchestration Prefect", id="orchestration") as tab:
            gr.Markdown("""
            ## 🚀 Gestion des Workflows Prefect
            
            Contrôlez et surveillez vos workflows d'automatisation directement depuis l'interface.
            """)
            
            # Section Statut
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### 📊 Statut du Système")
                    
                    status_display = gr.Markdown(
                        value="Chargement du statut...",
                        label="Statut Prefect"
                    )
                    
                    with gr.Row():
                        refresh_status_btn = gr.Button("🔄 Actualiser Statut", variant="secondary")
                        open_prefect_ui_btn = gr.Button("🌐 Interface Web Prefect", variant="primary")
                
                with gr.Column(scale=1):
                    connection_info_display = gr.Markdown(
                        value="Informations de connexion...",
                        label="Connexion"
                    )
            
            gr.Markdown("---")
            
            # Section Actions Rapides
            with gr.Row():
                gr.Markdown("### ⚡ Actions Rapides")
            
            with gr.Row():
                with gr.Column():
                    health_check_btn = gr.Button("🩺 Vérification Santé", variant="primary", scale=1)
                    maintenance_btn = gr.Button("🛠️ Maintenance DB", variant="secondary", scale=1)
                
                with gr.Column():
                    smoke_test_btn = gr.Button("🧪 Tests Smoke", variant="primary", scale=1)
                    batch_process_btn = gr.Button("📄 Traitement Batch", variant="secondary", scale=1)
                    
                with gr.Column():
                    api_key_quick = gr.Textbox(
                        label="Clé API (pour tests/batch)",
                        placeholder="Votre clé API Mistral...",
                        type="password",
                        scale=2
                    )
                    
                    batch_folder_quick = gr.Textbox(
                        label="Dossier batch (optionnel)",
                        placeholder="./data/inbox",
                        value="./data/inbox",
                        scale=1
                    )
            
            # Résultats des actions rapides
            quick_action_result = gr.Textbox(
                label="Résultat de l'action",
                interactive=False,
                lines=8
            )
            
            gr.Markdown("---")
            
            # Section Workflows Avancés
            with gr.Row():
                gr.Markdown("### 🔧 Workflows Avancés")
            
            with gr.Row():
                with gr.Column(scale=1):
                    workflow_selector = gr.Dropdown(
                        choices=[
                            ("batch_processing", "📄 Traitement par lot"),
                            ("health_check", "🩺 Vérification santé"),
                            ("maintenance", "🛠️ Maintenance complète"),
                            ("smoke_tests", "🧪 Tests smoke"),
                            ("performance_monitoring", "📊 Surveillance performance"),
                            ("cleanup_files", "🧹 Nettoyage fichiers")
                        ],
                        label="Type de workflow",
                        value="health_check"
                    )
                    
                    # Paramètres dynamiques selon le workflow
                    workflow_folder_path = gr.Textbox(
                        label="Dossier à traiter (batch processing)",
                        value="./data/inbox",
                        visible=False
                    )
                    
                    workflow_api_key = gr.Textbox(
                        label="Clé API Mistral",
                        type="password",
                        visible=False
                    )
                    
                    trigger_workflow_btn = gr.Button("🚀 Lancer Workflow", variant="primary")
                
                with gr.Column(scale=1):
                    workflow_result = gr.Textbox(
                        label="Résultat du workflow",
                        interactive=False,
                        lines=8
                    )
            
            # Section Surveillance
            with gr.Row():
                gr.Markdown("### 👁️ Surveillance des Exécutions")
            
            with gr.Row():
                with gr.Column(scale=1):
                    current_run_id = gr.Textbox(
                        label="ID d'exécution à surveiller",
                        placeholder="Sélectionnez ou collez un ID...",
                        interactive=True
                    )
                    
                    with gr.Row():
                        check_status_btn = gr.Button("📊 Vérifier Statut", variant="secondary")
                        get_logs_btn = gr.Button("📋 Récupérer Logs", variant="secondary")
                
                with gr.Column(scale=1):
                    run_status_display = gr.Textbox(
                        label="Statut de l'exécution",
                        interactive=False,
                        lines=8
                    )
            
            # Logs de l'exécution
            with gr.Row():
                run_logs_display = gr.Code(
                    label="Logs de l'exécution",
                    lines=10,
                    interactive=False
                )
            
            # Variables d'état cachées
            last_run_id = gr.State("")
            
            # Événements - Actions rapides (via Prefect Bridge pour exécution directe)
            health_check_btn.click(
                fn=prefect_bridge.health_check_sync,
                inputs=[],
                outputs=[quick_action_result]
            )
            
            maintenance_btn.click(
                fn=prefect_bridge.maintenance_sync,
                inputs=[],
                outputs=[quick_action_result]
            )
            
            smoke_test_btn.click(
                fn=prefect_bridge.smoke_tests_sync,
                inputs=[api_key_quick],
                outputs=[quick_action_result]
            )
            
            batch_process_btn.click(
                fn=lambda folder, api_key: prefect_bridge.batch_process_sync(
                    documents_folder=folder,
                    api_key=api_key,
                    file_extensions=['.pdf', '.docx', '.txt']
                ),
                inputs=[batch_folder_quick, api_key_quick],
                outputs=[quick_action_result]
            )
            
            # Événements - Workflows avancés
            def update_workflow_params(workflow_type):
                """Mettre à jour les paramètres selon le type de workflow"""
                show_folder = workflow_type == "batch_processing"
                show_api = workflow_type in ["batch_processing", "smoke_tests"]
                
                return {
                    workflow_folder_path: gr.update(visible=show_folder),
                    workflow_api_key: gr.update(visible=show_api)
                }
            
            workflow_selector.change(
                fn=update_workflow_params,
                inputs=[workflow_selector],
                outputs=[workflow_folder_path, workflow_api_key]
            )
            
            def trigger_advanced_workflow(workflow_type, folder_path, api_key):
                """Déclencher un workflow avancé avec paramètres"""
                kwargs = {}
                if workflow_type == "batch_processing":
                    kwargs = {"folder_path": folder_path, "api_key": api_key}
                elif workflow_type in ["smoke_tests"]:
                    kwargs = {"api_key": api_key}
                
                return self.trigger_workflow_action(workflow_type, **kwargs)
            
            trigger_workflow_btn.click(
                fn=trigger_advanced_workflow,
                inputs=[workflow_selector, workflow_folder_path, workflow_api_key],
                outputs=[workflow_result, last_run_id]
            )
            
            # Événements - Surveillance
            refresh_status_btn.click(
                fn=self.refresh_status,
                outputs=[status_display, connection_info_display]
            )
            
            check_status_btn.click(
                fn=self.check_workflow_status,
                inputs=[current_run_id],
                outputs=[run_status_display]
            )
            
            get_logs_btn.click(
                fn=self.get_workflow_logs,
                inputs=[current_run_id],
                outputs=[run_logs_display]
            )
            
            # Auto-remplir l'ID du dernier run
            last_run_id.change(
                fn=lambda run_id: run_id,
                inputs=[last_run_id],
                outputs=[current_run_id]
            )
            
            # Bouton interface web Prefect
            def open_prefect_ui():
                return "🌐 Interface Prefect disponible sur: http://localhost:4200"
            
            open_prefect_ui_btn.click(
                fn=open_prefect_ui,
                outputs=[connection_info_display]
            )
            
            # Chargement initial du statut
            tab.select(
                fn=self.refresh_status,
                outputs=[status_display, connection_info_display]
            )
        
        return tab

# Instance globale pour utilisation
orchestration_interface = OrchestrationInterface()