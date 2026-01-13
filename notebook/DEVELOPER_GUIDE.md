#  Guide Développeur DontREADME

> **Documentation technique complète pour comprendre, modifier et étendre DontREADME**

Ce guide explique en détail l'architecture, les composants, et le fonctionnement interne de DontREADME. Idéal pour les développeurs souhaitant comprendre, modifier ou étendre le système.

##  Architecture du Projet

### Vue d'Ensemble
```
DontREADME/
├── 📱 app/                    # Application principale
├──  utils/                  # Utilitaires avancés
├──  workflows/              # Orchestration Prefect
├──  scripts/                # Scripts d'automatisation
├──  data/                   # Données et stockage
├──  tests/                  # Tests (structure préparée)
├──  logs/                   # Logs système
└── 📚 docs/                   # Documentation
```

##  Structure Détaillée

### 📱 **Dossier `app/` - Application Principale**

#### `app/main.py` - Point d'Entrée Principal
**Rôle** : Interface Gradio unifiée avec orchestration intégrée
```python
class EnhancedDocumentChatBot:
    """Application principale améliorée"""
    
    def __init__(self):
        self.chat_engine = EnhancedChatEngine()         # Moteur de conversation
        self.global_monitor = PerformanceMonitor()      # Monitoring global
        self.current_document = None                     # Document actuel
        self.document_processed = False                  # État traitement
        self.system_status = {}                          # Statut système
```

**Fonctions clés** :
- `process_document_enhanced()` : Traitement document avec monitoring
- `chat_enhanced()` : Conversation avec métadonnées enrichies
- `get_detailed_status()` : Statut système détaillé
- `export_session_data()` : Export complet de session

**Interface Gradio** :
- **Onglet Configuration** : Upload et paramétrage
- **Onglet Chat** : Conversation intelligente  
- **Onglet Monitoring** : Métriques et export
- **Onglet Orchestration** : Workflows Prefect

#### `app/config.py` - Configuration Centrale
**Rôle** : Centralisation de toutes les configurations système
```python
class Config:
    # Paramètres de base
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_K_DOCUMENTS = 3
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Chemins
    CHROMADB_PATH = "./data/vectorstore"
    UPLOAD_PATH = "./data/uploads"
    
    # Modèles IA
    MISTRAL_MODEL = "mistral-tiny"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Sécurité
    ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']
    MAX_TOKENS = 4000
```

#### `app/components/` - Composants Modulaires

##### `file_processor.py` - Traitement de Fichiers
**Rôle** : Extraction de texte depuis différents formats
```python
class FileProcessor:
    @staticmethod
    def process_uploaded_file(file_path):
        """Traite un fichier uploadé selon son type"""
        # Détection automatique du type MIME
        # Extraction spécialisée par format
        # Nettoyage et validation du texte
        
    @staticmethod  
    def extract_text_from_pdf(file_path):
        """Extraction PDF avec PyPDF2"""
        
    @staticmethod
    def extract_text_from_docx(file_path):
        """Extraction DOCX avec python-docx"""
```

##### `chat_engine.py` - Moteur de Conversation IA
**Rôle** : Orchestration de la conversation avec Mistral AI
```python
class EnhancedChatEngine:
    def __init__(self):
        self.llm = None                                 # LLM Mistral
        self.vectorstore_manager = EnhancedVectorStoreManager()
        self.memory = ConversationMemory()              # Historique
        self.prompt_manager = PromptTemplateManager()   # Templates
        self.performance_monitor = PerformanceMonitor() # Métriques
        
    def setup_llm(self, api_key, model="mistral-tiny"):
        """Configuration du LLM avec validation"""
        
    def process_document_smart(self, text, filename, chunk_size, template_type):
        """Traitement intelligent avec templates adaptatifs"""
        
    def chat_with_sources(self, question):
        """Conversation avec sources enrichies"""
```

##### `vectorstore.py` - Gestion Base Vectorielle
**Rôle** : Gestion de ChromaDB et embeddings
```python
class EnhancedVectorStoreManager:
    def __init__(self):
        self.embeddings = None                          # HuggingFace embeddings
        self.vectorstore = None                         # ChromaDB
        self.text_splitter = SmartTextSplitter()       # Découpage intelligent
        self.performance_monitor = PerformanceMonitor()
        
    def initialize_vectorstore(self):
        """Initialisation ChromaDB avec configuration optimisée"""
        
    def add_documents_enhanced(self, text, filename, chunk_size, chunk_overlap):
        """Ajout de documents avec métadonnées enrichies"""
        
    def similarity_search_with_details(self, query, k=3):
        """Recherche avec métadonnées détaillées"""
```

