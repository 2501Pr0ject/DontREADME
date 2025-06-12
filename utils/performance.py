import time
import psutil
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class PerformanceMetrics:
    """Structure pour stocker les métriques de performance"""
    timestamp: datetime
    operation: str
    duration: float
    memory_usage: float
    cpu_usage: float
    success: bool
    error_message: Optional[str] = None

class PerformanceMonitor:
    """
    Moniteur de performance pour l'application
    """
    
    def __init__(self, max_history: int = 100):
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history = max_history
        self._lock = threading.Lock()
    
    def measure_performance(self, operation_name: str):
        """
        Décorateur pour mesurer les performances d'une fonction
        """
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                start_cpu = psutil.cpu_percent()
                
                success = True
                error_message = None
                result = None
                
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    success = False
                    error_message = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    duration = end_time - start_time
                    
                    # Mesure CPU pendant l'opération (approximation)
                    cpu_usage = psutil.cpu_percent()
                    
                    metrics = PerformanceMetrics(
                        timestamp=datetime.now(),
                        operation=operation_name,
                        duration=duration,
                        memory_usage=end_memory - start_memory,
                        cpu_usage=cpu_usage,
                        success=success,
                        error_message=error_message
                    )
                    
                    self._add_metrics(metrics)
                
                return result
            return wrapper
        return decorator
    
    def _add_metrics(self, metrics: PerformanceMetrics):
        """Ajoute des métriques à l'historique"""
        with self._lock:
            self.metrics_history.append(metrics)
            
            # Limiter la taille de l'historique
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]
    
    def get_metrics_summary(self, 
                           operation: Optional[str] = None,
                           last_n_minutes: Optional[int] = None) -> Dict:
        """
        Retourne un résumé des métriques
        """
        with self._lock:
            filtered_metrics = self.metrics_history.copy()
        
        # Filtrage par opération
        if operation:
            filtered_metrics = [m for m in filtered_metrics if m.operation == operation]
        
        # Filtrage temporel
        if last_n_minutes:
            cutoff_time = datetime.now() - timedelta(minutes=last_n_minutes)
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= cutoff_time]
        
        if not filtered_metrics:
            return {"message": "Aucune métrique disponible"}
        
        # Calculs statistiques
        durations = [m.duration for m in filtered_metrics]
        memory_usages = [m.memory_usage for m in filtered_metrics]
        success_count = sum(1 for m in filtered_metrics if m.success)
        
        summary = {
            "total_operations": len(filtered_metrics),
            "success_rate": success_count / len(filtered_metrics) * 100,
            "avg_duration": sum(durations) / len(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "avg_memory_usage": sum(memory_usages) / len(memory_usages),
            "max_memory_usage": max(memory_usages),
            "recent_errors": [
                {"operation": m.operation, "error": m.error_message, "timestamp": m.timestamp}
                for m in filtered_metrics[-5:] if not m.success
            ]
        }
        
        return summary
    
    def get_system_info(self) -> Dict:
        """Retourne les informations système actuelles"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_gb": psutil.virtual_memory().available / 1024 / 1024 / 1024,
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "timestamp": datetime.now().isoformat()
        }
    
    def export_metrics(self, filepath: str):
        """Exporte les métriques vers un fichier JSON"""
        import json
        
        with self._lock:
            data = {
                "export_timestamp": datetime.now().isoformat(),
                "metrics": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "operation": m.operation,
                        "duration": m.duration,
                        "memory_usage": m.memory_usage,
                        "cpu_usage": m.cpu_usage,
                        "success": m.success,
                        "error_message": m.error_message
                    }
                    for m in self.metrics_history
                ]
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def clear_metrics(self):
        """Efface l'historique des métriques"""
        with self._lock:
            self.metrics_history.clear()

# Exemple d'utilisation du moniteur de performance
def create_performance_monitor():
    """Factory function pour créer un moniteur de performance"""
    return PerformanceMonitor(max_history=200)