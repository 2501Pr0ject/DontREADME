"""
Workflows Prefect pour DontREADME

Ce module contient les workflows d'orchestration automatisés :
- Traitement en lot de documents
- Maintenance et optimisation
- Monitoring et alertes
- Tests automatisés
"""

from .batch_processing import batch_document_flow, process_folder_documents, nightly_batch_processing
from .maintenance import database_maintenance_flow, cleanup_old_files_flow, weekly_maintenance_flow
from .monitoring import health_check_flow, performance_monitoring_flow, continuous_monitoring_flow
from .testing import automated_testing_flow, regression_testing_flow, smoke_testing_flow

__version__ = "1.0.0"
__all__ = [
    # Batch processing
    "batch_document_flow",
    "process_folder_documents",
    "nightly_batch_processing",
    
    # Maintenance
    "database_maintenance_flow", 
    "cleanup_old_files_flow",
    "weekly_maintenance_flow",
    
    # Monitoring
    "health_check_flow",
    "performance_monitoring_flow",
    "continuous_monitoring_flow",
    
    # Testing
    "automated_testing_flow",
    "regression_testing_flow",
    "smoke_testing_flow"
]