##### `memory.py` - Gestion de la Mémoire
**Rôle** : Historique et contexte conversationnel
```python
class ConversationMemory:
    def __init__(self, max_history=50):
        self.conversation_history = []
        self.max_history = max_history
        self.performance_history = []
        
    def add_exchange(self, question, answer, metadata):
        """Ajouter un échange avec métadonnées"""
        
    def get_relevant_context(self, current_question, max_context=3):
        """Récupérer le contexte pertinent"""
        
    def export_history(self):
        """Export complet de l'historique"""
```

##### `orchestration_manager.py` - Gestionnaire Prefect
**Rôle** : Interface avec l'API Prefect pour orchestration
```python
class OrchestrationManager:
    def __init__(self):
        self.prefect_available = PREFECT_AVAILABLE
        self.api_url = "http://localhost:4200/api"
        self.status_cache = {}
        
    async def get_prefect_status(self):
        """Récupérer le statut général de Prefect"""
        
    async def trigger_workflow(self, workflow_name, parameters):
        """Déclencher un workflow Prefect"""
        
    async def get_workflow_status(self, run_id):
        """Récupérer le statut d'un workflow spécifique"""
```

##### `prefect_bridge.py` - Pont Prefect
**Rôle** : Exécution directe de workflows sans serveur
```python
class PrefectBridge:
    def __init__(self):
        self.workflows_available = WORKFLOWS_AVAILABLE
        
    async def process_documents_batch(self, documents_folder, api_key):
        """Traiter des documents en lot via Prefect"""
        
    async def check_system_health(self, alert_threshold=70):
        """Vérifier la santé du système via Prefect"""
        
    def run_sync(self, coro):
        """Exécuter une coroutine de manière synchrone pour Gradio"""
```

#### `orchestration_interface.py` - Interface Orchestration
**Rôle** : Interface Gradio pour gestion des workflows
```python
class OrchestrationInterface:
    def __init__(self):
        self.manager = orchestration_manager
        self.current_runs = {}
        
    def refresh_status(self):
        """Actualiser le statut de Prefect"""
        
    def trigger_workflow_action(self, workflow_type, **kwargs):
        """Déclencher une action de workflow"""
        
    def create_orchestration_tab(self):
        """Créer l'onglet d'orchestration Prefect"""
```

###  **Dossier `utils/` - Utilitaires Avancés**

#### `validators.py` - Validation et Sécurité
**Rôle** : Validation complète des entrées utilisateur
```python
class FileValidator:
    @staticmethod
    def validate_file(file_obj):
        """Validation complète d'un fichier"""
        # Vérification taille, type MIME, contenu
        # Détection de malware potentiel
        # Validation encodage
        
    @staticmethod
    def check_file_safety(file_path):
        """Vérifications de sécurité avancées"""

class InputValidator:
    @staticmethod
    def validate_api_key(api_key, provider='mistral'):
        """Validation format clé API"""
        
    @staticmethod
    def sanitize_user_input(user_input):
        """Nettoyage et sécurisation input utilisateur"""
        
    @staticmethod
    def validate_question(question):
        """Validation d'une question utilisateur"""
```

#### `performance.py` - Monitoring de Performance
**Rôle** : Surveillance et métriques complètes
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
        self.system_stats = {}
        
    def measure_performance(self, operation_name):
        """Décorateur pour mesurer les performances"""
        
    def track_system_resources(self):
        """Surveillance des ressources système"""
        
    def get_performance_summary(self):
        """Résumé complet des performances"""
        
    def export_metrics(self, format='json'):
        """Export des métriques"""
