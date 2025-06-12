#!/usr/bin/env python3
"""
Test des différents types d'embeddings
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_huggingface_api_embeddings():
    """Test des embeddings HuggingFace API"""
    print("🧪 Test des embeddings HuggingFace API")
    print("=" * 40)
    
    try:
        from app.components.vectorstore import HuggingFaceAPIEmbeddings
        
        # Initialisation
        embeddings = HuggingFaceAPIEmbeddings()
        print("✅ Initialisation réussie")
        
        # Test d'un embedding simple
        test_text = "Ceci est un test d'embedding"
        result = embeddings.embed_query(test_text)
        
        if isinstance(result, list) and len(result) == 384:
            print(f"✅ Embedding généré: {len(result)} dimensions")
            print(f"   Exemple: [{result[0]:.3f}, {result[1]:.3f}, ...]")
        else:
            print(f"⚠️ Embedding inattendu: {type(result)}, longueur: {len(result) if isinstance(result, list) else 'N/A'}")
        
        # Test d'embeddings multiples
        test_docs = ["Document 1", "Document 2", "Document 3"]
        results = embeddings.embed_documents(test_docs)
        
        if len(results) == 3 and all(len(emb) == 384 for emb in results):
            print(f"✅ Embeddings multiples: {len(results)} documents")
        else:
            print(f"⚠️ Problème avec embeddings multiples")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_vectorstore_integration():
    """Test de l'intégration avec ChromaDB"""
    print("\n🧪 Test d'intégration ChromaDB")
    print("=" * 35)
    
    try:
        from app.components.vectorstore import EnhancedVectorStoreManager
        
        # Initialisation
        manager = EnhancedVectorStoreManager()
        print("✅ VectorStore Manager initialisé")
        
        # Test d'initialisation
        success = manager.initialize_vectorstore(collection_name="test_collection")
        if success:
            print("✅ VectorStore initialisé")
        else:
            print("❌ Échec d'initialisation VectorStore")
            return False
        
        # Test d'ajout de documents
        test_text = """
        Ceci est un document de test pour vérifier le fonctionnement
        du système d'embeddings avec ChromaDB. Il contient plusieurs
        phrases pour tester le découpage intelligent.
        """
        
        num_chunks, doc_info = manager.add_documents_enhanced(
            text=test_text,
            filename="test_doc.txt",
            chunk_size=100,
            chunk_overlap=20
        )
        
        print(f"✅ Document ajouté: {num_chunks} chunks")
        print(f"   Type détecté: {doc_info['document_type']}")
        
        # Test de recherche
        results = manager.search_with_metadata("document test", k=2)
        if results:
            print(f"✅ Recherche fonctionnelle: {len(results)} résultats")
        else:
            print("⚠️ Aucun résultat de recherche")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Exécuter tous les tests d'embeddings"""
    print("🔬 TESTS DES EMBEDDINGS DONTREADME")
    print("=" * 50)
    
    results = []
    
    # Test 1: Embeddings HuggingFace API
    results.append(test_huggingface_api_embeddings())
    
    # Test 2: Intégration VectorStore
    results.append(test_vectorstore_integration())
    
    # Résumé
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 RÉSULTATS: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests d'embeddings sont OK!")
    else:
        print("⚠️ Certains tests ont échoué - vérifiez la configuration")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()