"""
Script de démonstration DontREADME
Permet de tester rapidement les fonctionnalités principales
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Afficher la bannière de démonstration"""
    print("=" * 60)
    print(" DÉMONSTRATION DONTREADME")
    print("=" * 60)
    print("Plateforme d'Analyse Documentaire Intelligente")
    print("Développé avec  et Claude Sonnet 4")
    print("=" * 60)

def check_environment():
    """Vérifier l'environnement de démonstration"""
    print("\n Vérification de l'environnement...")
    
    # Vérifier Python
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"[OK] Python {python_version.major}.{python_version.minor}")
    else:
        print(f"[ERROR] Python {python_version.major}.{python_version.minor} - Version 3.8+ requise")
        return False
    
    # Vérifier les modules critiques
    modules = [
        ("gradio", "Interface web"),
        ("langchain", "Framework IA"),
        ("chromadb", "Base vectorielle"),
        ("mistralai", "LLM"),
        ("prefect", "Orchestration")
    ]
    
    all_good = True
    for module, description in modules:
        try:
            __import__(module)
            print(f"[OK] {module} - {description}")
        except ImportError:
            print(f"[ERROR] {module} - {description} (pip install {module})")
            all_good = False
    
    return all_good

def check_system_components():
    """Vérifier les composants système"""
    print("\n Vérification des composants...")
    
    # Vérifier la structure des fichiers
    critical_files = [
        "app/main.py",
        "app/config.py",
        "utils/validators.py",
        "workflows/tasks.py",
        "scripts/start_prefect.sh",
        "requirements.txt"
    ]
    
    all_files_ok = True
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[ERROR] {file_path} manquant")
            all_files_ok = False
    
    return all_files_ok

def demo_configuration():
    """Démonstration de la configuration"""
    print("\n Configuration du système...")
    
    try:
        from app.config import Config
        print(f"[OK] Chunk size par défaut: {Config.DEFAULT_CHUNK_SIZE}")
        print(f"[OK] Documents récupérés: {Config.DEFAULT_K_DOCUMENTS}")
        print(f"[OK] Modèle Mistral: {Config.MISTRAL_MODEL}")
        print(f"[OK] Chemin ChromaDB: {Config.CHROMADB_PATH}")
        return True
    except Exception as e:
        print(f"[ERROR] Erreur configuration: {e}")
        return False

def demo_components():
    """Démonstration des composants"""
    print("\n🧩 Test des composants...")
    
    components = [
        ("app.components.file_processor", "FileProcessor", "Traitement fichiers"),
        ("utils.validators", "FileValidator", "Validation"),
        ("utils.performance", "PerformanceMonitor", "Monitoring"),
        ("utils.text_splitter", "SmartTextSplitter", "Découpage intelligent")
    ]
    
    all_components_ok = True
    for module, component, description in components:
        try:
            exec(f"from {module} import {component}")
            print(f"[OK] {component} - {description}")
        except Exception as e:
            print(f"[ERROR] {component} - {description}: {e}")
            all_components_ok = False
    
    return all_components_ok

def demo_orchestration():
    """Démonstration de l'orchestration"""
    print("\n Test de l'orchestration...")
    
    try:
        from app.orchestration_interface import orchestration_interface
        print(f"[OK] Interface orchestration: {type(orchestration_interface).__name__}")
        
        from app.components.prefect_bridge import prefect_bridge
        print(f"[OK] Pont Prefect: {type(prefect_bridge).__name__}")
        print(f"[OK] Workflows disponibles: {'Oui' if prefect_bridge.is_available() else 'Non (normal en mode test)'}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Erreur orchestration: {e}")
        return False

def show_usage_examples():
    """Afficher des exemples d'utilisation"""
    print("\n📚 Exemples d'utilisation:")
    print("""
 Démarrage rapide:
   python app/main.py

 Configuration Prefect:
   ./scripts/start_prefect.sh

 Tests système:
   python test_system_status.py

 Interface web:
   http://localhost:7860

 Interface Prefect:
   http://localhost:4200
""")

def show_next_steps():
    """Afficher les prochaines étapes"""
    print("\n Prochaines étapes:")
    print("""
1.  Configurer votre clé API:
   export MISTRAL_API_KEY="votre_cle_api"

2.  Démarrer l'application:
   python app/main.py

3.  Uploader un document dans l'interface

4.  Poser vos premières questions

5.  Explorer l'orchestration Prefect

6.  Surveiller les performances
""")

def main():
    """Fonction principale de démonstration"""
    print_banner()
    
    # Tests de l'environnement
    checks = [
        ("Environnement Python", check_environment),
        ("Composants système", check_system_components),
        ("Configuration", demo_configuration),
        ("Composants applicatifs", demo_components),
        ("Orchestration", demo_orchestration)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"[ERROR] Erreur {check_name}: {e}")
            all_passed = False
    
    # Résultat final
    print("\n" + "=" * 60)
    if all_passed:
        print(" DÉMONSTRATION RÉUSSIE!")
        print("[OK] Tous les composants sont opérationnels")
        print(" DontREADME est prêt à être utilisé!")
    else:
        print("[WARN] PROBLÈMES DÉTECTÉS")
        print(" Certains composants nécessitent une attention")
        print(" Consultez les messages ci-dessus pour les corrections")
    
    print("=" * 60)
    
    # Afficher les informations d'usage
    show_usage_examples()
    show_next_steps()
    
    print("\n💡 Pour plus d'informations:")
    print("   📖 README.md - Guide utilisateur complet")
    print("    DEVELOPER_GUIDE.md - Documentation technique")
    print("   🆘 Issues GitHub pour le support")

if __name__ == "__main__":
    main()