```

#### `text_splitter.py` - Découpage Intelligent
**Rôle** : Découpage adaptatif selon le type de document
```python
class SmartTextSplitter:
    def __init__(self):
        self.document_patterns = {
            'academic': r'\n\d+\.\s+|\n[A-Z][A-Z\s]+\n',
            'legal': r'\n(?:Art\.|Article|Section)\s+\d+',
            'technical': r'\n\d+\.\d+\s+|\n#+\s+',
            'general': r'\n\n+'
        }
        
    def detect_document_type(self, text):
        """Détection automatique du type de document"""
        
    def split_text_smart(self, text, chunk_size, chunk_overlap, doc_type):
        """Découpage intelligent avec préservation de structure"""
        
    def extract_keywords(self, text, max_keywords=10):
        """Extraction de mots-clés contextuels"""
```

#### `prompt_templates.py` - Templates de Prompts
**Rôle** : Prompts optimisés par type de document
```python
class PromptTemplateManager:
    def __init__(self):
        self.templates = {
            'general': "...",
            'academic': "...", 
            'technical': "...",
            'legal': "...",
            'summary': "...",
            'extraction': "..."
        }
        
    def get_template(self, template_type):
        """Récupérer un template selon le type"""
        
    def auto_select_template(self, document_type, question_type):
        """Sélection automatique du meilleur template"""
        
    def customize_template(self, base_template, customizations):
        """Personnalisation de template"""
```

###  **Dossier `workflows/` - Orchestration Prefect**

#### `tasks.py` - Tâches Réutilisables
**Rôle** : Bibliothèque de tâches Prefect atomiques
```python
@task(name="process_single_document", retries=2, tags=["document", "processing"])
def process_single_document(file_path, api_key, chunk_size=None, template_type="auto"):
    """Traiter un document unique via Prefect"""
    
@task(name="test_document_query", tags=["testing", "query"])
def test_document_query(question, api_key, expected_keywords=None):
    """Tester une requête sur un document traité"""
    
@task(name="cleanup_old_data", tags=["maintenance", "cleanup"])
def cleanup_old_data(max_age_days=7, directories=None):
    """Nettoyer les fichiers anciens"""
    
@task(name="check_system_health", tags=["monitoring", "health"])
def check_system_health():
    """Effectuer une vérification de santé système"""
    
@task(name="generate_performance_report", tags=["monitoring", "report"])
def generate_performance_report(include_system_metrics=True):
    """Générer un rapport de performance complet"""
```

#### `batch_processing.py` - Traitement par Lots
**Rôle** : Workflows de traitement massif de documents
```python
@flow(name="batch_document_processing", task_runner=ConcurrentTaskRunner())
async def batch_document_flow(documents_folder, api_key, file_extensions=None):
    """Traiter plusieurs documents en parallèle"""
    
@flow(name="process_folder_documents")
async def process_folder_documents(input_folder, api_key, output_report=None):
    """Workflow complet pour traiter un dossier avec surveillance"""
    
@flow(name="nightly_batch_processing")
async def nightly_batch_processing(watch_folder="./data/inbox", api_key=None):
    """Workflow nocturne pour traitement automatisé"""
```

#### `maintenance.py` - Maintenance Automatisée
**Rôle** : Workflows de maintenance et optimisation
```python
@flow(name="database_maintenance")
async def database_maintenance_flow(vacuum_database=True, backup_database=True):
    """Workflow de maintenance de la base de données ChromaDB"""
    
@flow(name="cleanup_old_files", task_runner=ConcurrentTaskRunner())
async def cleanup_old_files_flow(max_age_days=7, dry_run=False):
    """Workflow de nettoyage des anciens fichiers"""
    
@flow(name="weekly_maintenance", task_runner=ConcurrentTaskRunner())
async def weekly_maintenance_flow(notification_email=None):
    """Workflow de maintenance hebdomadaire complète"""
```

#### `monitoring.py` - Surveillance Système
**Rôle** : Workflows de monitoring et alertes
```python
@flow(name="health_check_flow")
async def health_check_flow(alert_threshold=70, notification_email=None):
    """Workflow de surveillance de santé système"""
    
@flow(name="performance_monitoring_flow", task_runner=ConcurrentTaskRunner())
async def performance_monitoring_flow(generate_detailed_report=True):
    """Workflow de surveillance des performances"""
    
@flow(name="continuous_monitoring")
async def continuous_monitoring_flow(monitoring_duration_minutes=60):
    """Workflow de surveillance continue"""
