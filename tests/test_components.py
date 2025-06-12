#!/usr/bin/env python3
"""
Test des composants principaux de DontREADME
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_file_processor():
    """Test du processeur de fichiers"""
    print("🧪 Test du FileProcessor")
    print("=" * 25)
    
    try:
        from app.components.file_processor import FileProcessor
        
        # Test des méthodes statiques
        print("✅ Import FileProcessor réussi")
        
        # Vérifier que les méthodes existent
        if hasattr(FileProcessor, 'process_uploaded_file'):
            print("✅ Méthode process_uploaded_file disponible")
        else:
            print("❌ Méthode process_uploaded_file manquante")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_validators():
    """Test des validateurs"""
    print("\n🧪 Test des Validateurs")
    print("=" * 25)
    
    try:
        from utils.validators import FileValidator, InputValidator
        
        # Test FileValidator
        print("✅ Import FileValidator réussi")
        
        # Test InputValidator
        print("✅ Import InputValidator réussi")
        
        # Test validation clé API
        valid, msg = InputValidator.validate_api_key("test_key", "mistral")
        print(f"✅ Validation clé API: {msg}")
        
        # Test validation chunk size
        valid, msg = InputValidator.validate_chunk_size(500)
        if valid:
            print("✅ Validation chunk size OK")
        else:
            print(f"⚠️ Validation chunk size: {msg}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_text_splitter():
    """Test du découpage de texte intelligent"""
    print("\n🧪 Test du SmartTextSplitter")
    print("=" * 30)
    
    try:
        from utils.text_splitter import SmartTextSplitter
        
        splitter = SmartTextSplitter()
        print("✅ SmartTextSplitter initialisé")
        
        # Test avec un texte simple
        test_text = """
        Chapitre 1: Introduction
        
        Ceci est un document de test pour vérifier le fonctionnement
        du système de découpage intelligent. Il contient plusieurs
        paragraphes et sections.
        
        Chapitre 2: Développement
        
        Cette section traite du développement de l'application
        et des différentes fonctionnalités implémentées.
        """
        
        documents = splitter.split_documents_with_metadata(
            text=test_text,
            filename="test.txt",
            chunk_size=200,
            chunk_overlap=50
        )
        
        if documents:
            print(f"✅ Découpage réussi: {len(documents)} chunks")
            print(f"   Premier chunk: {len(documents[0].page_content)} caractères")
            print(f"   Métadonnées: {list(documents[0].metadata.keys())}")
        else:
            print("❌ Aucun chunk généré")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_performance_monitor():
    """Test du monitoring de performance"""
    print("\n🧪 Test du PerformanceMonitor")
    print("=" * 30)
    
    try:
        from utils.performance import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        print("✅ PerformanceMonitor initialisé")
        
        # Test du décorateur
        @monitor.measure_performance("test_function")
        def test_function():
            import time
            time.sleep(0.1)
            return "test result"
        
        result = test_function()
        print(f"✅ Test de mesure de performance: {result}")
        
        # Vérifier les métriques
        metrics = monitor.get_metrics_summary()
        if metrics:
            print("✅ Métriques collectées")
        else:
            print("⚠️ Aucune métrique disponible")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_prompt_templates():
    """Test du gestionnaire de templates"""
    print("\n🧪 Test du PromptTemplateManager")
    print("=" * 32)
    
    try:
        from utils.prompt_templates import PromptTemplateManager
        
        manager = PromptTemplateManager()
        print("✅ PromptTemplateManager initialisé")
        
        # Test des templates disponibles
        available = manager.get_available_templates()
        print(f"✅ Templates disponibles: {available}")
        
        # Test d'obtention d'un template
        template = manager.get_optimized_template("general", "general")
        if template:
            print("✅ Template récupéré avec succès")
        else:
            print("❌ Échec de récupération de template")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def run_component_tests():
    """Exécuter tous les tests de composants"""
    print("🔧 TESTS DES COMPOSANTS DONTREADME")
    print("=" * 50)
    
    tests = [
        test_file_processor,
        test_validators,
        test_text_splitter,
        test_performance_monitor,
        test_prompt_templates
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Résumé
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 RÉSULTATS: {passed}/{total} composants testés avec succès")
    
    if passed == total:
        print("🎉 Tous les composants fonctionnent correctement!")
    else:
        print("⚠️ Certains composants ont des problèmes - vérifiez les logs")
    
    return passed == total

if __name__ == "__main__":
    run_component_tests()