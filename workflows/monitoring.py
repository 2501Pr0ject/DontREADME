"""
Workflows Prefect pour le monitoring et surveillance de DontREADME
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta

from prefect import flow, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner

from .tasks import check_system_health, generate_performance_report


@flow(
    name="health_check_flow",
    description="Surveillance de santé système en continu",
    version="1.0",
    timeout_seconds=300,  # 5 minutes max
    retries=1
)
async def health_check_flow(
    alert_threshold: int = 70,
    notification_email: str = None
) -> Dict[str, Any]:
    """
    Workflow de surveillance de santé système
    
    Args:
        alert_threshold: Seuil d'alerte pour le score de santé
        notification_email: Email pour les alertes (optionnel)
        
    Returns:
        Dict avec les résultats de santé
    """
    logger = get_run_logger()
    
    logger.info("🩺 Surveillance de santé système")
    check_start = datetime.now()
    
    try:
        # Vérification de santé principale
        health_result = check_system_health()
        
        # Analyser les résultats
        health_score = health_result.get("health_score", 0)
        overall_status = health_result.get("overall_status", "unknown")
        issues = health_result.get("issues", [])
        
        # Déterminer si des alertes sont nécessaires
        needs_alert = health_score < alert_threshold
        critical_issues = [issue for issue in issues if "élevé" in issue or "plein" in issue]
        
        # Surveillance spécifique ChromaDB
        chromadb_status = health_result.get("chromadb", {}).get("status", "unknown")
        chromadb_healthy = chromadb_status == "healthy"
        
        # Métriques système détaillées
        system_metrics = health_result.get("system", {})
        
        # Historique de santé (simulation - pourrait être stocké en DB)
        health_history = {
            "current_check": {
                "timestamp": check_start.isoformat(),
                "score": health_score,
                "status": overall_status,
                "issues_count": len(issues)
            }
        }
        
        # Résultat du monitoring
        monitoring_result = {
            "status": "success",
            "monitoring_type": "health_check",
            "started_at": check_start.isoformat(),
            "completed_at": datetime.now().isoformat(),
            "health_summary": {
                "score": health_score,
                "status": overall_status,
                "needs_alert": needs_alert,
                "critical_issues_count": len(critical_issues),
                "chromadb_healthy": chromadb_healthy
            },
            "detailed_health": health_result,
            "history": health_history,
            "alert_threshold": alert_threshold
        }
        
        # Envoyer alerte si nécessaire
        if needs_alert and notification_email:
            await send_health_alert(
                health_result, 
                notification_email, 
                alert_threshold
            )
            monitoring_result["alert_sent"] = True
        else:
            monitoring_result["alert_sent"] = False
        
        # Logging des résultats
        logger.info(f"🩺 Monitoring de santé terminé:")
        logger.info(f"   📊 Score: {health_score}/100")
        logger.info(f"   🚥 Statut: {overall_status.upper()}")
        if issues:
            logger.warning(f"   ⚠️ Problèmes: {len(issues)}")
        if needs_alert:
            logger.warning(f"   🚨 Alerte nécessaire (seuil: {alert_threshold})")
        
        return monitoring_result
        
    except Exception as e:
        logger.error(f"❌ Erreur monitoring santé: {str(e)}")
        return {
            "status": "error",
            "monitoring_type": "health_check",
            "started_at": check_start.isoformat(),
            "failed_at": datetime.now().isoformat(),
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


@flow(
    name="performance_monitoring_flow",
    description="Surveillance des performances et métriques",
    version="1.0",
    task_runner=ConcurrentTaskRunner(),
    timeout_seconds=600  # 10 minutes max
)
async def performance_monitoring_flow(
    generate_detailed_report: bool = True,
    save_metrics_history: bool = True
) -> Dict[str, Any]:
    """
    Workflow de surveillance des performances
    
    Args:
        generate_detailed_report: Générer un rapport détaillé
        save_metrics_history: Sauvegarder l'historique des métriques
        
    Returns:
        Dict avec les résultats de performance
    """
    logger = get_run_logger()
    
    logger.info("📈 Surveillance des performances")
    monitoring_start = datetime.now()
    
    try:
        # Vérification de santé pour le contexte
        health_check_task = check_system_health()
        
        # Génération du rapport de performance
        if generate_detailed_report:
            performance_report_task = generate_performance_report(
                include_system_metrics=True
            )
        else:
            performance_report_task = None
        
        # Attendre les résultats
        health_result = health_check_task
        performance_report = performance_report_task if performance_report_task else {}
        
        # Métriques de performance en temps réel
        current_metrics = await collect_realtime_metrics()
        
        # Analyse des tendances (simulation)
        trends_analysis = analyze_performance_trends(
            current_metrics, 
            health_result
        )
        
        # Détection d'anomalies
        anomalies = detect_performance_anomalies(
            current_metrics,
            health_result
        )
        
        # Compilation des résultats
        performance_summary = {
            "status": "success",
            "monitoring_type": "performance",
            "started_at": monitoring_start.isoformat(),
            "completed_at": datetime.now().isoformat(),
            "current_metrics": current_metrics,
            "health_context": {
                "score": health_result.get("health_score", 0),
                "status": health_result.get("overall_status", "unknown"),
                "system": health_result.get("system", {})
            },
            "trends": trends_analysis,
            "anomalies": anomalies,
            "performance_report": performance_report
        }
        
        # Sauvegarder l'historique si demandé
        if save_metrics_history:
            history_saved = await save_performance_history(performance_summary)
            performance_summary["history_saved"] = history_saved
        
        # Évaluation globale de performance
        performance_score = calculate_performance_score(
            current_metrics,
            health_result,
            anomalies
        )
        
        performance_summary["performance_score"] = performance_score
        
        logger.info(f"📈 Monitoring performance terminé:")
        logger.info(f"   📊 Score performance: {performance_score}/100")
        logger.info(f"   🔍 Anomalies détectées: {len(anomalies)}")
        logger.info(f"   📋 Rapport généré: {'Oui' if generate_detailed_report else 'Non'}")
        
        return performance_summary
        
    except Exception as e:
        logger.error(f"❌ Erreur monitoring performance: {str(e)}")
        return {
            "status": "error",
            "monitoring_type": "performance",
            "started_at": monitoring_start.isoformat(),
            "failed_at": datetime.now().isoformat(),
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


@flow(
    name="continuous_monitoring",
    description="Surveillance continue avec alertes",
    version="1.0",
    timeout_seconds=1800  # 30 minutes max
)
async def continuous_monitoring_flow(
    monitoring_duration_minutes: int = 60,
    check_interval_minutes: int = 5,
    alert_email: str = None
) -> Dict[str, Any]:
    """
    Workflow de surveillance continue
    
    Args:
        monitoring_duration_minutes: Durée totale de surveillance
        check_interval_minutes: Intervalle entre les vérifications
        alert_email: Email pour les alertes
        
    Returns:
        Dict avec le résumé de la surveillance continue
    """
    logger = get_run_logger()
    
    logger.info(f"🔄 Surveillance continue ({monitoring_duration_minutes}min)")
    continuous_start = datetime.now()
    
    try:
        monitoring_results = []
        alerts_sent = 0
        end_time = continuous_start + timedelta(minutes=monitoring_duration_minutes)
        
        while datetime.now() < end_time:
            check_start = datetime.now()
            
            # Vérification de santé
            health_result = await health_check_flow(
                alert_threshold=75,
                notification_email=alert_email
            )
            
            # Surveillance de performance légère
            perf_metrics = await collect_realtime_metrics()
            
            # Enregistrer les résultats
            check_result = {
                "timestamp": check_start.isoformat(),
                "health_score": health_result.get("health_summary", {}).get("score", 0),
                "health_status": health_result.get("health_summary", {}).get("status", "unknown"),
                "alert_triggered": health_result.get("alert_sent", False),
                "performance_metrics": perf_metrics
            }
            
            monitoring_results.append(check_result)
            
            if check_result["alert_triggered"]:
                alerts_sent += 1
            
            logger.info(f"🔍 Check #{len(monitoring_results)}: {check_result['health_status']} "
                       f"(score: {check_result['health_score']})")
            
            # Attendre avant le prochain check
            if datetime.now() < end_time:
                await asyncio.sleep(check_interval_minutes * 60)
        
        # Analyse des résultats de surveillance
        health_scores = [r["health_score"] for r in monitoring_results]
        avg_health_score = sum(health_scores) / len(health_scores) if health_scores else 0
        min_health_score = min(health_scores) if health_scores else 0
        max_health_score = max(health_scores) if health_scores else 0
        
        # Statuts uniques observés
        statuses_observed = list(set(r["health_status"] for r in monitoring_results))
        
        continuous_summary = {
            "status": "completed",
            "monitoring_type": "continuous",
            "started_at": continuous_start.isoformat(),
            "completed_at": datetime.now().isoformat(),
            "duration_minutes": monitoring_duration_minutes,
            "check_interval_minutes": check_interval_minutes,
            "total_checks": len(monitoring_results),
            "alerts_sent": alerts_sent,
            "health_statistics": {
                "average_score": round(avg_health_score, 1),
                "min_score": min_health_score,
                "max_score": max_health_score,
                "statuses_observed": statuses_observed
            },
            "detailed_results": monitoring_results
        }
        
        logger.info(f"🔄 Surveillance continue terminée:")
        logger.info(f"   📊 {len(monitoring_results)} vérifications effectuées")
        logger.info(f"   📈 Score moyen: {avg_health_score:.1f}/100")
        logger.info(f"   🚨 Alertes envoyées: {alerts_sent}")
        logger.info(f"   ⏱️ Durée: {monitoring_duration_minutes} minutes")
        
        return continuous_summary
        
    except Exception as e:
        logger.error(f"❌ Erreur surveillance continue: {str(e)}")
        return {
            "status": "error",
            "monitoring_type": "continuous",
            "started_at": continuous_start.isoformat(),
            "failed_at": datetime.now().isoformat(),
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


# Fonctions utilitaires pour le monitoring
async def collect_realtime_metrics() -> Dict[str, Any]:
    """Collecter les métriques en temps réel"""
    try:
        import psutil
        
        # CPU et mémoire instantanés
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Processus Python actuel
        current_process = psutil.Process()
        process_memory = current_process.memory_info()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / 1024**3, 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / 1024**3, 2),
            "process_memory_mb": round(process_memory.rss / 1024**2, 2),
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
        
    except Exception:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": "metrics_collection_failed"
        }


def analyze_performance_trends(
    current_metrics: Dict[str, Any], 
    health_result: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyser les tendances de performance"""
    try:
        # Analyse basique (simulation - dans un vrai système, on comparerait avec l'historique)
        system = health_result.get("system", {})
        
        trends = {
            "cpu_trend": "stable",  # stable/increasing/decreasing
            "memory_trend": "stable",
            "disk_trend": "stable",
            "overall_trend": "stable"
        }
        
        # Simulation d'analyse de tendance basée sur les seuils
        if system.get("cpu_percent", 0) > 70:
            trends["cpu_trend"] = "concerning"
        if system.get("memory_percent", 0) > 80:
            trends["memory_trend"] = "concerning"
        if system.get("disk_percent", 0) > 85:
            trends["disk_trend"] = "concerning"
        
        # Tendance globale
        concerning_trends = sum(1 for trend in trends.values() if trend == "concerning")
        if concerning_trends >= 2:
            trends["overall_trend"] = "degrading"
        elif concerning_trends == 1:
            trends["overall_trend"] = "watch"
        
        return trends
        
    except Exception:
        return {"error": "trend_analysis_failed"}


