"""
Workflows Prefect pour le traitement en lot de documents
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from prefect import flow, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner

from .tasks import process_single_document, test_document_query


@flow(
    name="batch_document_processing",
    description="Traitement en lot de plusieurs documents",
    version="1.0",
    task_runner=ConcurrentTaskRunner(),
    timeout_seconds=3600,  # 1 heure max
    retries=1
)
async def batch_document_flow(
    documents_folder: str,
    api_key: str,
    file_extensions: List[str] = None,
    chunk_size: int = None,
    template_type: str = "auto",
    test_queries: List[str] = None
) -> Dict[str, Any]:
    """
    Traiter plusieurs documents en parallèle
    
    Args:
        documents_folder: Dossier contenant les documents
        api_key: Clé API Mistral
        file_extensions: Extensions autorisées (par défaut: .pdf, .docx, .txt)
        chunk_size: Taille des chunks
        template_type: Type de template
        test_queries: Questions de test optionnelles
        
    Returns:
        Dict avec le résumé du traitement
    """
    logger = get_run_logger()
    
    logger.info(f"📂 Démarrage du traitement en lot: {documents_folder}")
    batch_start_time = datetime.now()
    
    try:
        # Vérifier que le dossier existe
        folder_path = Path(documents_folder)
        if not folder_path.exists():
            raise FileNotFoundError(f"Dossier non trouvé: {documents_folder}")
        
        # Extensions par défaut
        if file_extensions is None:
            file_extensions = ['.pdf', '.docx', '.txt']
        
        # Trouver tous les documents
        documents = []
        for ext in file_extensions:
            documents.extend(folder_path.glob(f"*{ext}"))
        
        if not documents:
            logger.warning(f"Aucun document trouvé dans {documents_folder}")
            return {
                "status": "completed",
                "documents_found": 0,
                "documents_processed": 0,
                "documents_failed": 0,
                "processing_time": 0,
                "results": []
            }
        
        logger.info(f"📄 {len(documents)} documents trouvés")
        
        # Traiter les documents en parallèle
        processing_tasks = []
        for doc_path in documents:
            task = process_single_document.submit(
                file_path=str(doc_path),
                api_key=api_key,
                chunk_size=chunk_size,
                template_type=template_type
            )
            processing_tasks.append(task)
        
        # Attendre tous les résultats
        processing_results = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        # Analyser les résultats
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(processing_results):
            if isinstance(result, Exception):
                failed_results.append({
                    "file_path": str(documents[i]),
                    "error": str(result),
                    "error_type": type(result).__name__
                })
            elif result.get("status") == "success":
                successful_results.append(result)
            else:
                failed_results.append(result)
        
        # Tests optionnels si des documents ont été traités avec succès
        test_results = []
        if test_queries and successful_results:
            logger.info(f"🧪 Exécution de {len(test_queries)} tests")
            
            for query in test_queries:
                test_task = test_document_query.submit(
                    question=query,
                    api_key=api_key
                )
                test_results.append(await test_task)
        
        # Statistiques finales
        batch_end_time = datetime.now()
        processing_time = (batch_end_time - batch_start_time).total_seconds()
        
        # Calculer des métriques globales
        total_chunks = sum(r.get("chunks_created", 0) for r in successful_results)
        avg_processing_time = (
            sum(r.get("processing_time", 0) for r in successful_results) / 
            len(successful_results) if successful_results else 0
        )
        
        batch_summary = {
            "status": "completed",
            "started_at": batch_start_time.isoformat(),
            "completed_at": batch_end_time.isoformat(),
            "total_processing_time": round(processing_time, 2),
            "documents_found": len(documents),
            "documents_processed": len(successful_results),
            "documents_failed": len(failed_results),
            "success_rate": round(len(successful_results) / len(documents) * 100, 1),
            "statistics": {
                "total_chunks_created": total_chunks,
                "avg_processing_time": round(avg_processing_time, 2),
                "templates_used": list(set(r.get("template_used") for r in successful_results)),
            },
            "results": {
                "successful": successful_results,
                "failed": failed_results,
                "tests": test_results
            }
        }
        
        logger.info(f"✅ Traitement en lot terminé:")
        logger.info(f"   📊 {len(successful_results)}/{len(documents)} documents traités")
        logger.info(f"   ⏱️ Temps total: {processing_time:.1f}s")
        logger.info(f"   🧩 Chunks créés: {total_chunks}")
        
        if failed_results:
            logger.warning(f"⚠️ {len(failed_results)} échecs:")
            for failed in failed_results[:3]:  # Log les 3 premiers échecs
                logger.warning(f"   • {Path(failed['file_path']).name}: {failed.get('error_message', 'Erreur inconnue')}")
        
        return batch_summary
        
    except Exception as e:
        batch_end_time = datetime.now()
        processing_time = (batch_end_time - batch_start_time).total_seconds()
        
        logger.error(f"❌ Erreur critique lors du traitement en lot: {str(e)}")
        return {
            "status": "error",
            "started_at": batch_start_time.isoformat(),
            "failed_at": batch_end_time.isoformat(),
            "processing_time": round(processing_time, 2),
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


@flow(
    name="process_folder_documents",
    description="Traiter tous les documents d'un dossier avec surveillance",
    version="1.0",
    timeout_seconds=7200  # 2 heures max
)
async def process_folder_documents(
    input_folder: str,
    api_key: str,
    output_report: str = None,
    enable_monitoring: bool = True
) -> Dict[str, Any]:
    """
    Workflow complet pour traiter un dossier de documents avec surveillance
    
    Args:
        input_folder: Dossier d'entrée avec les documents
        api_key: Clé API Mistral
        output_report: Fichier de rapport de sortie (optionnel)
        enable_monitoring: Activer la surveillance système
        
    Returns:
        Dict avec le résumé complet
    """
    logger = get_run_logger()
    
    logger.info(f"🚀 Workflow complet pour dossier: {input_folder}")
    
    try:
        # Phase 1: Vérification de santé préliminaire
        if enable_monitoring:
            from .tasks import check_system_health
            
            logger.info("🩺 Vérification de santé préliminaire")
            health_check = check_system_health()
            
            if health_check.get("overall_status") == "unhealthy":
                logger.warning("⚠️ Système en mauvaise santé - continuation risquée")
        
        # Phase 2: Traitement en lot principal
        logger.info("📂 Démarrage du traitement en lot")
        
        # Questions de test prédéfinies
        test_queries = [
            "Résume ce document en quelques phrases.",
            "Quels sont les points clés de ce document ?",
            "Y a-t-il des conclusions importantes ?"
        ]
        
        batch_result = await batch_document_flow(
            documents_folder=input_folder,
            api_key=api_key,
            test_queries=test_queries
        )
        
        # Phase 3: Génération du rapport (si demandée)
        if output_report:
            logger.info(f"📊 Génération du rapport: {output_report}")
            
            from .tasks import generate_performance_report
            
            performance_report = generate_performance_report()
            
            # Compiler le rapport final
            final_report = {
                "workflow": "process_folder_documents",
                "input_folder": input_folder,
                "batch_processing": batch_result,
                "performance": performance_report,
                "generated_at": datetime.now().isoformat()
            }
            
            # Sauvegarder le rapport
            report_path = Path(output_report)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Rapport sauvegardé: {output_report}")
        
        # Phase 4: Vérification de santé finale
        if enable_monitoring:
            logger.info("🩺 Vérification de santé finale")
            final_health = check_system_health()
            
            # Comparaison santé avant/après
            health_comparison = {
                "initial_status": health_check.get("overall_status") if 'health_check' in locals() else "unknown",
                "final_status": final_health.get("overall_status"),
                "health_degraded": (
                    health_check.get("health_score", 100) > final_health.get("health_score", 0)
                    if 'health_check' in locals() else False
                )
            }
        else:
            health_comparison = {"monitoring_disabled": True}
        
        # Résumé final du workflow
        workflow_summary = {
            "status": "completed",
            "input_folder": input_folder,
            "documents_processed": batch_result.get("documents_processed", 0),
            "success_rate": batch_result.get("success_rate", 0),
            "total_time": batch_result.get("total_processing_time", 0),
            "output_report": output_report,
            "health_monitoring": health_comparison,
            "completed_at": datetime.now().isoformat()
        }
        
        logger.info(f"🎉 Workflow terminé avec succès:")
        logger.info(f"   📁 Dossier: {input_folder}")
        logger.info(f"   📄 Documents: {workflow_summary['documents_processed']}")
        logger.info(f"   ✅ Taux de succès: {workflow_summary['success_rate']}%")
        logger.info(f"   ⏱️ Temps total: {workflow_summary['total_time']}s")
        
        return workflow_summary
        
    except Exception as e:
        logger.error(f"❌ Erreur critique du workflow: {str(e)}")
        return {
            "status": "error",
            "input_folder": input_folder,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "failed_at": datetime.now().isoformat()
        }


# Workflow pour automatiser le traitement nocturne
@flow(
    name="nightly_batch_processing",
    description="Traitement nocturne automatisé",
    version="1.0"
)
async def nightly_batch_processing(
    watch_folder: str = "./data/inbox",
    api_key: str = None
) -> Dict[str, Any]:
    """
    Workflow nocturne pour traiter automatiquement les nouveaux documents
    
    Args:
        watch_folder: Dossier à surveiller
        api_key: Clé API (ou depuis variables d'environnement)
        
    Returns:
        Dict avec le résumé du traitement nocturne
    """
    logger = get_run_logger()
    
    logger.info(f"🌙 Traitement nocturne automatisé: {watch_folder}")
    
    try:
        # Utiliser la clé API depuis l'environnement si pas fournie
        if not api_key:
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                raise ValueError("Clé API Mistral non trouvée (ni en paramètre ni en variable d'environnement)")
        
        # Vérifier s'il y a des documents à traiter
        watch_path = Path(watch_folder)
        if not watch_path.exists():
            logger.info(f"📁 Création du dossier de surveillance: {watch_folder}")
            watch_path.mkdir(parents=True, exist_ok=True)
            
            return {
                "status": "completed",
                "action": "folder_created",
                "documents_found": 0,
                "message": f"Dossier {watch_folder} créé pour surveillance future"
            }
        
        # Compter les documents
        document_count = 0
        for ext in ['.pdf', '.docx', '.txt']:
            document_count += len(list(watch_path.glob(f"*{ext}")))
        
        if document_count == 0:
            logger.info("📭 Aucun nouveau document à traiter")
            return {
                "status": "completed",
                "action": "no_documents",
                "documents_found": 0,
                "message": "Aucun document trouvé pour traitement"
            }
        
        # Traitement des documents trouvés
        logger.info(f"📄 {document_count} document(s) trouvé(s) pour traitement")
        
        # Générer un rapport avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"./data/reports/nightly_report_{timestamp}.json"
        
        # Lancer le workflow de traitement complet
        result = await process_folder_documents(
            input_folder=watch_folder,
            api_key=api_key,
            output_report=report_file,
            enable_monitoring=True
        )
        
        # Déplacer les documents traités vers un dossier d'archive
        archive_folder = Path(watch_folder) / "processed" / timestamp
        archive_folder.mkdir(parents=True, exist_ok=True)
        
        archived_count = 0
        for ext in ['.pdf', '.docx', '.txt']:
            for doc_file in watch_path.glob(f"*{ext}"):
                if doc_file.is_file():
                    archive_path = archive_folder / doc_file.name
                    doc_file.rename(archive_path)
                    archived_count += 1
        
        # Résumé du traitement nocturne
        nightly_summary = {
            "status": "completed",
            "action": "processed_documents",
            "documents_found": document_count,
            "documents_archived": archived_count,
            "archive_folder": str(archive_folder),
            "report_file": report_file,
            "processing_result": result,
            "completed_at": datetime.now().isoformat()
        }
        
        logger.info(f"🌙 Traitement nocturne terminé:")
        logger.info(f"   📄 {document_count} documents traités")
        logger.info(f"   📦 Documents archivés dans: {archive_folder}")
        logger.info(f"   📊 Rapport: {report_file}")
        
        return nightly_summary
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement nocturne: {str(e)}")
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "failed_at": datetime.now().isoformat()
        }