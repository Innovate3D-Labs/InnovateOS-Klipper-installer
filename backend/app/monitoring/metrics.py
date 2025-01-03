from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Dict, Optional
import psutil
import time
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        # System Metrics
        self.cpu_usage = Gauge(
            'system_cpu_usage',
            'CPU usage in percent'
        )
        self.memory_usage = Gauge(
            'system_memory_usage',
            'Memory usage in bytes'
        )
        self.disk_usage = Gauge(
            'system_disk_usage',
            'Disk usage in bytes'
        )

        # Installation Metrics
        self.installations_total = Counter(
            'installations_total',
            'Total number of installations',
            ['status']
        )
        self.installation_duration = Histogram(
            'installation_duration_seconds',
            'Time taken for installation',
            buckets=[60, 120, 300, 600, 1200]
        )
        self.active_installations = Gauge(
            'active_installations',
            'Number of active installations'
        )

        # Hardware Metrics
        self.detected_boards = Gauge(
            'detected_boards',
            'Number of detected printer boards'
        )
        self.board_detection_time = Histogram(
            'board_detection_time_seconds',
            'Time taken for board detection',
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )

        # Error Metrics
        self.errors_total = Counter(
            'errors_total',
            'Total number of errors',
            ['type', 'component']
        )
        self.error_rate = Gauge(
            'error_rate',
            'Rate of errors per minute'
        )

        # Performance Metrics
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
        )
        self.request_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )

        # Version Info
        self.version_info = Info(
            'application_info',
            'Application version information'
        )

    def collect_system_metrics(self):
        """Collect system metrics"""
        try:
            # CPU Usage
            self.cpu_usage.set(psutil.cpu_percent())

            # Memory Usage
            memory = psutil.virtual_memory()
            self.memory_usage.set(memory.used)

            # Disk Usage
            disk = psutil.disk_usage('/')
            self.disk_usage.set(disk.used)
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            self.errors_total.labels(type='system', component='metrics').inc()

    def track_installation(self, status: str, duration: float):
        """Track installation metrics"""
        try:
            self.installations_total.labels(status=status).inc()
            self.installation_duration.observe(duration)
        except Exception as e:
            logger.error(f"Error tracking installation: {e}")
            self.errors_total.labels(type='tracking', component='installation').inc()

    def update_active_installations(self, count: int):
        """Update active installations count"""
        self.active_installations.set(count)

    def track_board_detection(self, count: int, duration: float):
        """Track board detection metrics"""
        try:
            self.detected_boards.set(count)
            self.board_detection_time.observe(duration)
        except Exception as e:
            logger.error(f"Error tracking board detection: {e}")
            self.errors_total.labels(type='tracking', component='board_detection').inc()

    def track_error(self, error_type: str, component: str):
        """Track error occurrence"""
        try:
            self.errors_total.labels(type=error_type, component=component).inc()
            self._update_error_rate()
        except Exception as e:
            logger.error(f"Error tracking error: {e}")

    def _update_error_rate(self):
        """Update error rate calculation"""
        try:
            # Calculate error rate over last minute
            current_time = time.time()
            one_minute_ago = current_time - 60
            
            recent_errors = sum(
                1 for t in self.errors_total._value.values()
                if t > one_minute_ago
            )
            
            self.error_rate.set(recent_errors / 60)
        except Exception as e:
            logger.error(f"Error updating error rate: {e}")

    def track_request(self, method: str, endpoint: str, status: int, duration: float):
        """Track HTTP request metrics"""
        try:
            self.request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            self.request_total.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()
        except Exception as e:
            logger.error(f"Error tracking request: {e}")
            self.errors_total.labels(type='tracking', component='request').inc()

    def set_version(self, version: str, build: str):
        """Set application version information"""
        try:
            self.version_info.info({
                'version': version,
                'build': build
            })
        except Exception as e:
            logger.error(f"Error setting version info: {e}")
            self.errors_total.labels(type='system', component='version').inc()

metrics_collector = MetricsCollector()
