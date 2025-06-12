#!/bin/bash

# Script d'arrêt Prefect pour DontREADME
# Ce script arrête proprement le serveur Prefect et les workers

set -e

echo "🛑 Arrêt de Prefect pour DontREADME"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Fonction pour arrêter un processus proprement
stop_process() {
    local process_name=$1
    local pids=$(pgrep -f "$process_name" || true)
    
    if [ -n "$pids" ]; then
        log "Arrêt des processus $process_name..."
        echo "$pids" | while read pid; do
            if [ -n "$pid" ]; then
                log "Arrêt du processus $pid..."
                kill -TERM "$pid" 2>/dev/null || true
                
                # Attendre que le processus se termine proprement
                for i in {1..10}; do
                    if ! ps -p "$pid" > /dev/null 2>&1; then
                        log "✅ Processus $pid arrêté proprement"
                        break
                    fi
                    if [ $i -eq 10 ]; then
                        warn "Forçage de l'arrêt du processus $pid..."
                        kill -KILL "$pid" 2>/dev/null || true
                    fi
                    sleep 1
                done
            fi
        done
    else
        log "Aucun processus $process_name trouvé"
    fi
}

# Afficher l'état actuel
echo "🔍 État actuel des processus Prefect:"
pgrep -f "prefect" | while read pid; do
    echo "  - PID $pid: $(ps -p $pid -o args= 2>/dev/null || echo 'processus non trouvé')"
done || echo "  Aucun processus Prefect trouvé"

echo

# Arrêter les workers en premier
log "Arrêt des workers Prefect..."
stop_process "prefect worker"

# Attendre un peu
sleep 2

# Arrêter le serveur Prefect
log "Arrêt du serveur Prefect..."
stop_process "prefect server"

# Vérifier qu'il ne reste plus de processus Prefect
remaining_processes=$(pgrep -f "prefect" || true)
if [ -n "$remaining_processes" ]; then
    warn "Des processus Prefect sont encore en cours d'exécution:"
    echo "$remaining_processes" | while read pid; do
        echo "  - PID $pid: $(ps -p $pid -o args= 2>/dev/null || echo 'processus non trouvé')"
    done
    
    read -p "Voulez-vous forcer l'arrêt de tous les processus Prefect? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Arrêt forcé de tous les processus Prefect..."
        pkill -KILL -f "prefect" 2>/dev/null || true
        sleep 1
    fi
fi

# Vérification finale
remaining_processes=$(pgrep -f "prefect" || true)
if [ -z "$remaining_processes" ]; then
    log "✅ Tous les processus Prefect ont été arrêtés"
else
    error "Certains processus Prefect sont encore actifs"
    echo "$remaining_processes" | while read pid; do
        echo "  - PID $pid: $(ps -p $pid -o args= 2>/dev/null || echo 'processus non trouvé')"
    done
fi

# Vérifier que les ports sont libérés
if lsof -i :4200 > /dev/null 2>&1; then
    warn "Le port 4200 est encore occupé"
else
    log "✅ Port 4200 libéré"
fi

# Nettoyer les fichiers de verrous si nécessaire
if [ -f ".prefect_server.pid" ]; then
    log "Suppression du fichier de verrou serveur..."
    rm -f .prefect_server.pid
fi

if [ -f ".prefect_worker.pid" ]; then
    log "Suppression du fichier de verrou worker..."
    rm -f .prefect_worker.pid
fi

# Afficher un résumé
echo
echo "📊 Résumé de l'arrêt:"
echo "  🛑 Serveur Prefect: Arrêté"
echo "  👷 Workers: Arrêtés"
echo "  🌐 Port 4200: Libéré"

# Informations sur les données persistantes
echo
echo "💾 Données conservées:"
echo "  📁 Base de données: $(pwd)/data/prefect.db"
echo "  📋 Logs: $(pwd)/logs/"
echo "  🗄️ Stockage: $(pwd)/data/prefect_storage/"

echo
echo "🔄 Pour redémarrer Prefect:"
echo "  ./scripts/start_prefect.sh"

echo
log "✅ Arrêt de Prefect terminé!"