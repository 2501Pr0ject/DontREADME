#!/usr/bin/env python3
"""
Script de configuration de l'orchestration Prefect pour DontREADME
"""

import os
import sys
import subprocess
from pathlib import Path

def check_prefect_installation():
    """Vérifier si Prefect est installé"""
    try:
        import prefect
        print(f"✅ Prefect installé - version: {prefect.__version__}")
        return True
    except ImportError:
        print("❌ Prefect non installé")
        return False

def install_prefect():
    """Installer Prefect et ses dépendances"""
    print("📦 Installation de Prefect...")
    
    packages = [
        "prefect>=2.14.0",
        "prefect-shell>=0.2.0",
        "psutil>=5.9.0",
        "aiofiles>=23.0.0"
    ]
    
    try:
        for package in packages:
            print(f"   Installation de {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("✅ Installation Prefect terminée")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation: {e}")
        return False

def create_directories():
    """Créer les répertoires nécessaires"""
    directories = [
        "./data/prefect_storage",
        "./data/inbox",
        "./data/reports",
        "./data/backups",
        "./data/monitoring",
        "./data/workflow_results",
        "./tests/documents",
        "./logs"
    ]
    
    print("📁 Création des répertoires...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")

def create_test_documents():
    """Créer des documents de test pour les workflows"""
    test_dir = Path("./tests/documents")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Document de test simple
    test_content = """
# Document de Test DontREADME

Ceci est un document de test pour l'orchestration Prefect de DontREADME.

## Section 1: Introduction
Ce document contient du contenu de test structuré pour valider le bon fonctionnement des workflows.

## Section 2: Contenu Principal
Le système DontREADME utilise Prefect pour orchestrer les tâches suivantes:
- Traitement de documents
- Maintenance automatisée
- Surveillance système
- Tests automatisés

## Section 3: Conclusions
L'orchestration Prefect améliore significativement la robustesse et l'automatisation du système.

Points clés:
- Workflows automatisés
- Surveillance continue
- Maintenance programmée
- Tests de régression

Recommandations:
1. Surveiller les performances régulièrement
2. Maintenir les workflows à jour
3. Vérifier les logs d'exécution
    """
    
    test_file = test_dir / "test_document.txt"
    if not test_file.exists():
        test_file.write_text(test_content, encoding='utf-8')
        print(f"✅ Document de test créé: {test_file}")

def check_environment():
    """Vérifier l'environnement"""
    print("🔍 Vérification de l'environnement...")
    
    # Vérifier Python
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python {python_version.major}.{python_version.minor} - Version 3.8+ requise")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}")
    
    # Vérifier les modules DontREADME
    try:
        sys.path.append(str(Path.cwd()))
        from app.config import Config
        print("✅ Modules DontREADME disponibles")
    except ImportError as e:
        print(f"❌ Erreur import DontREADME: {e}")
        return False
    
    return True

def setup_prefect_config():
    """Configurer Prefect"""
    print("⚙️ Configuration de Prefect...")
    
    # Définir les variables d'environnement
    os.environ["PREFECT_API_DATABASE_CONNECTION_URL"] = f"sqlite+aiosqlite:///{Path.cwd()}/data/prefect.db"
    
    try:
        # Import après installation
        from prefect import settings
        
        # Configuration de base
        config_commands = [
            ['prefect', 'config', 'set', 'PREFECT_API_URL=http://localhost:4200/api'],
            ['prefect', 'config', 'set', 'PREFECT_LOGGING_LEVEL=INFO']
        ]
        
        for cmd in config_commands:
            print(f"   Exécution: {' '.join(cmd)}")
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                # Continuer même si la commande échoue (config peut déjà exister)
                pass
        
        print("✅ Configuration Prefect terminée")
        return True
    except Exception as e:
        print(f"⚠️ Configuration partielle: {e}")
        return True  # Continue même si config partielle

def test_workflows_import():
    """Tester l'import des workflows"""
    print("🧪 Test d'import des workflows...")
    
    try:
        sys.path.append(str(Path.cwd()))
        
        # Test import des workflows
        from workflows.batch_processing import batch_document_flow
        from workflows.maintenance import database_maintenance_flow
        from workflows.monitoring import health_check_flow
        from workflows.testing import smoke_testing_flow
        
        print("✅ Workflows importés avec succès")
        return True
    except ImportError as e:
        print(f"❌ Erreur import workflows: {e}")
        return False

def create_startup_info():
    """Créer un fichier d'informations de démarrage"""
    info_content = f"""
# Configuration Orchestration DontREADME

## Statut de l'installation
- Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Répertoire: {Path.cwd()}
- Python: {sys.version.split()[0]}

## Commandes utiles

### Démarrer Prefect
```bash
./scripts/start_prefect.sh
```

### Arrêter Prefect
```bash
./scripts/stop_prefect.sh
```

### Interface Web
- URL: http://localhost:4200
- API: http://localhost:4200/api

### Variables d'environnement
```bash
export MISTRAL_API_KEY="votre_cle_api"
export PREFECT_API_URL="http://localhost:4200/api"
```

## Workflows disponibles
- Traitement batch: batch_document_flow
- Vérification santé: health_check_flow  
- Maintenance DB: database_maintenance_flow
- Tests smoke: smoke_testing_flow

## Dépannage
- Logs serveur: ./logs/prefect_server.log
- Logs worker: ./logs/prefect_worker.log
- Base de données: ./data/prefect.db
    """
    
    info_file = Path("./ORCHESTRATION_INFO.md")
    info_file.write_text(info_content, encoding='utf-8')
    print(f"✅ Informations sauvegardées: {info_file}")

def main():
    """Fonction principale"""
    print("🚀 Configuration de l'orchestration Prefect pour DontREADME\n")
    
    # Étape 1: Vérifier l'environnement
    if not check_environment():
        print("❌ Environnement non compatible")
        sys.exit(1)
    
    # Étape 2: Installer Prefect si nécessaire
    if not check_prefect_installation():
        if not install_prefect():
            print("❌ Échec installation Prefect")
            sys.exit(1)
    
    # Étape 3: Créer les répertoires
    create_directories()
    
    # Étape 4: Créer des documents de test
    create_test_documents()
    
    # Étape 5: Configurer Prefect
    setup_prefect_config()
    
    # Étape 6: Tester les imports
    if not test_workflows_import():
        print("⚠️ Workflows non disponibles - installation partielle")
    
    # Étape 7: Créer les informations
    create_startup_info()
    
    print("\n🎉 Configuration terminée!")
    print("\n📋 Prochaines étapes:")
    print("1. Définir votre clé API: export MISTRAL_API_KEY='votre_cle'")
    print("2. Démarrer Prefect: ./scripts/start_prefect.sh")
    print("3. Lancer l'application: python app/main.py")
    print("4. Accéder à l'onglet 'Orchestration Prefect'")
    
    print("\n🌐 Interfaces:")
    print("- Application: http://localhost:7860")
    print("- Prefect UI: http://localhost:4200")

if __name__ == "__main__":
    main()