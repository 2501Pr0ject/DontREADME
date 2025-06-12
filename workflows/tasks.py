"""
Tâches Prefect réutilisables pour DontREADME
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from prefect import task, get_run_logger
import psutil

# Import des composants DontREADME
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.components.file_processor import FileProcessor
from app.components.chat_engine import EnhancedChatEngine
from app.config import Config
from utils.validators import FileValidator, InputValidator
from utils.performance import PerformanceMonitor


@task(
    name="process_single_document",
    description="Traiter un document unique",
    retries=2,
    retry_delay_seconds=[30, 120],
    tags=["document", "processing"]
)
def process_single_document(
    file_path: str,
    api_key: str,
    chunk_size: int = None,
    template_type: str = "auto"
) -> Dict[str, Any]:
    """
    Traiter un document unique via Prefect
    
    Args:
        file_path: Chemin vers le fichier
        api_key: Clé API Mistral
        chunk_size: Taille des chunks (optionnel)
        template_type: Type de template à utiliser
        
    Returns:
        Dict avec les résultats du traitement
    """
    logger = get_run_logger()
    
    try:
        logger.info(f"📄 Traitement du document: {file_path}")
        
        # Vérifier que le fichier existe
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        # Validation du fichier
        with open(file_path, 'rb') as f:
            file_valid, file_error = FileValidator.validate_file(f)
            if not file_valid:
                raise ValueError(f"Fichier invalide: {file_error}")
        
        # Validation de la clé API
        api_valid, api_error = InputValidator.validate_api_key(api_key, 'mistral')
        if not api_valid:
            raise ValueError(f"Clé API invalide: {api_error}")
        
        # Traitement du document
        text_content, filename = FileProcessor.process_uploaded_file(file_path)
        
        if not text_content.strip():
            raise ValueError("Aucun contenu textuel extrait du document")
        
        # Configuration du moteur de chat
        chat_engine = EnhancedChatEngine()
        chat_engine.setup_llm(api_key)
        
        # Traitement avec monitoring
        monitor = PerformanceMonitor()
        
        @monitor.measure_performance("document_processing")
        def _process():
            return chat_engine.process_document_smart(
                text_content,
                filename,
                chunk_size or Config.DEFAULT_CHUNK_SIZE,
                template_type
            )
        
        processing_result = _process()
        
        # Récupérer les métriques de performance
        metrics = monitor.get_performance_summary()
        
        result = {
            "status": "success",
            "file_path": file_path,
            "filename": filename,
            "content_length": len(text_content),
            "template_used": processing_result.get("template_type", template_type),
            "chunks_created": processing_result.get("chunk_count", 0),
            "processing_time": metrics.get("document_processing", {}).get("avg_duration", 0),
            "processed_at": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        logger.info(f"✅ Document traité avec succès: {filename}")
        logger.info(f"   📊 {result['chunks_created']} chunks créés")
        logger.info(f"   ⏱️ Temps: {result['processing_time']:.2f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement document {file_path}: {str(e)}")
        return {
            "status": "error",
            "file_path": file_path,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "processed_at": datetime.now().isoformat()
        }


@task(
    name="test_document_query",
    description="Tester une requête sur un document traité",
    retries=1,
    tags=["testing", "query"]
)
def test_document_query(
    question: str,
    api_key: str,
    expected_keywords: List[str] = None
) -> Dict[str, Any]:
    """
    Tester une requête sur le document en cours
    
    Args:
        question: Question à poser
        api_key: Clé API Mistral
        expected_keywords: Mots-clés attendus dans la réponse
        
    Returns:
        Dict avec les résultats du test
    """
    logger = get_run_logger()
    
    try:
        logger.info(f"❓ Test de requête: {question}")
        
        # Configuration du moteur de chat
        chat_engine = EnhancedChatEngine()
        chat_engine.setup_llm(api_key)
        
        # Monitoring de la requête
        monitor = PerformanceMonitor()
        
        @monitor.measure_performance("query_test")
        def _query():
            return chat_engine.chat_with_sources(question)
        
        start_time = datetime.now()
        response_data = _query()
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        # Analyser la réponse
        response_text = response_data.get("response", "")
        sources = response_data.get("sources", [])
        
        # Vérifier les mots-clés attendus
        keywords_found = []
        if expected_keywords:
            for keyword in expected_keywords:
                if keyword.lower() in response_text.lower():
                    keywords_found.append(keyword)
        
        # Évaluer la qualité de la réponse
        quality_score = 0
        if len(response_text) > 50:  # Réponse substantielle
            quality_score += 40
        if sources:  # Sources trouvées
            quality_score += 30
        if keywords_found:  # Mots-clés trouvés
            quality_score += 30 * (len(keywords_found) / len(expected_keywords or [1]))
        
        result = {
            "status": "success",
            "question": question,
            "response_length": len(response_text),
            "sources_count": len(sources),
            "response_time": response_time,
            "keywords_expected": expected_keywords or [],
            "keywords_found": keywords_found,
            "quality_score": min(100, quality_score),
            "tested_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Test réussi - Score qualité: {quality_score}/100")
        logger.info(f"   📝 Réponse: {len(response_text)} caractères")
        logger.info(f"   📚 Sources: {len(sources)}")
        logger.info(f"   ⏱️ Temps: {response_time:.2f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur test requête: {str(e)}")
        return {
            "status": "error",
            "question": question,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "tested_at": datetime.now().isoformat()
        }


@task(
    name="cleanup_old_data",
    description="Nettoyer les anciennes données",
    retries=1,
    tags=["maintenance", "cleanup"]
)
def cleanup_old_data(
    max_age_days: int = 7,
    directories: List[str] = None
) -> Dict[str, Any]:
    """
    Nettoyer les fichiers anciens
    
    Args:
        max_age_days: Âge maximum en jours
        directories: Répertoires à nettoyer
        
    Returns:
        Dict avec les statistiques de nettoyage
    """
    logger = get_run_logger()
    
    try:
        logger.info(f"🧹 Nettoyage des fichiers > {max_age_days} jours")
        
        # Répertoires par défaut
        if directories is None:
            directories = [
                "./data/uploads",
                "./data/exports"
            ]
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        total_cleaned = 0
        total_size_freed = 0
        cleaned_by_dir = {}
        
        for directory in directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                continue
            
            dir_cleaned = 0
            dir_size_freed = 0
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if file_mtime < cutoff_date:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        
                        dir_cleaned += 1
                        dir_size_freed += file_size
                        
                        logger.debug(f"🗑️ Supprimé: {file_path}")
            
            cleaned_by_dir[directory] = {
                "files_cleaned": dir_cleaned,
                "size_freed_mb": round(dir_size_freed / 1024 / 1024, 2)
            }
            
            total_cleaned += dir_cleaned
            total_size_freed += dir_size_freed
        
        result = {
            "status": "success",
            "max_age_days": max_age_days,
            "total_files_cleaned": total_cleaned,
            "total_size_freed_mb": round(total_size_freed / 1024 / 1024, 2),
            "directories_processed": len(directories),
            "cleaned_by_directory": cleaned_by_dir,
            "cleaned_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Nettoyage terminé:")
        logger.info(f"   🗑️ {total_cleaned} fichiers supprimés")
        logger.info(f"   💾 {result['total_size_freed_mb']} MB libérés")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur nettoyage: {str(e)}")
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "cleaned_at": datetime.now().isoformat()
        }


@task(
    name="check_system_health",
    description="Vérifier la santé du système",
    retries=1,
    tags=["monitoring", "health"]
)
def check_system_health() -> Dict[str, Any]:
    """
    Effectuer une vérification de santé système
    
    Returns:
        Dict avec les métriques de santé
    """
    logger = get_run_logger()
    
    try:
        logger.info("🩺 Vérification de santé système")
        
        # Métriques système
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Vérifier ChromaDB
        chromadb_healthy = True
        try:
            import chromadb
            client = chromadb.PersistentClient(path=Config.CHROMADB_PATH)
            # Test de base
            collections = client.list_collections()
            chromadb_status = "healthy"
            chromadb_collections = len(collections)
        except Exception as e:
            chromadb_healthy = False
            chromadb_status = f"error: {str(e)}"
            chromadb_collections = 0
        
        # Vérifier les répertoires essentiels
        essential_dirs = [
            "./data/vectorstore",
            "./data/uploads",
            "./app/components"
        ]
        
        dirs_status = {}
        for dir_path in essential_dirs:
            path = Path(dir_path)
            dirs_status[dir_path] = {
                "exists": path.exists(),
                "readable": path.exists() and os.access(path, os.R_OK),
                "writable": path.exists() and os.access(path, os.W_OK)
            }
        
        # Évaluation globale de santé
        health_score = 100
        issues = []
        
        if cpu_percent > 80:
            health_score -= 20
            issues.append(f"CPU élevé: {cpu_percent}%")
        
        if memory.percent > 85:
            health_score -= 20
            issues.append(f"Mémoire élevée: {memory.percent}%")
        
        if disk.percent > 90:
            health_score -= 30
            issues.append(f"Disque plein: {disk.percent}%")
        
        if not chromadb_healthy:
            health_score -= 25
            issues.append("ChromaDB inaccessible")
        
        # Déterminer le statut global
        if health_score >= 80:
            overall_status = "healthy"
        elif health_score >= 60:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        result = {
            "status": "success",
            "overall_status": overall_status,
            "health_score": health_score,
            "issues": issues,
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / 1024**3, 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / 1024**3, 2)
            },
            "chromadb": {
                "status": chromadb_status,
                "collections_count": chromadb_collections
            },
            "directories": dirs_status,
            "checked_at": datetime.now().isoformat()
        }
        
        logger.info(f"🩺 Santé système: {overall_status.upper()}")
        logger.info(f"   📊 Score: {health_score}/100")
        logger.info(f"   🖥️ CPU: {cpu_percent}%")
        logger.info(f"   💾 RAM: {memory.percent}%")
        logger.info(f"   💿 Disque: {disk.percent}%")
        
        if issues:
            logger.warning(f"⚠️ Problèmes détectés: {', '.join(issues)}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur vérification santé: {str(e)}")
        return {
            "status": "error",
            "overall_status": "unknown",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "checked_at": datetime.now().isoformat()
        }


@task(
    name="generate_performance_report",
    description="Générer un rapport de performance",
    retries=1,
    tags=["monitoring", "report"]
)
def generate_performance_report(
    include_system_metrics: bool = True
) -> Dict[str, Any]:
    """
    Générer un rapport de performance complet
    
    Args:
        include_system_metrics: Inclure les métriques système
        
    Returns:
        Dict avec le rapport de performance
    """
    logger = get_run_logger()
    
    try:
        logger.info("📊 Génération du rapport de performance")
        
        # Vérification de santé
        health_result = check_system_health()
        
        # Métriques de performance (si disponibles)
        monitor = PerformanceMonitor()
        performance_summary = monitor.get_performance_summary()
        
        # Informations sur les données
        data_stats = {}
        
        # ChromaDB stats
        try:
            import chromadb
            client = chromadb.PersistentClient(path=Config.CHROMADB_PATH)
            collections = client.list_collections()
            
            total_documents = 0
            for collection in collections:
                total_documents += collection.count()
            
            data_stats["chromadb"] = {
                "collections": len(collections),
                "total_documents": total_documents
            }
        except Exception:
            data_stats["chromadb"] = {"status": "unavailable"}
        
        # Statistiques des fichiers
        upload_dir = Path("./data/uploads")
        if upload_dir.exists():
            files = list(upload_dir.glob("*"))
            data_stats["uploads"] = {
                "total_files": len(files),
                "total_size_mb": round(
                    sum(f.stat().st_size for f in files if f.is_file()) / 1024**2, 2
                )
            }
        
        # Compiler le rapport
        report = {
            "status": "success",
            "generated_at": datetime.now().isoformat(),
            "health": health_result,
            "performance": performance_summary,
            "data_statistics": data_stats,
            "system_info": {
                "python_version": sys.version.split()[0],
                "platform": sys.platform,
                "working_directory": str(Path.cwd())
            }
        }
        
        # Sauvegarder le rapport
        reports_dir = Path("./data/reports")
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        report["report_file"] = str(report_file)
        
        logger.info(f"📊 Rapport généré: {report_file.name}")
        logger.info(f"   🩺 Santé: {health_result.get('overall_status', 'unknown')}")
        logger.info(f"   📈 Métriques: {len(performance_summary)} catégories")
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Erreur génération rapport: {str(e)}")
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "generated_at": datetime.now().isoformat()
        }