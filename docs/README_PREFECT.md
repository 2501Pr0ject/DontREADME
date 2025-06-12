# 🚀 Guide d'utilisation Prefect pour DontREADME

## 📋 Vue d'ensemble

L'orchestration Prefect pour DontREADME fournit une automatisation complète des workflows de traitement de documents, maintenance système, surveillance et tests. Cette implémentation permet une gestion robuste et scalable de votre chatbot documentaire.

## 🏗️ Architecture des Workflows

### 📄 Traitement de Documents
- **`batch_document_flow`** : Traitement en parallèle de multiples documents
- **`process_folder_documents`** : Workflow complet avec surveillance et rapports
- **`nightly_batch_processing`** : Traitement automatisé nocturne des nouveaux documents

### 🛠️ Maintenance
- **`database_maintenance_flow`** : Sauvegarde et optimisation ChromaDB
- **`cleanup_old_files_flow`** : Nettoyage des fichiers anciens avec simulation
- **`weekly_maintenance_flow`** : Maintenance complète hebdomadaire

### 📊 Surveillance
- **`health_check_flow`** : Surveillance continue de la santé système
- **`performance_monitoring_flow`** : Collecte de métriques de performance
- **`continuous_monitoring_flow`** : Surveillance prolongée avec alertes

### 🧪 Tests
- **`automated_testing_flow`** : Suite complète de tests automatisés
- **`regression_testing_flow`** : Tests de régression avec comparaison baseline
- **`smoke_testing_flow`** : Tests rapides de fonctionnement de base

## ⚡ Démarrage Rapide

### 1. Installation des dépendances
```bash
pip install prefect>=2.14.0 prefect-shell>=0.2.0
```

### 2. Démarrage de Prefect
```bash
./scripts/start_prefect.sh
```

### 3. Accès à l'interface web
- **URL** : http://localhost:4200
- **API** : http://localhost:4200/api

### 4. Configuration de la clé API
```bash
export MISTRAL_API_KEY="votre_cle_api_ici"
```

## 🕐 Planification Automatique

### Workflows Quotidiens
- **02:00** - Traitement nocturne des nouveaux documents
- **06:00** - Tests smoke quotidiens
- **Toutes les 15min** - Surveillance de santé système

### Workflows Hebdomadaires
- **Mardi 01:00** - Maintenance base de données ChromaDB
- **Vendredi 01:00** - Maintenance base de données ChromaDB
- **Samedi 04:00** - Tests automatisés complets
- **Dimanche 03:00** - Maintenance complète hebdomadaire

## 🎯 Utilisation Manuelle

### Lancer un workflow unique
```python
from workflows import batch_document_flow
import asyncio

# Traitement d'un dossier de documents
result = asyncio.run(batch_document_flow(
    documents_folder="./mon_dossier",
    api_key="votre_cle_api",
    file_extensions=['.pdf', '.docx', '.txt']
))
```

### Tests de santé système
```python
from workflows import health_check_flow
import asyncio

# Vérification santé avec alertes
result = asyncio.run(health_check_flow(
    alert_threshold=70,
    notification_email="admin@example.com"
))
```

### Maintenance manuelle
```python
from workflows import database_maintenance_flow
import asyncio

# Maintenance complète de la base
result = asyncio.run(database_maintenance_flow(
    vacuum_database=True,
    backup_database=True,
    optimize_collections=True
))
```

## 📊 Surveillance et Alertes

### Métriques Surveillées
- **CPU** : Utilisation processeur (seuil: 80%)
- **Mémoire** : Utilisation RAM (seuil: 85%)
- **Disque** : Espace disponible (seuil: 90%)
- **ChromaDB** : Santé et accessibilité
- **Répertoires** : Existence et permissions

### Seuils d'Alerte
- **Score santé < 70** : Alerte système
- **Score santé < 60** : Système dégradé
- **Score santé < 40** : Système défaillant

### Configuration des Notifications
```python
# Dans vos workflows
await health_check_flow(
    alert_threshold=70,
    notification_email="votre@email.com"
)
```

## 🗃️ Gestion des Données

### Structure de Stockage
```
data/
├── prefect.db              # Base Prefect SQLite
├── prefect_storage/        # Artefacts Prefect
├── inbox/                  # Documents à traiter
├── backups/               # Sauvegardes ChromaDB
├── reports/               # Rapports de performance
└── monitoring/            # Historique surveillance
```

### Sauvegardes Automatiques
- **ChromaDB** : Sauvegarde avant chaque maintenance
- **Rapports** : Conservation 30 jours
- **Métriques** : Rétention 30 jours

## 🧪 Tests et Qualité

### Types de Tests
1. **Tests de Santé** : Vérification des composants système
2. **Tests de Documents** : Traitement de différents formats
3. **Tests de Requêtes** : Qualité des réponses IA
4. **Tests de Performance** : Latence et ressources
5. **Tests de Robustesse** : Gestion d'erreurs

