import os
os.environ.update({
    'TF_CPP_MIN_LOG_LEVEL': '3',
    'CUDA_VISIBLE_DEVICES': '-1',
    'TF_ENABLE_ONEDNN_OPTS': '0',
    'TF_DISABLE_MKL': '1',
    'TF_FORCE_GPU_ALLOW_GROWTH': 'false'
})

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from typing import Optional, Tuple, List
import json
# from app.components.file_processor import FileProcessor
from components.file_processor import FileProcessor
from components.chat_engine import EnhancedChatEngine
from config import Config
from utils.validators import FileValidator, InputValidator
from utils.performance import PerformanceMonitor

class EnhancedDocumentChatBot:
    """Application principale améliorée avec tous les utilitaires"""
    
    def __init__(self):
        self.chat_engine = EnhancedChatEngine()
        self.global_monitor = PerformanceMonitor()
        self.current_document = None
        self.document_processed = False
        self.system_status = {}
    
    def process_document_enhanced(self, 
                                api_key: str, 
                                file_obj, 
                                chunk_size: int, 
                                k_documents: int,
                                template_type: str = 'auto') -> Tuple[str, str, str, List[dict]]:
        """
        Version améliorée du traitement de documents
        Returns: (status_message, document_info, performance_info, empty_chat_history)
        """
        @self.global_monitor.measure_performance("full_document_processing")
        def _process():
            try:
                # Validation du fichier
                file_valid, file_error = FileValidator.validate_file(file_obj)
                if not file_valid:
                    return f"[ERREUR] {file_error}", "", "", []
                
                # Validation de la clé API
                api_valid, api_error = InputValidator.validate_api_key(api_key.strip(), 'mistral')
                if not api_valid:
                    return f"[ERREUR] {api_error}", "", "", []
                
                # Configuration du LLM
                self.chat_engine.setup_llm(api_key.strip())
                
                # Traitement du fichier
                text_content, filename = FileProcessor.process_uploaded_file(file_obj)
                
                # Réinitialisation complète pour nouveau document
                self.chat_engine.vectorstore_manager.reset_collection()
                
                # Réinitialisation de la mémoire de conversation
                self.chat_engine.memory.clear_history()
                
                # Ajout des documents avec métadonnées enrichies
                chunk_overlap = max(50, chunk_size // 5)
                num_chunks, doc_details = self.chat_engine.vectorstore_manager.add_documents_enhanced(
                    text_content, filename, chunk_size, chunk_overlap
                )
                
                # Configuration de la chaîne avec template intelligent
                self.chat_engine.setup_chain_with_template(k_documents, template_type)
                
                # Mise à jour de l'état
                self.current_document = filename
                self.document_processed = True
                self.system_status = self.chat_engine.get_system_status()
                
                # Messages de statut
                status = f"[OK] Document traité avec succès!"

                doc_info = f"""
### Informations du document
- **Fichier**: {filename}
- **Type détecté**: {doc_details['document_type']}
- **Chunks créés**: {num_chunks}
- **Taille moyenne des chunks**: {doc_details['average_chunk_size']:.0f} caractères
- **Structure préservée**: {doc_details['structure_preserved']} sections
- **Mots-clés extraits**: {'Oui' if doc_details['keywords_extracted'] else 'Non'}

### Configuration
- **Template utilisé**: {self.chat_engine.current_template_type}
- **Documents récupérés**: {k_documents}
- **Modèle**: Mistral AI (mistral-tiny)
                """.strip()
                
                # Informations de performance
                perf_summary = self.global_monitor.get_metrics_summary()
                system_info = self.global_monitor.get_system_info()
                
                perf_info = f"""
### Performance
- **Temps de traitement**: {perf_summary.get('avg_duration', 0):.2f}s
- **Utilisation mémoire**: {system_info['memory_percent']:.1f}%
- **CPU**: {system_info['cpu_percent']:.1f}%
- **Taux de succès**: {perf_summary.get('success_rate', 100):.1f}%
                """.strip()
                
                # Historique de chat vide pour nouveau document
                empty_chat_history = []
                
                return status, doc_info, perf_info, empty_chat_history
                
            except Exception as e:
                error_msg = f"[ERREUR] {str(e)}"
                return error_msg, "", "", []
        
        return _process()
    
    def chat_enhanced(self, 
                     message: str, 
                     history: List[dict]) -> Tuple[str, List[dict], str]:
        """
        Version améliorée du chat avec métadonnées (format messages)
        Returns: ("", updated_history, metadata_info)
        """
        if not self.document_processed:
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": "Veuillez d'abord traiter un document dans l'onglet Configuration."})
            return "", history, ""
        
        if not message.strip():
            return "", history, ""
        
        # Ajouter le message de l'utilisateur
        history.append({"role": "user", "content": message})
        
        # Traitement amélioré de la question
        answer, sources, metadata = self.chat_engine.process_question_enhanced(message)
        
        # Formatage de la réponse avec sources détaillées
        if sources:
            source_details = []
            for i, source in enumerate(sources):
                if i < len(metadata.get('source_details', [])):
                    detail = metadata['source_details'][i]
                    keywords_str = ', '.join(detail['keywords'][:3]) if detail['keywords'] else 'N/A'
                    source_details.append(f"[{source}] Mots-clés: {keywords_str}")
                else:
                    source_details.append(f"[{source}]")
            
            formatted_answer = f"{answer}\n\n**Sources consultées:**\n" + "\n".join(source_details)
        else:
            formatted_answer = answer
        
        # Informations de métadonnées pour affichage
        metadata_info = f"""
**Template**: {metadata.get('template_used', 'N/A')} | **Sources**: {metadata.get('sources_count', 0)} | **Performance**: {metadata.get('performance', {}).get('avg_duration', 0):.2f}s
        """.strip()
        
        # Ajouter la réponse de l'assistant
        history.append({"role": "assistant", "content": formatted_answer})
        
        return "", history, metadata_info
    
    def get_detailed_status(self) -> str:
        """Retourne un statut détaillé du système"""
        if not self.document_processed:
            return "**Statut**: Aucun document traité"

        status = self.chat_engine.get_system_status()

        status_text = f"""
### Système opérationnel

**Configuration actuelle:**
- Template: {status['current_template']}
- Conversations: {status['conversation_length']} échanges
- Performance moyenne: {status['performance_summary'].get('avg_duration', 0):.2f}s

**Ressources système:**
- Mémoire: {status['system_info']['memory_percent']:.1f}%
- CPU: {status['system_info']['cpu_percent']:.1f}%
- Espace disque: {status['system_info']['disk_usage_percent']:.1f}%

**Templates disponibles:** {', '.join(status['available_templates'])}
        """.strip()
        
        return status_text
    
    def export_session_data(self) -> str:
        """Exporte les données de la session"""
        if not self.document_processed:
            return "Aucune donnée à exporter"
        
        try:
            # Données à exporter
            session_data = {
                "document": self.current_document,
                "system_status": self.chat_engine.get_system_status(),
                "conversation_history": self.chat_engine.memory.conversation_history,
                "performance_metrics": self.global_monitor.get_metrics_summary()
            }
            
            # Sauvegarde dans un fichier
            filename = f"session_export_{self.current_document}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)
            
            return f"[OK] Session exportée: {filename}"

        except Exception as e:
            return f"[ERREUR] Erreur d'export: {str(e)}"

# Integration dans l'interface Gradio
def create_enhanced_interface():
    """Crée l'interface Gradio épurée avec charte gris foncé et orange"""
    
    app = EnhancedDocumentChatBot()
    
    # CSS avec charte graphique gris foncé et orange
    css = """
    :root {
        --primary-color: #ff6b35;  /* Orange */
        --secondary-color: #2d3748;  /* Gris foncé */
        --background-dark: #1a202c;  /* Gris très foncé */
        --background-light: #4a5568;  /* Gris moyen */
        --text-light: #e2e8f0;  /* Texte clair */
        --text-accent: #ff6b35;  /* Texte accent orange */
    }
    
    .gradio-container {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        max-width: 1000px;
        margin: 0 auto;
        background: var(--background-dark) !important;
        color: var(--text-light) !important;
    }
    
    .dark {
        background: var(--background-dark) !important;
    }
    
    /* En-têtes et titres */
    h1, h2, h3 {
        color: var(--text-accent) !important;
        font-weight: 600;
    }
    
    /* Onglets */
    .tab-nav button {
        background: var(--secondary-color) !important;
        color: var(--text-light) !important;
        border: 1px solid var(--background-light) !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .tab-nav button:hover {
        background: var(--background-light) !important;
        border-color: var(--primary-color) !important;
    }
    
    .tab-nav button.selected {
        background: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
    }
    
    /* Boutons */
    .primary {
        background: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
    }
    
    .primary:hover {
        background: #e55a2b !important;
        border-color: #e55a2b !important;
    }
    
    /* Zones de texte et inputs */
    input, textarea {
        background: var(--secondary-color) !important;
        border: 1px solid var(--background-light) !important;
        color: var(--text-light) !important;
    }
    
    input:focus, textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.3) !important;
    }
    
    /* Chat */
    .message.user {
        background: var(--secondary-color) !important;
        border-left: 3px solid var(--primary-color) !important;
    }
    
    .message.bot {
        background: var(--background-light) !important;
        border-left: 3px solid var(--text-light) !important;
    }
    
    /* Métadonnées */
    .metadata-info {
        background: var(--secondary-color) !important;
        border: 1px solid var(--background-light) !important;
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        color: var(--text-light) !important;
    }
    """
    
    # Thème personnalisé
    theme = gr.themes.Base(
        primary_hue="orange",
        secondary_hue="gray",
        neutral_hue="slate",
        text_size="sm",
        radius_size="md"
    ).set(
        body_background_fill="#1a202c",
        body_text_color="#e2e8f0",
        background_fill_primary="#2d3748",
        background_fill_secondary="#4a5568"
    )
    
    with gr.Blocks(css=css, title="DontREADME - Assistant Documentaire IA", theme=theme) as interface:
        
        # En-tête principal centré
        with gr.Row():
            with gr.Column():
                gr.HTML("""
                <div style="text-align: center; margin: 20px 0;">
                    <h1 style="font-family: 'Georgia', 'Times New Roman', serif; font-size: 3em; color: #ff6b35; margin-bottom: 10px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                        DontREADME
                    </h1>
                    <h3 style="color: #e2e8f0; font-weight: 300; margin-top: 0;">
                        Assistant Documentaire Intelligent
                    </h3>
                    <p style="color: #a0aec0; font-size: 1.1em; margin-top: 10px;">
                        Analysez vos documents PDF, DOCX et TXT avec l'IA Mistral
                    </p>
                </div>
                """)
        
        with gr.Tabs():
            # Onglet Configuration simplifié
            with gr.Tab("Document", id="document"):

                with gr.Row():
                    with gr.Column(scale=2):
                        api_key_input = gr.Textbox(
                            label="Clé API Mistral AI",
                            placeholder="Saisissez votre clé API Mistral...",
                            type="password",
                            info="Validation automatique de la clé"
                        )

                        file_upload = gr.File(
                            label="Fichier à analyser",
                            file_types=[".pdf", ".docx", ".txt"],
                            type="filepath"
                        )

                        with gr.Row():
                            chunk_size_slider = gr.Slider(
                                minimum=200,
                                maximum=2000,
                                value=Config.DEFAULT_CHUNK_SIZE,
                                step=100,
                                label="Taille des chunks",
                                info="Découpage intelligent automatique"
                            )

                            k_documents_slider = gr.Slider(
                                minimum=1,
                                maximum=10,
                                value=Config.DEFAULT_K_DOCUMENTS,
                                step=1,
                                label="Documents récupérés"
                            )

                        template_dropdown = gr.Dropdown(
                            choices=['auto', 'general', 'academic', 'technical', 'legal'],
                            value='auto',
                            label="Type de template",
                            info="Auto = détection automatique"
                        )

                        process_btn = gr.Button("Traiter le document", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        status_output = gr.Textbox(
                            label="Statut",
                            interactive=False,
                            lines=2
                        )

                        doc_info_output = gr.Markdown(
                            label="Informations détaillées"
                        )

                        perf_info_output = gr.Markdown(
                            label="Performance",
                            elem_classes=["performance-info"]
                        )

            # Onglet Chat Amélioré
            with gr.Tab("Chat Intelligent", id="chat"):
                
                chatbot = gr.Chatbot(
                    label="Conversation avec intelligence augmentée",
                    height=500
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        label="Votre question",
                        placeholder="Question intelligente avec validation automatique...",
                        scale=4
                    )
                    
                    with gr.Column(scale=1):
                        send_btn = gr.Button("Envoyer", variant="primary")
                        clear_btn = gr.Button("Effacer", variant="secondary")

                # Informations de métadonnées en temps réel
                metadata_display = gr.Textbox(
                    label="Métadonnées de la réponse",
                    interactive=False,
                    lines=1,
                    elem_classes=["performance-info"]
                )
            
        
        # Événements
        process_btn.click(
            fn=app.process_document_enhanced,
            inputs=[api_key_input, file_upload, chunk_size_slider, k_documents_slider, template_dropdown],
            outputs=[status_output, doc_info_output, perf_info_output, chatbot]
        )
        
        send_btn.click(
            fn=app.chat_enhanced,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot, metadata_display]
        )
        
        msg_input.submit(
            fn=app.chat_enhanced,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot, metadata_display]
        )
        
        clear_btn.click(
            fn=lambda: ([], ""),
            outputs=[chatbot, metadata_display]
        )
        
    
    return interface

if __name__ == "__main__":
    from datetime import datetime
    os.makedirs("./data/uploads", exist_ok=True)
    os.makedirs("./data/vectorstore", exist_ok=True)
    
    interface = create_enhanced_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        debug=True
    )