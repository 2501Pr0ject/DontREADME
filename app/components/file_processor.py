import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import PyPDF2
from docx import Document

class FileProcessor:
    """Traitement des fichiers uploadés"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extrait le texte d'un fichier PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extrait le texte d'un fichier DOCX"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extrait le texte d'un fichier TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Essayer avec d'autres encodages
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read().strip()
                except UnicodeDecodeError:
                    continue
            raise Exception("Impossible de décoder le fichier texte")
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du TXT: {str(e)}")
    
    @classmethod
    def process_uploaded_file(cls, file_obj) -> Tuple[str, str]:
        """
        Traite un fichier uploadé et retourne le texte extrait
        Returns: (text_content, filename)
        """
        if file_obj is None:
            raise ValueError("Aucun fichier fourni")
        
        # Debug: voir ce qu'on reçoit
        print(f"Type de file_obj: {type(file_obj)}")
        
        # Gérer différents types d'input de Gradio
        if isinstance(file_obj, str):
            # file_obj est un chemin de fichier
            file_path = file_obj
            filename = Path(file_path).name
            file_extension = Path(file_path).suffix.lower()
            
        elif hasattr(file_obj, 'name'):
            # file_obj est un objet fichier avec .name
            filename = Path(file_obj.name).name
            file_extension = Path(file_obj.name).suffix.lower()
            
            # Sauvegarder temporairement le fichier
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                if hasattr(file_obj, 'read'):
                    tmp_file.write(file_obj.read())
                else:
                    tmp_file.write(file_obj)
                file_path = tmp_file.name
                
        else:
            # file_obj est probablement des bytes ou autre
            # On ne peut pas deviner l'extension, on essaie PDF par défaut
            filename = "document_uploade"
            file_extension = ".pdf"  # Défaut, à ajuster selon tes besoins
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                if isinstance(file_obj, bytes):
                    tmp_file.write(file_obj)
                elif hasattr(file_obj, 'read'):
                    tmp_file.write(file_obj.read())
                else:
                    tmp_file.write(file_obj)
                file_path = tmp_file.name
        
        try:
            # Extraire le texte selon l'extension
            if file_extension == '.pdf':
                text = cls.extract_text_from_pdf(file_path)
            elif file_extension == '.docx':
                text = cls.extract_text_from_docx(file_path)
            elif file_extension == '.txt':
                text = cls.extract_text_from_txt(file_path)
            else:
                raise ValueError(f"Format de fichier non supporté: {file_extension}")
            
            if not text.strip():
                raise ValueError("Le fichier ne contient pas de texte extractible")
            
            return text, filename
            
        finally:
            # Nettoyer le fichier temporaire (seulement si on l'a créé)
            if not isinstance(file_obj, str) and os.path.exists(file_path):
                os.unlink(file_path)