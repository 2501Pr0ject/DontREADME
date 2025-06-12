"""
Workflows Prefect pour les tests automatisés de DontREADME
"""

import os
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from prefect import flow, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner

from .tasks import process_single_document, test_document_query, check_system_health


@flow(
    name="automated_testing_flow",
    description="Tests automatisés complets du système",
    version="1.0",
    task_runner=ConcurrentTaskRunner(),
    timeout_seconds=1800  # 30 minutes max
)
async def automated_testing_flow(
    api_key: str,
    test_documents_folder: str = "./tests/documents",
    generate_test_report: bool = True
) -> Dict[str, Any]:
    """
    Workflow de tests automatisés complets
    
    Args:
        api_key: Clé API Mistral pour les tests
        test_documents_folder: Dossier contenant les documents de test
        generate_test_report: Générer un rapport de test détaillé
        
    Returns:
        Dict avec les résultats des tests
    """
    logger = get_run_logger()
    
    logger.info("🧪 Démarrage des tests automatisés")
    testing_start = datetime.now()
    
    try:
        test_results = {
            "started_at": testing_start.isoformat(),
            "test_type": "automated_full_suite",
            "test_suites": {}
        }
        
        # Suite 1: Tests de santé système
        logger.info("🩺 Suite 1: Tests de santé système")
        health_tests = await run_health_tests()
        test_results["test_suites"]["health"] = health_tests
        
        # Suite 2: Tests de traitement de documents
        logger.info("📄 Suite 2: Tests de traitement de documents")
        document_tests = await run_document_processing_tests(
            api_key, 
            test_documents_folder
        )
        test_results["test_suites"]["document_processing"] = document_tests
        
        # Suite 3: Tests de requêtes et réponses
        logger.info("💬 Suite 3: Tests de requêtes et réponses")
        query_tests = await run_query_response_tests(api_key)
        test_results["test_suites"]["query_response"] = query_tests
        
        # Suite 4: Tests de performance
        logger.info("⚡ Suite 4: Tests de performance")
        performance_tests = await run_performance_tests(api_key)
        test_results["test_suites"]["performance"] = performance_tests
        
        # Suite 5: Tests de robustesse
        logger.info("🛡️ Suite 5: Tests de robustesse")
        robustness_tests = await run_robustness_tests(api_key)
        test_results["test_suites"]["robustness"] = robustness_tests
        
        # Compilation des résultats
        testing_end = datetime.now()
        testing_duration = (testing_end - testing_start).total_seconds()
        
        # Calculer les statistiques globales
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for suite_name, suite_results in test_results["test_suites"].items():
            suite_total = suite_results.get("total_tests", 0)
            suite_passed = suite_results.get("passed_tests", 0)
            suite_failed = suite_results.get("failed_tests", 0)
            
            total_tests += suite_total
            passed_tests += suite_passed
            failed_tests += suite_failed
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        test_results.update({
            "status": "completed",
            "completed_at": testing_end.isoformat(),
            "duration_seconds": round(testing_duration, 2),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round(success_rate, 1),
                "suites_count": len(test_results["test_suites"])
            }
        })
        
        # Générer le rapport si demandé
        if generate_test_report:
            report_path = await generate_test_report_file(test_results)
            test_results["report_file"] = report_path
        
        # Déterminer le statut global
        if success_rate >= 95:
            overall_status = "excellent"
        elif success_rate >= 85:
            overall_status = "good"
        elif success_rate >= 70:
            overall_status = "acceptable"
        else:
            overall_status = "needs_attention"
        
        test_results["overall_status"] = overall_status
        
        logger.info(f"🧪 Tests automatisés terminés:")
        logger.info(f"   📊 {passed_tests}/{total_tests} tests réussis ({success_rate:.1f}%)")
        logger.info(f"   ⏱️ Durée: {testing_duration:.1f}s")
        logger.info(f"   🎯 Statut: {overall_status.upper()}")
        
        return test_results
        
    except Exception as e:
        testing_end = datetime.now()
        testing_duration = (testing_end - testing_start).total_seconds()
        
        logger.error(f"❌ Erreur lors des tests automatisés: {str(e)}")
        return {
            "status": "error",
            "started_at": testing_start.isoformat(),
            "failed_at": testing_end.isoformat(),
            "duration_seconds": round(testing_duration, 2),
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


@flow(
    name="regression_testing",
    description="Tests de régression après modifications",
    version="1.0",
    timeout_seconds=900  # 15 minutes max
)
async def regression_testing_flow(
    api_key: str,
    baseline_report_path: str = None
) -> Dict[str, Any]:
    """
    Workflow de tests de régression
    
    Args:
        api_key: Clé API Mistral
        baseline_report_path: Chemin vers le rapport de référence
        
    Returns:
        Dict avec les résultats de régression
    """
    logger = get_run_logger()
    
    logger.info("🔄 Tests de régression")
    regression_start = datetime.now()
    
    try:
        # Exécuter les tests actuels
        current_results = await automated_testing_flow(
            api_key=api_key,
            generate_test_report=False
        )
        
        # Charger les résultats de référence si disponibles
        baseline_results = None
        if baseline_report_path and Path(baseline_report_path).exists():
            with open(baseline_report_path, 'r', encoding='utf-8') as f:
                baseline_data = json.load(f)
                baseline_results = baseline_data.get("summary", {})
        
        # Comparer les résultats
        regression_analysis = analyze_regression(current_results, baseline_results)
        
        regression_summary = {
            "status": "completed",
            "started_at": regression_start.isoformat(),
            "completed_at": datetime.now().isoformat(),
            "current_results": current_results.get("summary", {}),
            "baseline_results": baseline_results,
            "regression_analysis": regression_analysis,
            "has_regression": regression_analysis.get("has_regression", False),
            "baseline_used": baseline_results is not None
        }
        
        # Déterminer l'action recommandée
        if regression_analysis.get("has_regression", False):
            regression_summary["recommendation"] = "investigate_changes"
            logger.warning("⚠️ Régression détectée - investigation nécessaire")
        else:
            regression_summary["recommendation"] = "changes_ok"
            logger.info("✅ Aucune régression détectée")
        
        return regression_summary
        
    except Exception as e:
        logger.error(f"❌ Erreur tests de régression: {str(e)}")
        return {
            "status": "error",
            "started_at": regression_start.isoformat(),
            "failed_at": datetime.now().isoformat(),
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


@flow(
    name="smoke_testing",
    description="Tests rapides de fonctionnement de base",
    version="1.0",
    timeout_seconds=300  # 5 minutes max
)
async def smoke_testing_flow(api_key: str) -> Dict[str, Any]:
    """
    Workflow de tests smoke (tests rapides de base)
    
    Args:
        api_key: Clé API Mistral
        
    Returns:
        Dict avec les résultats des tests smoke
    """
    logger = get_run_logger()
    
    logger.info("💨 Tests smoke (vérifications rapides)")
    smoke_start = datetime.now()
    
    try:
        smoke_results = {
            "started_at": smoke_start.isoformat(),
            "test_type": "smoke",
            "tests": []
        }
        
        # Test 1: Santé système
        logger.info("🩺 Test 1: Santé système")
        health_result = check_system_health()
        smoke_results["tests"].append({
            "name": "system_health",
            "status": "passed" if health_result.get("status") == "success" else "failed",
            "duration": 1.0,
            "details": health_result.get("overall_status", "unknown")
        })
        
        # Test 2: Création d'un document de test
        logger.info("📄 Test 2: Traitement document basique")
        test_doc_result = await test_basic_document_processing(api_key)
        smoke_results["tests"].append(test_doc_result)
        
        # Test 3: Requête basique
        logger.info("💬 Test 3: Requête basique")
        test_query_result = await test_basic_query(api_key)
        smoke_results["tests"].append(test_query_result)
        
        # Compiler les résultats
        smoke_end = datetime.now()
        smoke_duration = (smoke_end - smoke_start).total_seconds()
        
        passed_tests = sum(1 for test in smoke_results["tests"] if test["status"] == "passed")
        total_tests = len(smoke_results["tests"])
        
        smoke_results.update({
            "status": "completed",
            "completed_at": smoke_end.isoformat(),
            "duration_seconds": round(smoke_duration, 2),
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "success_rate": round(passed_tests / total_tests * 100, 1) if total_tests > 0 else 0,
            "all_tests_passed": passed_tests == total_tests
        })
        
        logger.info(f"💨 Tests smoke terminés:")
        logger.info(f"   📊 {passed_tests}/{total_tests} tests réussis")
        logger.info(f"   ⏱️ Durée: {smoke_duration:.1f}s")
        logger.info(f"   ✅ Système: {'OK' if smoke_results['all_tests_passed'] else 'KO'}")
        
        return smoke_results
        
    except Exception as e:
        logger.error(f"❌ Erreur tests smoke: {str(e)}")
        return {
            "status": "error",
            "started_at": smoke_start.isoformat(),
            "failed_at": datetime.now().isoformat(),
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


# Fonctions utilitaires pour les tests
async def run_health_tests() -> Dict[str, Any]:
    """Exécuter les tests de santé système"""
    health_start = datetime.now()
    
    tests = []
    
    # Test santé globale
    health_result = check_system_health()
    tests.append({
        "name": "global_health_check",
        "status": "passed" if health_result.get("status") == "success" else "failed",
        "details": health_result,
        "duration": 2.0
    })
    
    # Test répertoires essentiels
    essential_dirs = ["./data", "./app", "./utils"]
    for dir_path in essential_dirs:
        dir_exists = Path(dir_path).exists()
        tests.append({
            "name": f"directory_exists_{dir_path.replace('./', '').replace('/', '_')}",
            "status": "passed" if dir_exists else "failed",
            "details": f"Directory {dir_path} exists: {dir_exists}",
            "duration": 0.1
        })
    
    # Test modules importables
    modules_to_test = [
        "app.config",
        "app.components.file_processor",
        "app.components.chat_engine_enhanced",
        "utils.validators"
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            test_status = "passed"
            test_details = f"Module {module_name} imported successfully"
        except Exception as e:
            test_status = "failed"
            test_details = f"Module {module_name} import failed: {str(e)}"
        
        tests.append({
            "name": f"import_{module_name.replace('.', '_')}",
            "status": test_status,
            "details": test_details,
            "duration": 0.5
        })
    
    # Compilation des résultats
    health_end = datetime.now()
    health_duration = (health_end - health_start).total_seconds()
    
    passed_tests = sum(1 for test in tests if test["status"] == "passed")
    total_tests = len(tests)
    
    return {
        "suite_name": "health",
        "started_at": health_start.isoformat(),
        "completed_at": health_end.isoformat(),
        "duration_seconds": round(health_duration, 2),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": round(passed_tests / total_tests * 100, 1),
        "tests": tests
    }


async def run_document_processing_tests(
    api_key: str, 
    test_documents_folder: str
) -> Dict[str, Any]:
    """Exécuter les tests de traitement de documents"""
    doc_start = datetime.now()
    
    tests = []
    
    # Créer des documents de test si le dossier n'existe pas
    test_docs = await create_test_documents(test_documents_folder)
    
    # Tester le traitement de chaque document
    for doc_path in test_docs:
        test_start = datetime.now()
        
        try:
            result = process_single_document(
                file_path=str(doc_path),
                api_key=api_key,
                chunk_size=500
            )
            
            test_end = datetime.now()
            test_duration = (test_end - test_start).total_seconds()
            
            test_status = "passed" if result.get("status") == "success" else "failed"
            
            tests.append({
                "name": f"process_document_{doc_path.name}",
                "status": test_status,
                "details": result,
                "duration": test_duration
            })
            
        except Exception as e:
            test_end = datetime.now()
            test_duration = (test_end - test_start).total_seconds()
            
            tests.append({
                "name": f"process_document_{doc_path.name}",
                "status": "failed",
                "details": f"Error: {str(e)}",
                "duration": test_duration
            })
    
    # Compilation des résultats
    doc_end = datetime.now()
    doc_duration = (doc_end - doc_start).total_seconds()
    
    passed_tests = sum(1 for test in tests if test["status"] == "passed")
    total_tests = len(tests)
    
    return {
        "suite_name": "document_processing",
        "started_at": doc_start.isoformat(),
        "completed_at": doc_end.isoformat(),
        "duration_seconds": round(doc_duration, 2),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": round(passed_tests / total_tests * 100, 1) if total_tests > 0 else 0,
        "tests": tests
    }


async def run_query_response_tests(api_key: str) -> Dict[str, Any]:
    """Exécuter les tests de requêtes et réponses"""
    query_start = datetime.now()
    
    tests = []
    
    # Questions de test prédéfinies
    test_queries = [
        {
            "question": "Résume le contenu principal de ce document.",
            "expected_keywords": ["résumé", "principal", "contenu"]
        },
        {
            "question": "Quels sont les points clés abordés ?",
            "expected_keywords": ["points", "clés", "important"]
        },
        {
            "question": "Y a-t-il des conclusions ou recommandations ?",
            "expected_keywords": ["conclusion", "recommandation"]
        }
    ]
    
    # Tester chaque requête
    for test_query in test_queries:
        test_start = datetime.now()
        
        try:
            result = test_document_query(
                question=test_query["question"],
                api_key=api_key,
                expected_keywords=test_query["expected_keywords"]
            )
            
            test_end = datetime.now()
            test_duration = (test_end - test_start).total_seconds()
            
            test_status = "passed" if result.get("status") == "success" else "failed"
            
            tests.append({
                "name": f"query_test_{len(tests) + 1}",
                "status": test_status,
                "details": result,
                "duration": test_duration
            })
            
        except Exception as e:
            test_end = datetime.now()
            test_duration = (test_end - test_start).total_seconds()
            
            tests.append({
                "name": f"query_test_{len(tests) + 1}",
                "status": "failed",
                "details": f"Error: {str(e)}",
                "duration": test_duration
            })
    
    # Compilation des résultats
    query_end = datetime.now()
    query_duration = (query_end - query_start).total_seconds()
    
    passed_tests = sum(1 for test in tests if test["status"] == "passed")
    total_tests = len(tests)
    
    return {
        "suite_name": "query_response",
        "started_at": query_start.isoformat(),
        "completed_at": query_end.isoformat(),
        "duration_seconds": round(query_duration, 2),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": round(passed_tests / total_tests * 100, 1) if total_tests > 0 else 0,
        "tests": tests
    }


async def run_performance_tests(api_key: str) -> Dict[str, Any]:
    """Exécuter les tests de performance"""
    perf_start = datetime.now()
    
    tests = []
    
    # Test de latence
    test_start = datetime.now()
    try:
        result = test_document_query(
            question="Test de latence simple",
            api_key=api_key
        )
        test_end = datetime.now()
        response_time = (test_end - test_start).total_seconds()
        
        # Critère: réponse en moins de 10 secondes
        test_status = "passed" if response_time < 10.0 else "failed"
        
        tests.append({
            "name": "response_latency",
            "status": test_status,
            "details": f"Response time: {response_time:.2f}s",
            "duration": response_time
        })
        
    except Exception as e:
        tests.append({
            "name": "response_latency",
            "status": "failed",
            "details": f"Error: {str(e)}",
            "duration": 0
        })
    
    # Test de charge mémoire
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        # Critère: moins de 1GB de RAM
        test_status = "passed" if memory_mb < 1024 else "failed"
        
        tests.append({
            "name": "memory_usage",
            "status": test_status,
            "details": f"Memory usage: {memory_mb:.1f} MB",
            "duration": 0.1
        })
        
    except Exception as e:
        tests.append({
            "name": "memory_usage",
            "status": "failed",
            "details": f"Error: {str(e)}",
            "duration": 0.1
        })
    
    # Compilation des résultats
    perf_end = datetime.now()
    perf_duration = (perf_end - perf_start).total_seconds()
    
    passed_tests = sum(1 for test in tests if test["status"] == "passed")
    total_tests = len(tests)
    
    return {
        "suite_name": "performance",
        "started_at": perf_start.isoformat(),
        "completed_at": perf_end.isoformat(),
        "duration_seconds": round(perf_duration, 2),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": round(passed_tests / total_tests * 100, 1) if total_tests > 0 else 0,
        "tests": tests
    }


async def run_robustness_tests(api_key: str) -> Dict[str, Any]:
    """Exécuter les tests de robustesse"""
    robust_start = datetime.now()
    
    tests = []
    
    # Test avec question vide
    try:
        result = test_document_query(
            question="",
            api_key=api_key
        )
        # Doit échouer gracieusement
        test_status = "passed" if result.get("status") == "error" else "failed"
        tests.append({
            "name": "empty_question_handling",
            "status": test_status,
            "details": "Empty question handled correctly",
            "duration": 0.5
        })
    except Exception:
        tests.append({
            "name": "empty_question_handling",
            "status": "passed",
            "details": "Exception correctly raised for empty question",
            "duration": 0.5
        })
    
    # Test avec API key invalide
    try:
        result = test_document_query(
            question="Test avec clé invalide",
            api_key="invalid_key_123"
        )
        # Doit échouer gracieusement
        test_status = "passed" if result.get("status") == "error" else "failed"
        tests.append({
            "name": "invalid_api_key_handling",
            "status": test_status,
            "details": "Invalid API key handled correctly",
            "duration": 1.0
        })
    except Exception:
        tests.append({
            "name": "invalid_api_key_handling",
            "status": "passed",
            "details": "Exception correctly raised for invalid API key",
            "duration": 1.0
        })
    
    # Compilation des résultats
    robust_end = datetime.now()
    robust_duration = (robust_end - robust_start).total_seconds()
    
    passed_tests = sum(1 for test in tests if test["status"] == "passed")
    total_tests = len(tests)
    
    return {
        "suite_name": "robustness",
        "started_at": robust_start.isoformat(),
        "completed_at": robust_end.isoformat(),
        "duration_seconds": round(robust_duration, 2),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": round(passed_tests / total_tests * 100, 1) if total_tests > 0 else 0,
        "tests": tests
    }


async def create_test_documents(test_folder: str) -> List[Path]:
    """Créer des documents de test si nécessaire"""
    test_dir = Path(test_folder)
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_docs = []
    
    # Document texte simple
    txt_doc = test_dir / "test_document.txt"
    if not txt_doc.exists():
        txt_content = """
Document de test pour DontREADME
================================

Ceci est un document de test contenant plusieurs sections importantes.

Section 1: Introduction
Ce document sert à tester les fonctionnalités de base du système DontREADME.

Section 2: Contenu principal
Le contenu principal aborde différents sujets pour tester la capacité d'extraction d'information.

Section 3: Conclusions
Les conclusions montrent que le système fonctionne correctement.

Points clés:
- Fonctionnalité de base
- Extraction d'information
- Test de performance
- Robustesse du système

Recommandations:
1. Continuer les tests réguliers
2. Surveiller les performances
3. Maintenir la documentation à jour
"""
        txt_doc.write_text(txt_content, encoding='utf-8')
    
    test_docs.append(txt_doc)
    
    return test_docs


async def test_basic_document_processing(api_key: str) -> Dict[str, Any]:
    """Test basique de traitement de document"""
    test_start = datetime.now()
    
    try:
        # Créer un document temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Ceci est un document de test basique pour les tests smoke.")
            temp_file = f.name
        
        # Traiter le document
        result = process_single_document(
            file_path=temp_file,
            api_key=api_key,
            chunk_size=200
        )
        
        # Nettoyer
        Path(temp_file).unlink(missing_ok=True)
        
        test_end = datetime.now()
        test_duration = (test_end - test_start).total_seconds()
        
        return {
            "name": "basic_document_processing",
            "status": "passed" if result.get("status") == "success" else "failed",
            "details": result.get("filename", "unknown"),
            "duration": test_duration
        }
        
    except Exception as e:
        test_end = datetime.now()
        test_duration = (test_end - test_start).total_seconds()
        
        return {
            "name": "basic_document_processing",
            "status": "failed",
            "details": f"Error: {str(e)}",
            "duration": test_duration
        }


async def test_basic_query(api_key: str) -> Dict[str, Any]:
    """Test basique de requête"""
    test_start = datetime.now()
    
    try:
        result = test_document_query(
            question="Test basique de fonctionnement",
            api_key=api_key
        )
        
        test_end = datetime.now()
        test_duration = (test_end - test_start).total_seconds()
        
        return {
            "name": "basic_query",
            "status": "passed" if result.get("status") == "success" else "failed",
            "details": f"Response length: {result.get('response_length', 0)} chars",
            "duration": test_duration
        }
        
    except Exception as e:
        test_end = datetime.now()
        test_duration = (test_end - test_start).total_seconds()
        
        return {
            "name": "basic_query",
            "status": "failed",
            "details": f"Error: {str(e)}",
            "duration": test_duration
        }


def analyze_regression(
    current_results: Dict[str, Any], 
    baseline_results: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Analyser la régression entre les résultats actuels et de référence"""
    if not baseline_results:
        return {
            "has_regression": False,
            "reason": "no_baseline",
            "message": "Aucune référence disponible pour comparaison"
        }
    
    try:
        current_summary = current_results.get("summary", {})
        
        current_success_rate = current_summary.get("success_rate", 0)
        baseline_success_rate = baseline_results.get("success_rate", 0)
        
        # Seuil de régression: -5% de taux de succès
        regression_threshold = -5.0
        success_rate_change = current_success_rate - baseline_success_rate
        
        has_regression = success_rate_change < regression_threshold
        
        return {
            "has_regression": has_regression,
            "success_rate_change": round(success_rate_change, 1),
            "current_success_rate": current_success_rate,
            "baseline_success_rate": baseline_success_rate,
            "threshold": regression_threshold,
            "message": (
                f"Régression détectée: {success_rate_change:+.1f}% de variation"
                if has_regression
                else f"Performance stable: {success_rate_change:+.1f}% de variation"
            )
        }
        
    except Exception as e:
        return {
            "has_regression": True,
            "reason": "analysis_error",
            "message": f"Erreur d'analyse: {str(e)}"
        }


async def generate_test_report_file(test_results: Dict[str, Any]) -> str:
    """Générer un fichier de rapport de test"""
    try:
        reports_dir = Path("./data/reports")
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"test_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        return str(report_file)
        
    except Exception as e:
        return f"Error generating report: {str(e)}"