"""
Configuration de déploiement Prefect pour DontREADME
"""

from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from prefect.client.schemas.schedules import IntervalSchedule
from datetime import timedelta

from .batch_processing import nightly_batch_processing
from .maintenance import weekly_maintenance_flow, database_maintenance_flow
from .monitoring import health_check_flow, continuous_monitoring_flow
from .testing import smoke_testing_flow, automated_testing_flow

# Déploiement pour le traitement nocturne
nightly_processing_deployment = Deployment.build_from_flow(
    flow=nightly_batch_processing,
    name="nightly-document-processing",
    schedule=CronSchedule(cron="0 2 * * *"),  # Tous les jours à 2h du matin
    work_pool_name="default-agent-pool",
    description="Traitement automatique nocturne des nouveaux documents",
    parameters={
        "watch_folder": "./data/inbox",
        "api_key": None  # Sera récupérée depuis les variables d'environnement
    },
    tags=["automation", "nightly", "batch-processing"]
)

# Déploiement pour la maintenance hebdomadaire
weekly_maintenance_deployment = Deployment.build_from_flow(
    flow=weekly_maintenance_flow,
    name="weekly-maintenance",
    schedule=CronSchedule(cron="0 3 * * 0"),  # Dimanche à 3h du matin
    work_pool_name="default-agent-pool",
    description="Maintenance hebdomadaire complète du système",
    parameters={
        "notification_email": None  # À configurer selon les besoins
    },
    tags=["maintenance", "weekly", "cleanup"]
)

# Déploiement pour la surveillance continue
health_monitoring_deployment = Deployment.build_from_flow(
    flow=health_check_flow,
    name="health-monitoring",
    schedule=IntervalSchedule(interval=timedelta(minutes=15)),  # Toutes les 15 minutes
    work_pool_name="default-agent-pool",
    description="Surveillance continue de la santé du système",
    parameters={
        "alert_threshold": 70,
        "notification_email": None
    },
    tags=["monitoring", "health", "alerts"]
)

# Déploiement pour les tests smoke quotidiens
daily_smoke_tests_deployment = Deployment.build_from_flow(
    flow=smoke_testing_flow,
    name="daily-smoke-tests",
    schedule=CronSchedule(cron="0 6 * * *"),  # Tous les jours à 6h du matin
    work_pool_name="default-agent-pool",
    description="Tests smoke quotidiens pour vérifier le bon fonctionnement",
    parameters={
        "api_key": None  # Sera récupérée depuis les variables d'environnement
    },
    tags=["testing", "daily", "smoke"]
)

# Déploiement pour la maintenance de base de données (deux fois par semaine)
database_maintenance_deployment = Deployment.build_from_flow(
    flow=database_maintenance_flow,
    name="database-maintenance",
    schedule=CronSchedule(cron="0 1 * * 2,5"),  # Mardi et vendredi à 1h du matin
    work_pool_name="default-agent-pool",
    description="Maintenance de la base de données ChromaDB",
    parameters={
        "vacuum_database": True,
        "backup_database": True,
        "optimize_collections": True
    },
    tags=["maintenance", "database", "chromadb"]
)

# Déploiement pour les tests complets (hebdomadaire)
weekly_full_tests_deployment = Deployment.build_from_flow(
    flow=automated_testing_flow,
    name="weekly-full-tests",
    schedule=CronSchedule(cron="0 4 * * 6"),  # Samedi à 4h du matin
    work_pool_name="default-agent-pool",
    description="Tests automatisés complets hebdomadaires",
    parameters={
        "api_key": None,
        "test_documents_folder": "./tests/documents",
        "generate_test_report": True
    },
    tags=["testing", "weekly", "comprehensive"]
)

# Liste de tous les déploiements
ALL_DEPLOYMENTS = [
    nightly_processing_deployment,
    weekly_maintenance_deployment,
    health_monitoring_deployment,
    daily_smoke_tests_deployment,
    database_maintenance_deployment,
    weekly_full_tests_deployment
]

def deploy_all():
    """Déployer tous les workflows Prefect"""
    for deployment in ALL_DEPLOYMENTS:
        print(f"Déploiement de {deployment.name}...")
        deployment.apply()
        print(f"✅ {deployment.name} déployé avec succès")

if __name__ == "__main__":
    deploy_all()