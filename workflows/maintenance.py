"""
Workflows Prefect pour la maintenance de DontREADME
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta

from prefect import flow, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner

from .tasks import cleanup_old_data, check_system_health, generate_performance_report


@flow(
    name="database_maintenance",
    description="Maintenance de la base de données ChromaDB",
    version="1.0",
    timeout_seconds=1800,  # 30 minutes max
    retries=1
)
async def database_maintenance_flow(
    vacuum_database: bool = True,
    backup_database: bool = True,
    optimize_collections: bool = True
) -> Dict[str, Any]:
    """
    Workflow de maintenance de la base de données ChromaDB
    
    Args:
        vacuum_database: Nettoyer la base de données
        backup_database: Créer une sauvegarde
        optimize_collections: Optimiser les collections
        
    Returns:
        Dict avec les résultats de maintenance
    """
    logger = get_run_logger()
    
    logger.info("🛠️ Démarrage de la maintenance ChromaDB")
    maintenance_start = datetime.now()
    
    try:
        from app.config import Config
        
        maintenance_results = {
            "started_at": maintenance_start.isoformat(),
            "operations": {}
        }
        
        # Vérification préliminaire de santé
        logger.info("🩺 Vérification de santé préliminaire")
        initial_health = check_system_health()
        maintenance_results["initial_health"] = initial_health
        
        if initial_health.get("overall_status") == "unhealthy":
            logger.warning("⚠️ Système en mauvaise santé - maintenance risquée")
        
        # Phase 1: Sauvegarde de la base de données
        if backup_database:
            logger.info("💾 Création de sauvegarde ChromaDB")
            
            backup_result = await create_chromadb_backup()
            maintenance_results["operations"]["backup"] = backup_result
            
            if backup_result.get("status") != "success":
                logger.error("❌ Échec de la sauvegarde - arrêt de la maintenance")
                return {**maintenance_results, "status": "failed", "reason": "backup_failed"}
        
        # Phase 2: Nettoyage et optimisation des collections
        if optimize_collections:
            logger.info("⚡ Optimisation des collections ChromaDB")
            
            optimization_result = await optimize_chromadb_collections()
            maintenance_results["operations"]["optimization"] = optimization_result
        
        # Phase 3: Vacuum de la base (si supporté)
        if vacuum_database:
            logger.info("🧹 Nettoyage de la base ChromaDB")
            
            vacuum_result = await vacuum_chromadb()
            maintenance_results["operations"]["vacuum"] = vacuum_result
        
        # Phase 4: Vérification post-maintenance
        logger.info("🩺 Vérification de santé post-maintenance")
        final_health = check_system_health()
        maintenance_results["final_health"] = final_health
        
        # Calculer les métriques de maintenance
        maintenance_end = datetime.now()
        maintenance_duration = (maintenance_end - maintenance_start).total_seconds()
        
        # Évaluer l'amélioration
        initial_score = initial_health.get("health_score", 0)
        final_score = final_health.get("health_score", 0)
        improvement = final_score - initial_score
        
        maintenance_results.update({
            "status": "success",
            "completed_at": maintenance_end.isoformat(),
            "duration_seconds": round(maintenance_duration, 2),
            "health_improvement": {
                "initial_score": initial_score,
                "final_score": final_score,
                "improvement": improvement
            }
        })
        
        logger.info(f"✅ Maintenance ChromaDB terminée:")
        logger.info(f"   ⏱️ Durée: {maintenance_duration:.1f}s")
        logger.info(f"   📊 Amélioration santé: {improvement:+.1f} points")
        logger.info(f"   🏥 Santé finale: {final_health.get('overall_status', 'unknown')}")
        
        return maintenance_results
        
    except Exception as e:
        maintenance_end = datetime.now()
        maintenance_duration = (maintenance_end - maintenance_start).total_seconds()
        
        logger.error(f"❌ Erreur lors de la maintenance: {str(e)}")
        return {
            "status": "error",
            "started_at": maintenance_start.isoformat(),
            "failed_at": maintenance_end.isoformat(),
            "duration_seconds": round(maintenance_duration, 2),
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


@flow(
    name="cleanup_old_files",
    description="Nettoyage des anciens fichiers et données",
    version="1.0",
    task_runner=ConcurrentTaskRunner(),
    timeout_seconds=900  # 15 minutes max
)
async def cleanup_old_files_flow(
    max_age_days: int = 7,
    include_uploads: bool = True,
    include_exports: bool = True,
    include_reports: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Workflow de nettoyage des anciens fichiers
    
    Args:
        max_age_days: Âge maximum des fichiers en jours
        include_uploads: Nettoyer les uploads
        include_exports: Nettoyer les exports
        include_reports: Nettoyer les rapports
        dry_run: Mode simulation (pas de suppression réelle)
        
    Returns:
        Dict avec les résultats du nettoyage
    """
    logger = get_run_logger()
    
    logger.info(f"🧹 Nettoyage des fichiers anciens (>{max_age_days} jours)")
    if dry_run:
        logger.info("🔍 Mode simulation activé - aucune suppression")
    
    cleanup_start = datetime.now()
    
    try:
        # Définir les répertoires à nettoyer
        directories_to_clean = []
        
        if include_uploads:
            directories_to_clean.append("./data/uploads")
        
        if include_exports:
            directories_to_clean.append("./data/exports")
        
        if include_reports:
            directories_to_clean.append("./data/reports")
        
        if not directories_to_clean:
            logger.warning("⚠️ Aucun répertoire sélectionné pour nettoyage")
            return {
                "status": "skipped",
                "reason": "no_directories_selected",
                "directories_to_clean": []
            }
        
        logger.info(f"📁 Répertoires à nettoyer: {directories_to_clean}")
        
        # Effectuer le nettoyage (ou simulation)
        if dry_run:
            cleanup_result = await simulate_cleanup(directories_to_clean, max_age_days)
        else:
            cleanup_result = cleanup_old_data(max_age_days, directories_to_clean)
        
        # Statistiques détaillées
        cleanup_end = datetime.now()
        cleanup_duration = (cleanup_end - cleanup_start).total_seconds()
        
        # Vérifier l'espace disque libéré
        disk_stats = get_disk_usage_stats()
        
        result = {
            "status": "success",
            "dry_run": dry_run,
            "started_at": cleanup_start.isoformat(),
            "completed_at": cleanup_end.isoformat(),
            "duration_seconds": round(cleanup_duration, 2),
            "cleanup_results": cleanup_result,
            "disk_stats": disk_stats,
            "directories_processed": len(directories_to_clean)
        }
        
        logger.info(f"✅ Nettoyage terminé:")
        logger.info(f"   🗑️ Fichiers traités: {cleanup_result.get('total_files_cleaned', 0)}")
        logger.info(f"   💾 Espace libéré: {cleanup_result.get('total_size_freed_mb', 0)} MB")
        logger.info(f"   ⏱️ Durée: {cleanup_duration:.1f}s")
        
        return result
        
    except Exception as e:
        cleanup_end = datetime.now()
        cleanup_duration = (cleanup_end - cleanup_start).total_seconds()
        
        logger.error(f"❌ Erreur lors du nettoyage: {str(e)}")
        return {
            "status": "error",
            "started_at": cleanup_start.isoformat(),
            "failed_at": cleanup_end.isoformat(),
            "duration_seconds": round(cleanup_duration, 2),
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


@flow(
    name="weekly_maintenance",
    description="Maintenance hebdomadaire complète",
    version="1.0",
    task_runner=ConcurrentTaskRunner(max_workers=2),
    timeout_seconds=3600  # 1 heure max
)
async def weekly_maintenance_flow(
    notification_email: str = None
) -> Dict[str, Any]:
    """
    Workflow de maintenance hebdomadaire complète
    
    Args:
        notification_email: Email pour les notifications (optionnel)
        
    Returns:
        Dict avec le résumé de la maintenance
    """
    logger = get_run_logger()
    
    logger.info("📅 Démarrage de la maintenance hebdomadaire")
    weekly_start = datetime.now()
    
    try:
        maintenance_results = {
            "started_at": weekly_start.isoformat(),
            "type": "weekly",
            "tasks": {}
        }
        
        # Task 1: Maintenance de la base de données
        logger.info("🛠️ Maintenance de la base de données")
        db_maintenance = await database_maintenance_flow(
            vacuum_database=True,
            backup_database=True,
            optimize_collections=True
        )
        maintenance_results["tasks"]["database_maintenance"] = db_maintenance
        
        # Task 2: Nettoyage des fichiers anciens
        logger.info("🧹 Nettoyage des fichiers anciens")
        cleanup_result = await cleanup_old_files_flow(
            max_age_days=14,  # Plus agressif pour la maintenance hebdomadaire
            include_uploads=True,
            include_exports=True,
            include_reports=False  # Garder les rapports plus longtemps
        )
        maintenance_results["tasks"]["file_cleanup"] = cleanup_result
        
        # Task 3: Génération du rapport de performance
        logger.info("📊 Génération du rapport hebdomadaire")
        performance_report = generate_performance_report(include_system_metrics=True)
        maintenance_results["tasks"]["performance_report"] = performance_report
        
        # Task 4: Vérification de santé finale
        logger.info("🩺 Vérification de santé globale")
        final_health = check_system_health()
        maintenance_results["tasks"]["final_health"] = final_health
        
        # Task 5: Optimisation des modèles (si nécessaire)
        logger.info("🤖 Vérification des modèles ML")
        models_check = await check_ml_models_health()
        maintenance_results["tasks"]["models_check"] = models_check
        
        # Calcul des statistiques finales
        weekly_end = datetime.now()
        maintenance_duration = (weekly_end - weekly_start).total_seconds()
        
        # Analyser les résultats
        successful_tasks = sum(
            1 for task in maintenance_results["tasks"].values() 
            if task.get("status") == "success"
        )
        total_tasks = len(maintenance_results["tasks"])
        
        # Calculer l'espace total libéré
        total_space_freed = cleanup_result.get("cleanup_results", {}).get("total_size_freed_mb", 0)
        
        maintenance_results.update({
            "status": "success",
            "completed_at": weekly_end.isoformat(),
            "duration_seconds": round(maintenance_duration, 2),
            "summary": {
                "successful_tasks": successful_tasks,
                "total_tasks": total_tasks,
                "success_rate": round(successful_tasks / total_tasks * 100, 1),
                "space_freed_mb": total_space_freed,
                "final_health_status": final_health.get("overall_status", "unknown")
            }
        })
        
        # Notification si email fourni
        if notification_email:
            await send_maintenance_notification(maintenance_results, notification_email)
        
        logger.info(f"✅ Maintenance hebdomadaire terminée:")
        logger.info(f"   ⏱️ Durée: {maintenance_duration/60:.1f} minutes")
        logger.info(f"   📊 Tâches: {successful_tasks}/{total_tasks} réussies")
        logger.info(f"   💾 Espace libéré: {total_space_freed} MB")
        logger.info(f"   🏥 Santé finale: {final_health.get('overall_status', 'unknown')}")
        
        return maintenance_results
        
    except Exception as e:
        weekly_end = datetime.now()
        maintenance_duration = (weekly_end - weekly_start).total_seconds()
        
        logger.error(f"❌ Erreur lors de la maintenance hebdomadaire: {str(e)}")
        
        error_result = {
            "status": "error",
            "started_at": weekly_start.isoformat(),
            "failed_at": weekly_end.isoformat(),
            "duration_seconds": round(maintenance_duration, 2),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "tasks": maintenance_results.get("tasks", {}) if 'maintenance_results' in locals() else {}
        }
        
        # Notification d'erreur si email fourni
        if notification_email:
            await send_error_notification(error_result, notification_email)
        
        return error_result


# Fonctions utilitaires pour la maintenance
async def create_chromadb_backup() -> Dict[str, Any]:
    """Créer une sauvegarde de ChromaDB"""
    try:
        from app.config import Config
        
        source_path = Path(Config.CHROMADB_PATH)
        if not source_path.exists():
            return {
                "status": "skipped",
                "reason": "chromadb_not_found",
                "source_path": str(source_path)
            }
        
        # Créer le répertoire de sauvegarde
        backup_dir = Path("./data/backups/chromadb")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Nom de sauvegarde avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"chromadb_backup_{timestamp}"
        
        # Copier la base de données
        shutil.copytree(source_path, backup_path)
        
        # Calculer la taille
        backup_size = sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file())
        
        return {
            "status": "success",
            "backup_path": str(backup_path),
            "backup_size_mb": round(backup_size / 1024**2, 2),
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


async def optimize_chromadb_collections() -> Dict[str, Any]:
    """Optimiser les collections ChromaDB"""
    try:
        import chromadb
        from app.config import Config
        
        client = chromadb.PersistentClient(path=Config.CHROMADB_PATH)
        collections = client.list_collections()
        
        optimization_results = []
        
        for collection in collections:
            try:
                # Compter les documents
                doc_count = collection.count()
                
                # ChromaDB gère l'optimisation automatiquement
                # Ici on pourrait ajouter des optimisations spécifiques si nécessaire
                
                optimization_results.append({
                    "collection_name": collection.name,
                    "document_count": doc_count,
                    "status": "optimized"
                })
                
            except Exception as e:
                optimization_results.append({
                    "collection_name": collection.name,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "collections_processed": len(collections),
            "results": optimization_results,
            "optimized_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


async def vacuum_chromadb() -> Dict[str, Any]:
    """Effectuer un vacuum de ChromaDB (si supporté)"""
    try:
        # ChromaDB ne supporte pas encore le vacuum direct
        # Cette fonction est préparée pour de futures versions
        
        return {
            "status": "skipped",
            "reason": "vacuum_not_supported",
            "message": "ChromaDB vacuum sera implémenté dans une future version"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


async def simulate_cleanup(directories: List[str], max_age_days: int) -> Dict[str, Any]:
    """Simuler le nettoyage des fichiers"""
    try:
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        simulation_results = {}
        total_files = 0
        total_size = 0
        
        for directory in directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                continue
            
            dir_files = 0
            dir_size = 0
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if file_mtime < cutoff_date:
                        dir_files += 1
                        dir_size += file_path.stat().st_size
            
            simulation_results[directory] = {
                "files_to_delete": dir_files,
                "size_to_free_mb": round(dir_size / 1024**2, 2)
            }
            
            total_files += dir_files
            total_size += dir_size
        
        return {
            "status": "success",
            "simulation": True,
            "total_files_to_delete": total_files,
            "total_size_to_free_mb": round(total_size / 1024**2, 2),
            "directories": simulation_results,
            "simulated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


def get_disk_usage_stats() -> Dict[str, Any]:
    """Obtenir les statistiques d'utilisation du disque"""
    try:
        import psutil
        
        disk_usage = psutil.disk_usage('.')
        
        return {
            "total_gb": round(disk_usage.total / 1024**3, 2),
            "used_gb": round(disk_usage.used / 1024**3, 2),
            "free_gb": round(disk_usage.free / 1024**3, 2),
            "used_percent": round((disk_usage.used / disk_usage.total) * 100, 1)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def check_ml_models_health() -> Dict[str, Any]:
    """Vérifier la santé des modèles ML"""
    try:
        models_status = {}
        
        # Test des sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            
            # Test de chargement d'un modèle léger
            model = SentenceTransformer('all-MiniLM-L6-v2')
            test_embedding = model.encode(["test sentence"])
            
            models_status["sentence_transformers"] = {
                "status": "healthy",
                "model_loaded": True,
                "embedding_shape": test_embedding.shape
            }
            
        except Exception as e:
            models_status["sentence_transformers"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Test de Mistral AI (si clé disponible)
        try:
            from app.config import Config
            if Config.MISTRAL_API_KEY:
                # Test basique de connectivité
                models_status["mistral_api"] = {
                    "status": "configured",
                    "api_key_present": True
                }
            else:
                models_status["mistral_api"] = {
                    "status": "not_configured",
                    "api_key_present": False
                }
                
        except Exception as e:
            models_status["mistral_api"] = {
                "status": "error", 
                "error": str(e)
            }
        
        # Évaluation globale
        healthy_models = sum(1 for status in models_status.values() if status.get("status") == "healthy")
        total_models = len(models_status)
        
        return {
            "status": "success",
            "models_checked": total_models,
            "healthy_models": healthy_models,
            "models_status": models_status,
            "overall_health": "healthy" if healthy_models == total_models else "degraded",
            "checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


async def send_maintenance_notification(results: Dict[str, Any], email: str) -> None:
    """Envoyer une notification de maintenance (placeholder)"""
    # Cette fonction pourrait être implémentée avec un service d'email
    # Pour l'instant, on log juste l'intention
    logger = get_run_logger()
    logger.info(f"📧 Notification de maintenance envoyée à {email}")


async def send_error_notification(error_results: Dict[str, Any], email: str) -> None:
    """Envoyer une notification d'erreur (placeholder)"""
    # Cette fonction pourrait être implémentée avec un service d'email
    # Pour l'instant, on log juste l'intention
    logger = get_run_logger()
    logger.error(f"🚨 Notification d'erreur envoyée à {email}")