### Métriques de Qualité
- **Taux de succès** : % de tests réussis
- **Score de qualité** : Évaluation des réponses
- **Temps de réponse** : Latence des requêtes
- **Utilisation ressources** : CPU/Mémoire

### Tests de Régression
```python
from workflows import regression_testing_flow
import asyncio

# Comparer avec une baseline
result = asyncio.run(regression_testing_flow(
    api_key="votre_cle",
    baseline_report_path="./data/reports/baseline_test_report.json"
))
```

## ⚙️ Configuration Avancée

### Variables d'Environnement
```bash
export MISTRAL_API_KEY="votre_cle_api"
export NOTIFICATION_EMAIL="admin@example.com"
export ALERT_THRESHOLD="70"
export WATCH_FOLDER="./data/inbox"
export MAX_WORKERS="3"
```

### Configuration Prefect
```yaml
# prefect.yaml
work_pools:
  - name: default-agent-pool
    type: process
    concurrency_limit: 3

resources:
  memory_limit: "1GB"
  cpu_limit: 2
  storage_limit: "5GB"
```

### Personnalisation des Workflows
```python
# Workflow personnalisé
@flow(name="mon_workflow_custom")
async def mon_workflow(param1: str, param2: int):
    # Votre logique métier
    result = await ma_tache_custom(param1, param2)
    return result
```

## 🔧 Dépannage

### Problèmes Courants

#### Serveur Prefect ne démarre pas
```bash
# Vérifier les ports occupés
lsof -i :4200

# Redémarrer proprement
./scripts/stop_prefect.sh
./scripts/start_prefect.sh
```

#### Workers ne se connectent pas
```bash
# Vérifier les pools de workers
prefect work-pool ls

# Créer un nouveau pool si nécessaire
prefect work-pool create mon-pool --type process
```

#### Clé API manquante
```bash
# Définir la variable d'environnement
export MISTRAL_API_KEY="votre_cle_api"

# Ou utiliser Prefect secrets
prefect secret set MISTRAL_API_KEY
```

### Logs et Debugging
```bash
# Logs serveur Prefect
tail -f logs/prefect_server.log

# Logs worker
tail -f logs/prefect_worker.log

# Logs des workflows
prefect flow-run logs <run-id>
```

## 📈 Performance et Scalabilité

### Optimisations Implémentées
- **Traitement parallèle** : Jusqu'à 3 documents simultanés
- **Retry automatique** : Nouvelle tentative sur échec
- **Timeout intelligent** : Évite les blocages
- **Cache local** : Réutilisation des embeddings
- **Monitoring continu** : Détection proactive des problèmes

### Recommandations de Scaling
- **CPU** : 2-4 cœurs recommandés
- **RAM** : 4-8 GB selon le volume
- **Stockage** : SSD pour ChromaDB
- **Workers** : 1 worker par 2 cœurs CPU

## 🔐 Sécurité

### Bonnes Pratiques
- **Clés API** : Stockage sécurisé via Prefect secrets
- **Accès réseau** : Interface web locale uniquement
- **Validation** : Tous les inputs sont validés
- **Logs** : Pas de secrets dans les logs
- **Sauvegarde** : Chiffrement des backups sensibles

### Configuration de Production
```bash
# Variables d'environnement sécurisées
export PREFECT_API_URL="https://votre-prefect-cloud.com/api"
export PREFECT_API_KEY="votre_cle_cloud"

# Base de données PostgreSQL pour la production
export PREFECT_API_DATABASE_CONNECTION_URL="postgresql://user:pass@host/db"
```

## 📚 Ressources Supplémentaires

### Documentation
- [Documentation officielle Prefect](https://docs.prefect.io/)
- [Guide Prefect 2.0](https://docs.prefect.io/2.0/)
- [API Reference](https://docs.prefect.io/api-ref/)

### Commandes Utiles
```bash
# État des workflows
prefect flow ls
prefect deployment ls
prefect flow-run ls --limit 10

# Monitoring
prefect work-pool ls
prefect agent ls

# Configuration
prefect config view
prefect profile ls
```

### Support et Communauté
- [Forum Prefect](https://discourse.prefect.io/)
- [Slack Prefect](https://prefect.io/slack/)
- [GitHub Issues](https://github.com/PrefectHQ/prefect/issues)

---

## 🎯 Conclusion

Cette implémentation Prefect transforme DontREADME en une solution robuste et automatisée, capable de gérer l'ensemble du cycle de vie documentaire avec surveillance, maintenance et tests intégrés. L'architecture modulaire permet une extension facile selon vos besoins spécifiques.

Pour toute question ou personnalisation, n'hésitez pas à consulter la documentation des workflows dans le dossier `workflows/` ou à adapter les configurations selon votre environnement.

**Bonne orchestration ! 🚀**