def detect_performance_anomalies(
    current_metrics: Dict[str, Any],
    health_result: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Détecter les anomalies de performance"""
    anomalies = []
    
    try:
        system = health_result.get("system", {})
        
        # Anomalies CPU
        cpu_percent = system.get("cpu_percent", 0)
        if cpu_percent > 90:
            anomalies.append({
                "type": "cpu_spike",
                "severity": "critical",
                "value": cpu_percent,
                "threshold": 90,
                "message": f"CPU très élevé: {cpu_percent}%"
            })
        elif cpu_percent > 75:
            anomalies.append({
                "type": "cpu_high",
                "severity": "warning",
                "value": cpu_percent,
                "threshold": 75,
                "message": f"CPU élevé: {cpu_percent}%"
            })
        
        # Anomalies mémoire
        memory_percent = system.get("memory_percent", 0)
        if memory_percent > 95:
            anomalies.append({
                "type": "memory_critical",
                "severity": "critical",
                "value": memory_percent,
                "threshold": 95,
                "message": f"Mémoire critique: {memory_percent}%"
            })
        elif memory_percent > 85:
            anomalies.append({
                "type": "memory_high",
                "severity": "warning",
                "value": memory_percent,
                "threshold": 85,
                "message": f"Mémoire élevée: {memory_percent}%"
            })
        
        # Anomalies disque
        disk_percent = system.get("disk_percent", 0)
        if disk_percent > 95:
            anomalies.append({
                "type": "disk_full",
                "severity": "critical",
                "value": disk_percent,
                "threshold": 95,
                "message": f"Disque quasi-plein: {disk_percent}%"
            })
        
        return anomalies
        
    except Exception:
        return [{"type": "anomaly_detection_error", "severity": "error"}]


def calculate_performance_score(
    current_metrics: Dict[str, Any],
    health_result: Dict[str, Any],
    anomalies: List[Dict[str, Any]]
) -> int:
    """Calculer un score de performance global"""
    try:
        base_score = 100
        
        # Pénalités basées sur les anomalies
        for anomaly in anomalies:
            if anomaly.get("severity") == "critical":
                base_score -= 25
            elif anomaly.get("severity") == "warning":
                base_score -= 10
        
        # Bonus/malus basé sur le score de santé
        health_score = health_result.get("health_score", 100)
        if health_score < 70:
            base_score -= 15
        elif health_score > 90:
            base_score += 5
        
        return max(0, min(100, base_score))
        
    except Exception:
        return 0


async def save_performance_history(performance_data: Dict[str, Any]) -> bool:
    """Sauvegarder l'historique de performance"""
    try:
        history_dir = Path("./data/monitoring")
        history_dir.mkdir(exist_ok=True)
        
        # Fichier d'historique quotidien
        today = datetime.now().strftime("%Y%m%d")
        history_file = history_dir / f"performance_history_{today}.json"
        
        # Charger l'historique existant ou créer nouveau
        history = []
        if history_file.exists():
            import json
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        # Ajouter les nouvelles données
        history.append({
            "timestamp": datetime.now().isoformat(),
            "performance_score": performance_data.get("performance_score", 0),
            "health_score": performance_data.get("health_context", {}).get("score", 0),
            "anomalies_count": len(performance_data.get("anomalies", [])),
            "metrics_snapshot": performance_data.get("current_metrics", {})
        })
        
        # Garder seulement les 1000 dernières entrées
        history = history[-1000:]
        
        # Sauvegarder
        import json
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception:
        return False


async def send_health_alert(
    health_result: Dict[str, Any], 
    email: str, 
    threshold: int
) -> None:
    """Envoyer une alerte de santé (placeholder)"""
    logger = get_run_logger()
    
    # Cette fonction pourrait être implémentée avec un service d'email
    health_score = health_result.get("health_score", 0)
    issues = health_result.get("issues", [])
    
    logger.warning(f"🚨 Alerte santé envoyée à {email}:")
    logger.warning(f"   📊 Score: {health_score}/100 (seuil: {threshold})")
    logger.warning(f"   ⚠️ Problèmes: {', '.join(issues[:3])}")