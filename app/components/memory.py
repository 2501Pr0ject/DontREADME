from typing import List, Dict, Any
from datetime import datetime

class ConversationMemory:
    """Gestion de l'historique des conversations"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
    
    def add_exchange(self, question: str, answer: str, sources: List[str] = None):
        """Ajoute un échange question-réponse à l'historique"""
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "sources": sources or []
        }
        self.conversation_history.append(exchange)
    
    def get_recent_history(self, n_exchanges: int = 3) -> str:
        """
        Retourne l'historique récent formaté pour le contexte LLM
        """
        if not self.conversation_history:
            return ""
        
        recent = self.conversation_history[-n_exchanges:]
        history_text = "Historique de la conversation:\n"
        
        for exchange in recent:
            history_text += f"Q: {exchange['question']}\n"
            history_text += f"R: {exchange['answer']}\n\n"
        
        return history_text
    
    def get_formatted_history(self) -> List[List[str]]:
        """Retourne l'historique formaté pour l'affichage Gradio"""
        formatted = []
        for exchange in self.conversation_history:
            formatted.append([exchange["question"], exchange["answer"]])
        return formatted
    
    def clear_history(self):
        """Efface l'historique"""
        self.conversation_history = []