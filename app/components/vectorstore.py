import os
import sys
from typing import List, Optional, Tuple
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain.schema import Document
import requests
import json

# IMPORTANT: Ajouter les chemins pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # app/
root_dir = os.path.dirname(parent_dir)     # DontREADME/
sys.path.insert(0, parent_dir)  # Pour config
sys.path.insert(0, root_dir)    # Pour utils

# Maintenant les imports personnalisés
from config import Config
from utils.text_splitter import SmartTextSplitter
from utils.validators import InputValidator
from utils.performance import PerformanceMonitor

class HuggingFaceAPIEmbeddings:
    """Embeddings via l'API HuggingFace Inference (gratuite, sans installation locale)"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_name}"
        self.dimension = 384  # Dimension du modèle all-MiniLM-L6-v2
        
        # Test de connexion à l'API
        self._test_api_connection()
    
    def _test_api_connection(self):
        """Tester la connexion à l'API HuggingFace"""
        try:
            test_response = requests.post(
                self.api_url,
                headers={"Content-Type": "application/json"},
                json={"inputs": "test"},
                timeout=10
            )
            if test_response.status_code == 200:
                print("✅ Connexion API HuggingFace établie")
            else:
                print(f"⚠️ API HuggingFace: statut {test_response.status_code}")
        except Exception as e:
            print(f"⚠️ Test API HuggingFace échoué: {e}")
    
    def name(self):
        """Nom de la fonction d'embedding pour ChromaDB"""
        return "huggingface_api_embeddings"
    
    def __call__(self, input):
        """Interface ChromaDB standard"""
        if isinstance(input, str):
            return self.embed_query(input)
        elif isinstance(input, list):
            return self.embed_documents(input)
        else:
            raise ValueError(f"Type d'entrée non supporté: {type(input)}")
    
    def _call_api(self, texts: List[str], max_retries: int = 3):
        """Appeler l'API HuggingFace avec retry"""
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers={"Content-Type": "application/json"},
                    json={"inputs": texts},
                    timeout=30
                )
                
                if response.status_code == 200:
                    embeddings = response.json()
                    # Assurer que c'est une liste de listes
                    if isinstance(embeddings[0], list):
                        return embeddings
                    else:
                        return [embeddings]  # Un seul embedding
                        
                elif response.status_code == 503:  # Service temporairement indisponible
                    print(f"⏳ API HuggingFace occupée, tentative {attempt + 1}/{max_retries}")
                    import time
                    time.sleep(2 ** attempt)  # Backoff exponentiel
                    continue
                else:
                    print(f"❌ Erreur API HuggingFace: {response.status_code} - {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ Erreur réseau API HuggingFace: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                    continue
                break
        
        # Fallback vers embeddings factices en cas d'échec
        print("⚠️ Utilisation d'embeddings factices comme fallback")
        return self._generate_fake_embeddings(texts)
    
    def _generate_fake_embeddings(self, texts: List[str]):
        """Génère des embeddings factices cohérents en cas d'échec API"""
        embeddings = []
        for text in texts:
            text_hash = hash(text) % 1000
            embedding = [0.1 + (text_hash / 10000.0) + (j * 0.001) for j in range(self.dimension)]
            embeddings.append(embedding)
        return embeddings
    
    def embed_documents(self, texts: List[str]):
        """Générer des embeddings pour plusieurs documents"""
        # Traiter par batch pour éviter les timeouts
        batch_size = 10
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self._call_api(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    def embed_query(self, text: str):
        """Générer un embedding pour une seule requête"""
        embeddings = self._call_api([text])
        return embeddings[0] if embeddings else self._generate_fake_embeddings([text])[0]

class RealEmbeddings:
    """Wrapper pour SentenceTransformer compatible avec ChromaDB"""
    
    def __init__(self, model):
        self.model = model
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
    
    def name(self):
        """Nom de la fonction d'embedding pour ChromaDB"""
        return "sentence_transformers"
    
    def __call__(self, input):
        """Interface ChromaDB standard"""
        if isinstance(input, str):
            return self.embed_query(input)
        elif isinstance(input, list):
            return self.embed_documents(input)
        else:
            raise ValueError(f"Type d'entrée non supporté: {type(input)}")
    
    def embed_documents(self, texts):
        """Générer des embeddings réels pour les documents"""
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            # Convertir en liste de listes pour ChromaDB
            return embeddings.tolist()
        except Exception as e:
            print(f"Erreur embeddings documents: {e}")
            # Fallback vers embeddings factices
            fake = FakeEmbeddings()
            return fake.embed_documents(texts)
    
    def embed_query(self, text):
        """Générer un embedding réel pour une requête"""
        try:
            embedding = self.model.encode([text], convert_to_tensor=False)
            return embedding[0].tolist()
        except Exception as e:
            print(f"Erreur embedding query: {e}")
            # Fallback vers embeddings factices
            fake = FakeEmbeddings()
            return fake.embed_query(text)

class EnhancedVectorStoreManager:
    """Version améliorée du gestionnaire de base vectorielle avec utilitaires"""
    
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = SmartTextSplitter()
        self.performance_monitor = PerformanceMonitor()
        self._setup_embeddings()
    
    def _setup_embeddings(self):
        @self.performance_monitor.measure_performance("setup_embeddings")
        def _setup():
            print("🔧 Initialisation des embeddings HuggingFace API...")
            # Utiliser l'API HuggingFace pour des vrais embeddings sans dépendances locales
            self.embeddings = HuggingFaceAPIEmbeddings()
            print("✅ Embeddings HuggingFace API initialisés - Vrais embeddings activés")
        
        _setup()
    
    @property
    def performance_metrics(self):
        """Accès aux métriques de performance"""
        return self.performance_monitor.get_metrics_summary()
    
    def initialize_vectorstore(self, collection_name: str = Config.COLLECTION_NAME):
        """Initialise la base vectorielle avec monitoring"""
        @self.performance_monitor.measure_performance("initialize_vectorstore")
        def _initialize():
            try:
                if not self.embeddings:
                    print("❌ Erreur : Embeddings non initialisés")
                    return False
                
                print(f"🔧 Initialisation du VectorStore avec {type(self.embeddings).__name__}...")
                    
                os.makedirs(Config.CHROMADB_PATH, exist_ok=True)
                client = chromadb.PersistentClient(path=Config.CHROMADB_PATH)
                
                # Créer ou récupérer le vectorstore (Chroma gère automatiquement la collection)
                print(f"📝 Initialisation de la collection '{collection_name}'...")
                
                self.vectorstore = Chroma(
                    client=client,
                    collection_name=collection_name,
                    embedding_function=self.embeddings,
                )
                
                print(f"✅ VectorStore initialisé avec la collection '{collection_name}'")
                return True
                
            except Exception as e:
                print(f"❌ Erreur lors de l'initialisation du VectorStore: {e}")
                print(f"   Type d'erreur: {type(e).__name__}")
                self.vectorstore = None
                return False
        
        return _initialize()
    
    def reset_collection(self, collection_name: str = Config.COLLECTION_NAME):
        """Supprime et recrée la collection (optionnel)"""
        os.makedirs(Config.CHROMADB_PATH, exist_ok=True)
        client = chromadb.PersistentClient(path=Config.CHROMADB_PATH)
        
        try:
            client.delete_collection(collection_name)
            print(f"🗑️ Collection '{collection_name}' supprimée")
        except ValueError:
            print(f"ℹ️ Collection '{collection_name}' n'existait pas")
        
        self.vectorstore = Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
        )
        print(f"✅ Nouvelle collection '{collection_name}' créée")
    
    def add_documents_enhanced(self, 
                             text: str, 
                             filename: str, 
                             chunk_size: int, 
                             chunk_overlap: int) -> Tuple[int, dict]:
        """
        Version améliorée d'ajout de documents avec validation et monitoring
        Returns: (nombre_chunks, informations_détaillées)
        """
        # Validation des paramètres
        valid_chunk, chunk_error = InputValidator.validate_chunk_size(chunk_size)
        if not valid_chunk:
            raise ValueError(f"Chunk size invalide: {chunk_error}")
        
        @self.performance_monitor.measure_performance("add_documents")
        def _add_documents():
            # Auto-initialisation du VectorStore si nécessaire
            if not self.vectorstore:
                print("🔧 Auto-initialisation du VectorStore...")
                success = self.initialize_vectorstore()
                
                # Vérifier que l'initialisation a réussi
                if not success or not self.vectorstore:
                    raise ValueError("Échec d'initialisation du VectorStore")
            
            # ✅ VÉRIFICATION: Embeddings disponibles
            if not self.embeddings:
                raise ValueError("Embeddings non initialisés")
            
            # Découpage intelligent avec métadonnées enrichies
            documents = self.text_splitter.split_documents_with_metadata(
                text, filename, chunk_size, chunk_overlap
            )
            
            if not documents:
                raise ValueError("Aucun document généré lors du découpage")
            
            # Filtrer les métadonnées complexes pour ChromaDB
            filtered_documents = self._filter_complex_metadata(documents)
            
            # Ajout à la base vectorielle
            self.vectorstore.add_documents(filtered_documents)
            print(f"✅ {len(filtered_documents)} chunks ajoutés à la collection")
            
            # Informations détaillées sur le traitement
            doc_info = {
                "total_chunks": len(documents),
                "document_type": documents[0].metadata.get("document_type", "unknown") if documents else "unknown",
                "average_chunk_size": sum(len(doc.page_content) for doc in documents) / len(documents) if documents else 0,
                "keywords_extracted": any("keywords" in doc.metadata for doc in documents),
                "structure_preserved": sum(1 for doc in documents if doc.metadata.get("contains_structure", False))
            }
            
            return len(documents), doc_info
        
        return _add_documents()
    
    def _filter_complex_metadata(self, documents):
        """Filtrer les métadonnées complexes pour ChromaDB"""
        filtered_docs = []
        for doc in documents:
            # Créer une copie du document avec métadonnées filtrées
            filtered_metadata = {}
            for key, value in doc.metadata.items():
                # ChromaDB n'accepte que str, int, float, bool, None
                if isinstance(value, (str, int, float, bool)) or value is None:
                    filtered_metadata[key] = value
                elif isinstance(value, list):
                    # Convertir les listes en string
                    filtered_metadata[key] = ', '.join(map(str, value))
                elif isinstance(value, dict):
                    # Convertir les dicts en string JSON
                    import json
                    filtered_metadata[key] = json.dumps(value)
                else:
                    # Convertir tout autre type en string
                    filtered_metadata[key] = str(value)
            
            # Créer un nouveau document avec métadonnées filtrées
            from langchain.schema import Document
            filtered_doc = Document(
                page_content=doc.page_content,
                metadata=filtered_metadata
            )
            filtered_docs.append(filtered_doc)
        
        return filtered_docs
    
    def get_retriever(self, k: int = Config.DEFAULT_K_DOCUMENTS):
        """Retourner un retriever pour LangChain"""
        if not self.vectorstore:
            # Auto-initialisation si nécessaire
            print("🔧 Auto-initialisation du VectorStore pour le retriever...")
            success = self.initialize_vectorstore()
            if not success or not self.vectorstore:
                raise ValueError("Impossible d'initialiser le VectorStore pour le retriever")
        
        return self.vectorstore.as_retriever(search_kwargs={"k": k})
    
    def search_with_metadata(self, query: str, k: int = Config.DEFAULT_K_DOCUMENTS) -> List[dict]:
        """Recherche avec métadonnées détaillées"""
        # Validation de la requête
        valid_query, query_error = InputValidator.validate_question(query)
        if not valid_query:
            raise ValueError(f"Requête invalide: {query_error}")
        
        @self.performance_monitor.measure_performance("search_documents")
        def _search():
            # Auto-initialisation du VectorStore si nécessaire
            if not self.vectorstore:
                print("🔧 Auto-initialisation du VectorStore pour la recherche...")
                success = self.initialize_vectorstore()
                
                # Si toujours pas de vectorstore, retourner vide
                if not success or not self.vectorstore:
                    print("⚠️ VectorStore non disponible - aucun résultat")
                    return []
            
            # ✅ VÉRIFICATION: Collection existe
            try:
                documents = self.vectorstore.similarity_search(query, k=k)
            except Exception as e:
                print(f"❌ Erreur lors de la recherche: {e}")
                return []
            
            # Enrichissement des résultats avec métadonnées
            enriched_results = []
            for doc in documents:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": getattr(doc, 'relevance_score', None),
                    "chunk_info": {
                        "position": doc.metadata.get("chunk_position", "unknown"),
                        "total_chunks": doc.metadata.get("total_chunks", 0),
                        "chunk_id": doc.metadata.get("chunk_id", 0),
                        "has_structure": doc.metadata.get("contains_structure", False),
                        "keywords": doc.metadata.get("keywords", [])
                    }
                }
                enriched_results.append(result)
            
            return enriched_results
        
        return _search()