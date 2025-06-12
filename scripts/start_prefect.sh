#!/bin/bash

# Script de démarrage Prefect pour DontREADME
# Ce script lance le serveur Prefect et configure les workflows

set -e

echo "🚀 Démarrage de Prefect pour DontREADME"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour logger avec couleur
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Vérifier que Prefect est installé
if ! command -v prefect &> /dev/null; then
    error "Prefect n'est pas installé. Installez-le avec: pip install prefect>=2.14.0"
    exit 1
fi

log "Prefect est installé - version: $(prefect version)"

# Créer les répertoires nécessaires
log "Création des répertoires nécessaires..."
mkdir -p data/prefect_storage
mkdir -p data/inbox
mkdir -p data/reports
mkdir -p data/backups
mkdir -p data/monitoring
mkdir -p tests/documents
mkdir -p logs

# Définir la base de données Prefect (SQLite local)
export PREFECT_API_DATABASE_CONNECTION_URL="sqlite+aiosqlite:///$(pwd)/data/prefect.db"

log "Configuration de la base de données Prefect: $(pwd)/data/prefect.db"

# Vérifier si le serveur Prefect est déjà en cours d'exécution
if pgrep -f "prefect server start" > /dev/null; then
    warn "Un serveur Prefect semble déjà en cours d'exécution"
    read -p "Voulez-vous le redémarrer? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Arrêt du serveur existant..."
        pkill -f "prefect server start" || true
        sleep 2
    else
        log "Utilisation du serveur existant"
        export PREFECT_API_URL="http://localhost:4200/api"
        prefect config set PREFECT_API_URL="http://localhost:4200/api"
    fi
fi

# Démarrer le serveur Prefect en arrière-plan si nécessaire
if ! curl -s http://localhost:4200/api/health > /dev/null 2>&1; then
    log "Démarrage du serveur Prefect..."
    
    # Démarrer le serveur en arrière-plan
    nohup prefect server start --host 0.0.0.0 --port 4200 > logs/prefect_server.log 2>&1 &
    SERVER_PID=$!
    
    # Attendre que le serveur soit prêt
    log "Attente du démarrage du serveur..."
    for i in {1..30}; do
        if curl -s http://localhost:4200/api/health > /dev/null 2>&1; then
            log "✅ Serveur Prefect démarré avec succès (PID: $SERVER_PID)"
            break
        fi
        if [ $i -eq 30 ]; then
            error "Échec du démarrage du serveur Prefect après 30 secondes"
            exit 1
        fi
        sleep 1
    done
else
    log "✅ Serveur Prefect déjà en cours d'exécution"
fi

# Configurer l'URL de l'API
export PREFECT_API_URL="http://localhost:4200/api"
prefect config set PREFECT_API_URL="http://localhost:4200/api"

log "Configuration de l'API URL: $PREFECT_API_URL"

# Créer le pool de workers par défaut si nécessaire
log "Configuration du pool de workers..."
if ! prefect work-pool ls | grep -q "default-agent-pool"; then
    log "Création du pool de workers par défaut..."
    prefect work-pool create default-agent-pool --type process
else
    log "✅ Pool de workers 'default-agent-pool' déjà existant"
fi

# Vérifier la clé API Mistral
if [ -z "$MISTRAL_API_KEY" ]; then
    warn "Variable d'environnement MISTRAL_API_KEY non définie"
    echo "Pour utiliser les workflows automatisés, définissez votre clé API:"
    echo "export MISTRAL_API_KEY='votre_cle_api_ici'"
else
    log "✅ Clé API Mistral configurée"
fi

# Déployer les workflows
log "Déploiement des workflows..."
if [ -f "workflows/deployment.py" ]; then
    python -c "
import sys
sys.path.append('.')
from workflows.deployment import deploy_all
try:
    deploy_all()
    print('✅ Tous les workflows ont été déployés avec succès')
except Exception as e:
    print(f'❌ Erreur lors du déploiement: {e}')
    sys.exit(1)
"
else
    warn "Fichier de déploiement non trouvé, déploiement manuel nécessaire"
fi

# Démarrer un agent worker en arrière-plan
log "Démarrage de l'agent worker..."
nohup prefect worker start --pool default-agent-pool > logs/prefect_worker.log 2>&1 &
WORKER_PID=$!

# Attendre un peu pour que l'agent se connecte
sleep 3

# Vérifier que l'agent est connecté
if ps -p $WORKER_PID > /dev/null; then
    log "✅ Agent worker démarré avec succès (PID: $WORKER_PID)"
else
    error "Échec du démarrage de l'agent worker"
fi

# Afficher les informations importantes
echo
echo "🎉 Prefect pour DontREADME est maintenant configuré et en cours d'exécution!"
echo
echo "📊 Interface Web Prefect: http://localhost:4200"
echo "🔧 API Prefect: http://localhost:4200/api"
echo "📁 Base de données: $(pwd)/data/prefect.db"
echo "📋 Logs serveur: $(pwd)/logs/prefect_server.log"
echo "👷 Logs worker: $(pwd)/logs/prefect_worker.log"
echo

# Afficher les processus en cours
echo "🔍 Processus Prefect en cours:"
pgrep -f "prefect" | while read pid; do
    echo "  - PID $pid: $(ps -p $pid -o comm= 2>/dev/null || echo 'processus terminé')"
done

echo
echo "📅 Workflows programmés:"
prefect deployment ls 2>/dev/null || echo "  Aucun déploiement trouvé (normal si c'est la première exécution)"

echo
echo "🛠️ Commandes utiles:"
echo "  - Voir les flows: prefect flow ls"
echo "  - Voir les déploiements: prefect deployment ls"
echo "  - Voir les runs: prefect flow-run ls"
echo "  - Arrêter Prefect: ./scripts/stop_prefect.sh"
echo "  - Logs en temps réel: tail -f logs/prefect_*.log"

echo
log "✅ Configuration terminée! Vous pouvez maintenant accéder à l'interface web."

# Optionnel: ouvrir l'interface web automatiquement
if command -v open &> /dev/null; then
    read -p "Voulez-vous ouvrir l'interface web Prefect? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:4200
    fi
fi