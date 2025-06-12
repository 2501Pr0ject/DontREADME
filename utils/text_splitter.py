import re
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class SmartTextSplitter:
    """
    Découpeur de texte intelligent avec optimisations pour différents types de documents
    """
    
    def __init__(self):
        self.separators = {
            'default': ["\n\n", "\n", ". ", "! ", "? ", " ", ""],
            'academic': ["\n\n", "\n", ". ", "; ", ", ", " ", ""],
            'technical': ["\n\n", "\n", ".\n", ". ", ":\n", ": ", " ", ""],
            'legal': ["\n\n", "\n", ". ", "; ", " - ", " ", ""]
        }
    
    def detect_document_type(self, text: str) -> str:
        """
        Détecte le type de document pour optimiser le découpage
        """
        text_lower = text.lower()
        
        # Mots-clés pour différents types
        academic_keywords = ['abstract', 'résumé', 'introduction', 'conclusion', 'références', 'bibliographie']
        technical_keywords = ['api', 'fonction', 'class', 'def ', 'import', 'documentation', 'manuel']
        legal_keywords = ['article', 'clause', 'alinéa', 'considérant', 'attendu', 'arrêté']
        
        # Compter les occurrences
        academic_score = sum(1 for keyword in academic_keywords if keyword in text_lower)
        technical_score = sum(1 for keyword in technical_keywords if keyword in text_lower)
        legal_score = sum(1 for keyword in legal_keywords if keyword in text_lower)
        
        # Déterminer le type
        scores = {
            'academic': academic_score,
            'technical': technical_score,
            'legal': legal_score
        }
        
        max_score = max(scores.values())
        if max_score >= 2:  # Seuil minimum
            return max(scores, key=scores.get)
        
        return 'default'
    
    def create_splitter(self, 
                       chunk_size: int = 1000,
                       chunk_overlap: int = 200,
                       document_type: str = 'auto') -> RecursiveCharacterTextSplitter:
        """
        Crée un text splitter optimisé selon le type de document
        """
        if document_type == 'auto':
            # Le type sera détecté lors du split_text
            separators = self.separators['default']
        else:
            separators = self.separators.get(document_type, self.separators['default'])
        
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=separators,
            keep_separator=True
        )
    
    def smart_split(self, 
                   text: str, 
                   chunk_size: int = 1000,
                   chunk_overlap: int = 200,
                   preserve_structure: bool = True) -> List[str]:
        """
        Découpage intelligent qui préserve la structure du document
        """
        # Détection automatique du type
        doc_type = self.detect_document_type(text)
        
        # Préprocessing pour préserver la structure
        if preserve_structure:
            text = self._preprocess_text(text)
        
        # Création du splitter adapté
        splitter = self.create_splitter(chunk_size, chunk_overlap, doc_type)
        
        # Découpage
        chunks = splitter.split_text(text)
        
        # Post-processing pour nettoyer les chunks
        cleaned_chunks = [self._clean_chunk(chunk) for chunk in chunks]
        
        return [chunk for chunk in cleaned_chunks if chunk.strip()]
    
    def split_documents_with_metadata(self,
                                    text: str,
                                    filename: str,
                                    chunk_size: int = 1000,
                                    chunk_overlap: int = 200) -> List[Document]:
        """
        Découpe le texte et crée des documents avec métadonnées enrichies
        """
        chunks = self.smart_split(text, chunk_size, chunk_overlap)
        doc_type = self.detect_document_type(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            # Métadonnées enrichies
            metadata = {
                "filename": filename,
                "chunk_id": i,
                "total_chunks": len(chunks),
                "document_type": doc_type,
                "chunk_size": len(chunk),
                "chunk_position": "start" if i == 0 else ("end" if i == len(chunks) - 1 else "middle"),
                "contains_structure": self._has_structure_markers(chunk)
            }
            
            # Ajout de mots-clés pour ce chunk
            keywords = self._extract_keywords(chunk)
            if keywords:
                metadata["keywords"] = keywords
            
            documents.append(Document(page_content=chunk, metadata=metadata))
        
        return documents
    
    def _preprocess_text(self, text: str) -> str:
        """Préprocessing pour améliorer le découpage"""
        # Normaliser les espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Préserver les sauts de ligne importants
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Améliorer la détection des phrases
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\2', text)
        
        return text.strip()
    
    def _clean_chunk(self, chunk: str) -> str:
        """Nettoie un chunk après découpage"""
        # Supprimer les espaces en début/fin
        chunk = chunk.strip()
        
        # Supprimer les lignes vides multiples
        chunk = re.sub(r'\n\s*\n\s*\n', '\n\n', chunk)
        
        # S'assurer qu'on ne commence pas par un séparateur
        chunk = re.sub(r'^[.!?;:,\s]+', '', chunk)
        
        return chunk
    
    def _has_structure_markers(self, chunk: str) -> bool:
        """Détecte si le chunk contient des marqueurs structurels"""
        structure_patterns = [
            r'^\d+\.',  # Numérotation
            r'^[A-Z][.]',  # Sections A., B., etc.
            r'^-\s',  # Listes à puces
            r'^\*\s',  # Listes étoiles
            r'^\w+:\s',  # Titre: contenu
        ]
        
        return any(re.search(pattern, chunk, re.MULTILINE) for pattern in structure_patterns)
    
    def _extract_keywords(self, chunk: str, max_keywords: int = 5) -> List[str]:
        """Extrait les mots-clés principaux d'un chunk"""
        # Mots vides français et anglais
        stop_words = {
            'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'à', 'dans', 'sur', 'pour', 'par',
            'avec', 'sans', 'sous', 'que', 'qui', 'quoi', 'dont', 'où', 'ce', 'cette', 'ces', 'est', 'sont',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are'
        }
        
        # Extraction des mots
        words = re.findall(r'\b[a-zA-ZàâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]{3,}\b', chunk.lower())
        
        # Filtrage et comptage
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Retourner les mots les plus fréquents
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_keywords]]
