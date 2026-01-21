# DontREADME - Plateforme d'Analyse Documentaire Intelligente

> **ChatBot documentaire avancé avec orchestration Prefect intégrée**

DontREADME transforme vos documents en une base de connaissances conversationnelle puissante. Analysez, questionnez et automatisez le traitement de vos PDF, DOCX et fichiers texte avec l'intelligence artificielle Mistral AI.

## Fonctionnalités Principales

### **Intelligence Documentaire**
- **Analyse multiformat** : PDF, DOCX, TXT
- **Découpage intelligent** : Préservation de la structure et du contexte
- **Templates adaptatifs** : Optimisation automatique selon le type de document
- **Recherche sémantique** : Compréhension du sens, pas seulement des mots-clés

### **Orchestration Automatisée**
- **Traitement par lot** : Analyse de dossiers complets en parallèle
- **Maintenance automatique** : Optimisation et sauvegarde de la base de données
- **Surveillance continue** : Monitoring de santé et performances
- **Tests automatisés** : Validation continue de la qualité

### **Interface Unifiée**
- **Gradio moderne** : Interface web intuitive et responsive
- **Gestion d'orchestration** : Contrôle des workflows en un clic
- **Feedback temps réel** : Statuts, métriques et logs intégrés
- **Monitoring visuel** : Tableaux de bord et alertes

## Installation Rapide

### Prérequis
- **Python 3.8+**
- **macOS/Linux** (Windows supporté avec WSL)
- **4GB RAM minimum** (8GB recommandé)

### Installation Automatique
```bash
# 1. Cloner le projet
git clone <votre-repo> DontREADME
cd DontREADME

# 2. Configuration automatique
python scripts/setup_orchestration.py

# 3. Configuration de la clé API
export MISTRAL_API_KEY="votre_cle_api_mistral"

# 4. Démarrage
./scripts/start_prefect.sh
python app/main.py
```

### Installation Manuelle
```bash
# Installation des dépendances
pip install -r requirements.txt

# Installation système (macOS)
brew install libmagic

# Configuration Prefect
prefect config set PREFECT_API_URL="http://localhost:4200/api"

# Démarrage des services
./scripts/start_prefect.sh &
python app/main.py
```

## Guide d'Utilisation

### 1. **Première Utilisation**

#### Accès à l'Interface
- **URL Principale** : http://localhost:7860
- **Interface Prefect** : http://localhost:4200 (optionnel)

#### Configuration Initiale
1. Ouvrir l'onglet **"⚙️ Configuration Avancée"**
2. Saisir votre **clé API Mistral AI**
3. Uploader votre premier document
4. Cliquer **"Traiter le document"**

### 2. **Analyse de Documents**

#### Types de Documents Supportés
- **PDF** : Extraction de texte avec préservation de structure
- **DOCX** : Documents Word avec formatage
- **TXT** : Fichiers texte simples

#### Paramètres d'Analyse
- **Taille des chunks** : 200-2000 caractères (1000 par défaut)
- **Documents récupérés** : 1-10 sources par réponse
- **Type de template** : Auto-détection ou sélection manuelle

#### Résultats d'Analyse
```
Document traité avec succès!

Informations du document
- Fichier: rapport_annuel.pdf
- Type détecté: académique
- Chunks créés: 42
- Template utilisé: academic
- Mots-clés extraits: ✅
```

### 3. **Chat Intelligent**

#### Interface de Conversation
- **Questions naturelles** : Posez vos questions en français
- **Réponses contextuelles** : Sources et métadonnées incluses
- **Historique persistant** : Conversation sauvegardée
- **Suggestions intelligentes** : Amélioration continue

#### Exemples de Questions
```
"Résume ce document en 3 points clés"
"Quelles sont les recommandations principales ?"
"Compare les chiffres de 2023 et 2024"
"Y a-t-il des risques mentionnés ?"
```

#### Réponses Enrichies
```
Réponse détaillée avec analyse contextuelle...

Sources consultées:
Page 15 | Mots-clés: budget, prévisions, croissance
Page 23 | Mots-clés: objectifs, stratégie, risques

Template: academic | Sources: 3 | Performance: 2.34s
```

### 4. **Orchestration Avancée**