```

#### `testing.py` - Tests Automatisés
**Rôle** : Workflows de validation et tests
```python
@flow(name="automated_testing_flow", task_runner=ConcurrentTaskRunner())
async def automated_testing_flow(api_key, test_documents_folder="./tests/documents"):
    """Workflow de tests automatisés complets"""
    
@flow(name="regression_testing")
async def regression_testing_flow(api_key, baseline_report_path=None):
    """Workflow de tests de régression"""
    
@flow(name="smoke_testing")
async def smoke_testing_flow(api_key):
    """Workflow de tests smoke (tests rapides de base)"""
```

#### `deployment.py` - Configuration Déploiement
**Rôle** : Configuration des déploiements Prefect
```python
# Déploiements avec planification automatique
nightly_processing_deployment = Deployment.build_from_flow(
    flow=nightly_batch_processing,
    name="nightly-document-processing",
    schedule=CronSchedule(cron="0 2 * * *"),  # 2h du matin
    parameters={"watch_folder": "./data/inbox"}
)

weekly_maintenance_deployment = Deployment.build_from_flow(
    flow=weekly_maintenance_flow,
    name="weekly-maintenance", 
    schedule=CronSchedule(cron="0 3 * * 0"),  # Dimanche 3h
)
```

###  **Dossier `scripts/` - Scripts d'Automatisation**

#### `setup_orchestration.py` - Configuration Automatique
**Rôle** : Installation et configuration complète automatisée
```python
def check_prefect_installation():
    """Vérifier si Prefect est installé"""
    
def install_prefect():
    """Installer Prefect et ses dépendances"""
    
def create_directories():
    """Créer les répertoires nécessaires"""
    
def create_test_documents():
    """Créer des documents de test pour les workflows"""
    
def setup_prefect_config():
    """Configurer Prefect"""
    
def test_workflows_import():
    """Tester l'import des workflows"""
```

#### `start_prefect.sh` - Démarrage Prefect
**Rôle** : Script bash pour démarrage automatique
```bash
#!/bin/bash
# Vérification prérequis
# Création répertoires
# Configuration base de données
# Démarrage serveur + workers
# Déploiement workflows
# Validation santé
```

#### `stop_prefect.sh` - Arrêt Prefect
**Rôle** : Script bash pour arrêt propre
```bash
#!/bin/bash
# Arrêt workers
# Arrêt serveur
# Nettoyage processus
# Libération ports
```

###  **Dossier `data/` - Stockage et Données**

#### Structure de Stockage
```
data/
├── uploads/              # Fichiers temporaires uploadés
├── vectorstore/          # Base ChromaDB persistante
│   ├── chroma.sqlite3    # Base SQLite ChromaDB
│   └── collections/      # Collections vectorielles
├── inbox/                # Documents pour traitement automatique
├── exports/              # Exports de sessions
├── backups/              # Sauvegardes automatiques
│   ├── chromadb/         # Backups base vectorielle
│   └── configs/          # Backups configuration
├── reports/              # Rapports de performance
├── monitoring/           # Historique surveillance
├── workflow_results/     # Résultats workflows Prefect
└── prefect_storage/      # Artefacts Prefect
```

##  Flux de Données Détaillés

### 1. **Traitement de Document**
```
User Upload → FileValidator → FileProcessor → TextSplitter → 
EnhancedVectorStore → ChromaDB → Success Feedback
```

### 2. **Conversation Intelligente**
```
User Question → InputValidator → VectorStore Search → 
Context Retrieval → PromptTemplate → Mistral API → 
Response + Sources → ConversationMemory → UI Display
```

### 3. **Orchestration Workflow**
```
User Action → OrchestrationInterface → PrefectBridge → 
Workflow Execution → Status Monitoring → Results Display
```

### 4. **Monitoring Continu**
```
System Metrics → PerformanceMonitor → Health Calculation → 
Alert Evaluation → Notification Trigger → Dashboard Update
```

##  Points d'Extension

### Ajouter un Nouveau Format de Document
1. **Étendre FileProcessor**
```python
@staticmethod
def extract_text_from_pptx(file_path):
    """Extraction PowerPoint avec python-pptx"""
    # Implémentation extraction
