from typing import Optional, Tuple, List, Dict
from langchain_mistralai import ChatMistralAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Ajouter les chemins pour les imports
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # app/
root_dir = os.path.dirname(parent_dir)     # DontREADME/
sys.path.insert(0, parent_dir)  # Pour components
sys.path.insert(0, root_dir)    # Pour utils

from components.vectorstore import EnhancedVectorStoreManager
from components.memory import ConversationMemory
from utils.prompt_templates import PromptTemplateManager
from utils.validators import InputValidator
from utils.performance import PerformanceMonitor

class EnhancedChatEngine:
    """Moteur de conversation amélioré avec utilitaires avancés"""
    
    def __init__(self):
        self.llm = None
        self.vectorstore_manager = EnhancedVectorStoreManager()
        self.memory = ConversationMemory()
        self.prompt_manager = PromptTemplateManager()
        self.performance_monitor = PerformanceMonitor()
        self.chain = None
        self.current_template_type = 'general'
    
    def setup_llm(self, api_key: str, model: str = "mistral-tiny"):
        """Configuration du LLM avec validation"""
        # Validation de la clé API
        valid_key, key_error = InputValidator.validate_api_key(api_key, 'mistral')
        if not valid_key:
            raise ValueError(f"Clé API invalide: {key_error}")
        
        @self.performance_monitor.measure_performance("setup_llm")
        def _setup():
            self.llm = ChatMistralAI(
                mistral_api_key=api_key,
                model=model,
                temperature=0.1,
                max_tokens=1000
            )
        
        _setup()
    
    def setup_chain_with_template(self, 
                                 k_documents: int = 3, 
                                 template_type: str = 'auto'):
        """Configuration de la chaîne avec template intelligent"""
        if not self.llm:
            raise ValueError("LLM non configuré")
        
        if not self.vectorstore_manager.vectorstore:
            raise ValueError("VectorStore non initialisé")
        
        # Validation des paramètres
        valid_k, k_error = InputValidator.validate_k_documents(k_documents)
        if not valid_k:
            raise ValueError(f"Paramètre k invalide: {k_error}")
        
        @self.performance_monitor.measure_performance("setup_chain")
        def _setup():
            # Détection automatique du type de template si nécessaire
            if template_type == 'auto':
                # Récupérer le type de document depuis les métadonnées
                sample_docs = self.vectorstore_manager.search_with_metadata("test", k=1)
                if sample_docs:
                    document_type = sample_docs[0]['metadata'].get('document_type', 'general')
                    template_type_final = document_type
                else:
                    template_type_final = 'general'
            else:
                template_type_final = template_type
            
            # Sélection du template optimisé
            prompt_template = self.prompt_manager.get_optimized_template(
                document_type=template_type_final,
                query_type='general'
            )
            
            self.current_template_type = template_type_final
            
            # Configuration de la mémoire
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            
            # Création de la chaîne
            self.chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vectorstore_manager.get_retriever(k=k_documents),
                memory=memory,
                return_source_documents=True,
                combine_docs_chain_kwargs={"prompt": prompt_template}
            )
        
        _setup()
    
    def process_question_enhanced(self, question: str) -> Tuple[str, List[str], Dict]:
        """
        Traitement avancé des questions avec métadonnées enrichies
        Returns: (answer, sources, metadata)
        """
        # Validation et nettoyage de la question
        valid_question, question_error = InputValidator.validate_question(question)
        if not valid_question:
            return f"Question invalide: {question_error}", [], {}
        
        question = InputValidator.sanitize_input(question)
        
        @self.performance_monitor.measure_performance("process_question")
        def _process():
            if not self.chain:
                return "Erreur: Système non configuré", [], {}
            
            try:
                # Exécution de la chaîne
                result = self.chain({"question": question})
                
                answer = result.get("answer", "Pas de réponse générée")
                
                # Extraction enrichie des sources
                sources = []
                source_metadata = []
                
                if "source_documents" in result:
                    for doc in result["source_documents"]:
                        filename = doc.metadata.get("filename", "Document")
                        chunk_id = doc.metadata.get("chunk_id", 0)
                        chunk_position = doc.metadata.get("chunk_position", "unknown")
                        keywords = doc.metadata.get("keywords", [])
                        
                        source_label = f"{filename} (section {chunk_id + 1})"
                        sources.append(source_label)
                        
                        source_metadata.append({
                            "filename": filename,
                            "chunk_id": chunk_id,
                            "position": chunk_position,
                            "keywords": keywords,
                            "content_preview": doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                        })
                
                # Métadonnées de la réponse
                response_metadata = {
                    "template_used": self.current_template_type,
                    "sources_count": len(sources),
                    "source_details": source_metadata,
                    "performance": self.performance_monitor.get_metrics_summary("process_question", last_n_minutes=1)
                }
                
                # Sauvegarde dans l'historique
                self.memory.add_exchange(question, answer, sources)
                
                return answer, sources, response_metadata
                
            except Exception as e:
                error_msg = f"Erreur lors du traitement: {str(e)}"
                return error_msg, [], {"error": str(e)}
        
        return _process()
    
    def get_system_status(self) -> Dict:
        """Retourne le statut détaillé du système"""
        return {
            "llm_configured": self.llm is not None,
            "vectorstore_ready": self.vectorstore_manager.vectorstore is not None,
            "chain_ready": self.chain is not None,
            "current_template": self.current_template_type,
            "conversation_length": len(self.memory.conversation_history),
            "performance_summary": self.performance_monitor.get_metrics_summary(),
            "system_info": self.performance_monitor.get_system_info(),
            "available_templates": self.prompt_manager.get_available_templates()
        }
    
    def switch_template(self, new_template_type: str) -> bool:
        """Change le template de prompt en cours d'exécution"""
        try:
            available_templates = self.prompt_manager.get_available_templates()
            if new_template_type not in available_templates:
                return False
            
            # Reconfigurer la chaîne avec le nouveau template
            if self.chain:
                k_current = getattr(self.chain.retriever, 'search_kwargs', {}).get('k', 3)
                self.setup_chain_with_template(k_current, new_template_type)
                return True
            
            return False
        except Exception:
            return False