#### Accès aux Workflows
- Ouvrir l'onglet **"Orchestration Prefect"**
- Vérifier le statut du serveur (vert = connecté)
- Utiliser les actions rapides ou workflows avancés

#### Actions Rapides (Un Clic)

##### **Vérification Santé**
```
Vérification de santé terminée

Score de santé: 87/100
Statut: HEALTHY

Système:
- CPU: 25.3%
- Mémoire: 42.1%
- Disque: 67.8%

ChromaDB: healthy
```

##### **Traitement par Lot**
```
Traitement par lot terminé

Résultats:
- Documents traités: 12
- Échecs: 0
- Taux de succès: 100.0%
- Temps total: 34.2s
```

##### **Maintenance Automatique**
```
Maintenance terminée

Opérations:
- Sauvegarde: ✅ success
- Optimisation: ✅ success

Durée: 45.3 secondes
Amélioration santé: +3.2 points
```

### 5. **Monitoring et Performance**

#### Métriques en Temps Réel
- **Performance** : Temps de traitement, taux de succès
- **Ressources** : CPU, mémoire, espace disque
- **Santé** : Score global sur 100 points
- **Activité** : Documents traités, questions posées

#### Tableau de Bord
```
Statistiques Aujourd'hui:
- Documents analysés: 24
- Questions répondues: 156  
- Temps moyen réponse: 2.1s
- Score santé: 89/100
- Workflows exécutés: 12
```

#### Alertes et Notifications
- **Score santé < 70** : Alerte système
- **Erreurs répétées** : Notification d'intervention
- **Maintenance réussie** : Confirmation par email (configurable)

## Configuration Avancée

### Variables d'Environnement
```bash
# Obligatoire
export MISTRAL_API_KEY="votre_cle_api"

# Optionnel
export NOTIFICATION_EMAIL="admin@example.com"
export ALERT_THRESHOLD="70"
export WATCH_FOLDER="./data/inbox"
export MAX_WORKERS="3"
```

### Personnalisation
```python
# app/config.py
class Config:
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_K_DOCUMENTS = 3
    MISTRAL_MODEL = "mistral-tiny"
    CHROMADB_PATH = "./data/vectorstore"
```

### Templates Personnalisés
```python
# utils/prompt_templates.py
CUSTOM_TEMPLATE = """
Contexte: {context}
Question: {question}

Réponds en adoptant le style d'un expert dans le domaine.
Utilise des exemples concrets et des références précises.
"""
```

## Structure des Données

### Dossiers de Travail
```
data/
├── uploads/          # Documents uploadés temporairement
├── vectorstore/      # Base de données ChromaDB
├── inbox/            # Documents pour traitement automatique
├── exports/          # Exports et rapports générés
├── backups/          # Sauvegardes automatiques
├── reports/          # Rapports de performance
└── monitoring/       # Logs et métriques historiques
```

### Formats d'Export
- **Sessions** : JSON avec historique complet
- **Rapports** : JSON structuré avec métriques
- **Logs** : Format texte horodaté
- **Métriques** : CSV pour analyse externe

## Maintenance et Dépannage

### Maintenance Régulière

#### Quotidienne (Automatique)
- ✅ Vérification santé système
- ✅ Tests de fonctionnement
- ✅ Traitement nouveaux documents

#### Hebdomadaire (Automatique)
- ✅ Sauvegarde base de données
- ✅ Optimisation des collections
- ✅ Nettoyage fichiers anciens
- ✅ Rapport de performance

#### Mensuelle (Manuelle)
- Vérification des logs
- Analyse des métriques
- Nettoyage approfondi
- Optimisation des paramètres

### Problèmes Courants

#### "Serveur Prefect non disponible"
```bash
# Vérifier le statut
curl http://localhost:4200/api/health

# Redémarrer si nécessaire
./scripts/stop_prefect.sh
./scripts/start_prefect.sh
```

#### "Clé API invalide"
```bash
# Vérifier la variable
echo $MISTRAL_API_KEY

# Redéfinir si nécessaire
export MISTRAL_API_KEY="votre_nouvelle_cle"
```

#### "Erreur de traitement document"
1. Vérifier le format du fichier (PDF/DOCX/TXT)
2. Contrôler la taille (< 10MB)
3. Valider l'encodage (UTF-8 recommandé)
4. Consulter les logs dans l'onglet Monitoring

