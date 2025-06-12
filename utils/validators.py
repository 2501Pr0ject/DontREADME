import os
import magic
from pathlib import Path
from typing import Tuple, Optional, List
import re

class FileValidator:
    """
    Validateur pour les fichiers uploadés
    """
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.doc'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_FILE_SIZE = 100  # 100 bytes
    
    @classmethod
    def validate_file(cls, file_obj) -> Tuple[bool, Optional[str]]:
        """
        Valide un fichier uploadé
        Returns: (is_valid, error_message)
        """
        if file_obj is None:
            return False, "Aucun fichier fourni"
        
        # Vérification de l'extension
        if hasattr(file_obj, 'name'):
            file_extension = Path(file_obj.name).suffix.lower()
            if file_extension not in cls.SUPPORTED_EXTENSIONS:
                return False, f"Format non supporté. Formats acceptés: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
        
        # Vérification de la taille
        try:
            if hasattr(file_obj, 'size'):
                file_size = file_obj.size
            else:
                # Fallback pour les objets sans attribut size
                content = file_obj.read() if hasattr(file_obj, 'read') else file_obj
                file_size = len(content)
                # Reset du pointeur si possible
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
            
            if file_size > cls.MAX_FILE_SIZE:
                return False, f"Fichier trop volumineux (max {cls.MAX_FILE_SIZE // (1024*1024)}MB)"
            
            if file_size < cls.MIN_FILE_SIZE:
                return False, "Fichier trop petit ou vide"
                
        except Exception as e:
            return False, f"Erreur lors de la vérification de la taille: {str(e)}"
        
        return True, None
    
    @classmethod
    def detect_file_type(cls, file_path: str) -> str:
        """
        Détecte le type MIME d'un fichier
        """
        try:
            mime_type = magic.from_file(file_path, mime=True)
            return mime_type
        except:
            # Fallback basé sur l'extension
            extension = Path(file_path).suffix.lower()
            mime_mapping = {
                '.pdf': 'application/pdf',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.doc': 'application/msword',
                '.txt': 'text/plain'
            }
            return mime_mapping.get(extension, 'unknown')

class InputValidator:
    """
    Validateur pour les entrées utilisateur
    """
    
    @staticmethod
    def validate_api_key(api_key: str, provider: str = 'mistral') -> Tuple[bool, Optional[str]]:
        """
        Valide une clé API
        """
        if not api_key or not api_key.strip():
            return False, "Clé API manquante"
        
        api_key = api_key.strip()
        
        if provider.lower() == 'mistral':
            # Format attendu pour Mistral: commence généralement par des caractères spécifiques
            if len(api_key) < 20:
                return False, "Clé API Mistral trop courte"
            
            # Vérification basique du format
            if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
                return False, "Format de clé API invalide"
        
        elif provider.lower() == 'openai':
            # Format OpenAI: sk-...
            if not api_key.startswith('sk-'):
                return False, "Clé API OpenAI doit commencer par 'sk-'"
            
            if len(api_key) < 45:
                return False, "Clé API OpenAI trop courte"
        
        return True, None
    
    @staticmethod
    def validate_chunk_size(chunk_size: int) -> Tuple[bool, Optional[str]]:
        """
        Valide la taille des chunks
        """
        if not isinstance(chunk_size, int):
            return False, "La taille des chunks doit être un nombre entier"
        
        if chunk_size < 100:
            return False, "Taille des chunks trop petite (minimum 100)"
        
        if chunk_size > 4000:
            return False, "Taille des chunks trop grande (maximum 4000)"
        
        return True, None
    
    @staticmethod
    def validate_k_documents(k: int) -> Tuple[bool, Optional[str]]:
        """
        Valide le nombre de documents à récupérer
        """
        if not isinstance(k, int):
            return False, "Le nombre de documents doit être un entier"
        
        if k < 1:
            return False, "Nombre de documents minimum: 1"
        
        if k > 20:
            return False, "Nombre de documents maximum: 20"
        
        return True, None
    
    @staticmethod
    def validate_question(question: str) -> Tuple[bool, Optional[str]]:
        """
        Valide une question utilisateur
        """
        if not question or not question.strip():
            return False, "Question vide"
        
        question = question.strip()
        
        if len(question) < 3:
            return False, "Question trop courte (minimum 3 caractères)"
        
        if len(question) > 1000:
            return False, "Question trop longue (maximum 1000 caractères)"
        
        # Vérification de caractères suspects
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'eval\(',
            r'exec\('
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                return False, "Question contient des éléments suspects"
        
        return True, None
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Nettoie et sécurise une entrée texte
        """
        if not isinstance(text, str):
            return ""
        
        # Supprime les caractères de contrôle
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalise les espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Supprime les espaces en début/fin
        text = text.strip()
        
        return text