```

2. **Mettre à jour Config**
```python
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.pptx']
```

3. **Ajouter Pattern TextSplitter**
```python
'presentation': r'\nSlide \d+|\n(?:Titre|Title):'
```

### Ajouter un Nouveau Template
1. **Définir dans PromptTemplateManager**
```python
'custom_domain': """
Tu es un expert en [DOMAINE].
Contexte: {context}
Question: {question}
Réponds avec l'expertise spécialisée...
"""
```

2. **Implémenter Détection Automatique**
```python
def detect_custom_domain(self, text):
    domain_keywords = ['keyword1', 'keyword2']
    # Logique de détection
```

### Ajouter un Nouveau Workflow
1. **Créer le Flow**
```python
@flow(name="custom_workflow")
async def custom_workflow_flow(param1, param2):
    """Workflow personnalisé"""
    # Logique métier
    return results
```

2. **Ajouter au PrefectBridge**
```python
async def trigger_custom_workflow(self, param1, param2):
    return await self.trigger_workflow("custom-workflow", {
        "param1": param1, "param2": param2
    })
```

3. **Intégrer à l'Interface**
```python
# Dans OrchestrationInterface
custom_btn = gr.Button(" Custom Workflow")
custom_btn.click(
    fn=prefect_bridge.custom_workflow_sync,
    inputs=[param1_input, param2_input],
    outputs=[result_output]
)
```

##  Debugging et Développement

### Variables d'Environnement de Debug
```bash
export DEBUG_MODE="true"
export LOG_LEVEL="DEBUG"
export DISABLE_EMBEDDINGS="true"  # Pour tests sans TensorFlow
export MOCK_MISTRAL_API="true"    # Pour tests sans API
```

### Points de Debug Importants
1. **Performance Monitor** : Toutes les opérations sont tracées
2. **Logging Centralisé** : `logs/` avec rotation automatique
3. **Health Checks** : Surveillance continue des composants
4. **Exception Handling** : Gestion gracieuse des erreurs

### Tests de Composants
```python
# Test d'un composant isolé
from app.components.text_splitter import SmartTextSplitter
splitter = SmartTextSplitter()
result = splitter.split_text_smart(text, 1000, 200, "academic")

# Test d'un workflow
from workflows.tasks import check_system_health
health = check_system_health()
```

##  Déploiement en Production

### Configuration Production
```python
# app/config.py
class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "INFO"
    MAX_WORKERS = 6
    EMBEDDING_MODEL = "all-mpnet-base-v2"  # Plus performant
    CHROMADB_PATH = "/var/lib/dontreadme/vectorstore"
```

### Variables d'Environnement Production
```bash
export FLASK_ENV="production"
export PREFECT_API_URL="https://your-prefect-server.com/api"
export NOTIFICATION_EMAIL="admin@yourcompany.com"
export ALERT_THRESHOLD="80"
export BACKUP_RETENTION_DAYS="30"
```

### Monitoring Production
- **Logs** : Centralisés avec ELK Stack
- **Métriques** : Prometheus + Grafana
- **Alertes** : PagerDuty/Slack integration
- **Health Checks** : Kubernetes liveness/readiness probes

##  Checklist Développement

### Avant Modification
- [ ] Lire cette documentation complètement
- [ ] Comprendre l'architecture modulaire
- [ ] Identifier les points d'impact
- [ ] Créer une branche de développement

### Pendant Développement
- [ ] Suivre les patterns existants
- [ ] Ajouter tests unitaires appropriés
- [ ] Documenter les nouvelles fonctions
- [ ] Utiliser le PerformanceMonitor
- [ ] Gérer les erreurs gracieusement

### Après Modification
- [ ] Tester en isolation
- [ ] Tester l'intégration complète
- [ ] Vérifier les performances
- [ ] Mettre à jour la documentation
- [ ] Créer une Pull Request

---

##  Conclusion Technique

DontREADME est conçu avec une **architecture modulaire et extensible** qui permet :

[OK] **Facilité de maintenance** : Composants isolés et responsabilités claires
[OK] **Extensibilité** : Points d'extension bien définis
[OK] **Observabilité** : Monitoring et logging complets
[OK] **Robustesse** : Gestion d'erreurs et fallbacks
[OK] **Performance** : Optimisations et mise en cache

Le système est prêt pour la production et peut évoluer selon vos besoins spécifiques !

---

*Guide développeur DontREADME - Version 1.0*  
*Développé avec  et Claude Sonnet 4*