#### "Performance dégradée"
1. Vérifier l'espace disque disponible
2. Redémarrer l'application si nécessaire
3. Optimiser la base de données (maintenance)
4. Ajuster les paramètres de chunks

### Logs et Debugging
```bash
# Logs application
tail -f logs/app.log

# Logs Prefect
tail -f logs/prefect_server.log
tail -f logs/prefect_worker.log

# Statut système
python -c "from workflows.tasks import check_system_health; print(check_system_health())"
```

## Sécurité et Confidentialité

### Protection des Données
- **Stockage local** : Aucune donnée envoyée vers des serveurs externes
- **Chiffrement** : Clés API sécurisées en mémoire
- **Validation** : Tous les inputs sont validés et nettoyés
- **Isolation** : Chaque session est indépendante

### Bonnes Pratiques
- ✅ Utiliser des clés API dédiées (non partagées)
- ✅ Sauvegarder régulièrement la base ChromaDB
- ✅ Limiter l'accès réseau (localhost uniquement)
- ✅ Surveiller les logs pour détecter des anomalies

### Conformité
- **RGPD** : Pas de collecte de données personnelles
- **Local** : Traitement entièrement sur votre machine
- **Audit** : Logs complets pour traçabilité
- **Contrôle** : Vous gardez la maîtrise totale de vos données

## Cas d'Usage

### **Entreprise**
- **Analyse de contrats** : Extraction d'informations clés
- **Veille documentaire** : Surveillance de rapports sectoriels
- **Support client** : Base de connaissances conversationnelle
- **Audit de conformité** : Analyse de politiques et procédures

### **Recherche et Éducation**
- **Analyse de publications** : Extraction de méthodologies et résultats
- **Préparation de cours** : Synthèse de sources multiples
- **Revue de littérature** : Identification de tendances et gaps
- **Évaluation de thèses** : Analyse de cohérence et qualité

### **Juridique**
- **Analyse de jurisprudence** : Recherche de précédents
- **Préparation de dossiers** : Synthèse de documents légaux
- **Due diligence** : Analyse de contrats et accords
- **Veille réglementaire** : Suivi des évolutions légales

### **Santé et Médical**
- **Analyse de rapports** : Extraction d'informations cliniques
- **Veille scientifique** : Suivi des publications médicales
- **Protocoles de soins** : Navigation dans les recommandations
- **Formation continue** : Synthèse de littérature médicale

## Évolutions Futures

### Version 2.0 (Roadmap)
- **Multi-utilisateurs** : Gestion des permissions et espaces
- **API REST** : Intégration avec systèmes externes
- **Connecteurs cloud** : Google Drive, SharePoint, Dropbox
- **Analytics avancés** : Tableaux de bord interactifs

### Améliorations Planifiées
- **Support PowerPoint** : Analyse de présentations
- **OCR intégré** : Traitement d'images et scans
- **Recherche fédérée** : Requêtes multi-documents
- **Templates métier** : Spécialisations sectorielles

### Contributions
- **Open Source** : Code disponible pour modifications
- **Extensions** : Plugin system pour fonctionnalités custom
- **Communauté** : Partage de templates et workflows
- **Formation** : Tutoriels et webinaires

---

## Conclusion

### Pourquoi Choisir DontREADME ?

**Simplicité** : Interface intuitive, installation en 5 minutes
**Intelligence** : IA avancée avec compréhension contextuelle  
**Automatisation** : Workflows orchestrés pour gain de productivité
**Sécurité** : Traitement local, contrôle total de vos données
**Évolutivité** : Architecture extensible et personnalisable

Mais surtout : **La Flemme de tout lire !!**

### Démarrez Maintenant 

```bash
# Installation en une commande
curl -sSL https://get.dontreadme.ai | python3

# Ou manuellement
git clone <repo> && cd DontREADME && python scripts/setup_orchestration.py
```


  cd /Users/abdeltouati/Desktop/DontREADME
  source venv/bin/activate && python app/main.py

  ou 

  python app/main.py# DontREADME
  
## DontREADME est le fruit d'une sorte de Hackathon individuel d'une durée de 36 heures, durant ma formation de Chef de Projet IA.
