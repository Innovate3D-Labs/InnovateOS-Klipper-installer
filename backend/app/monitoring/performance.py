from typing import Dict, Optional, List
import logging
import time
import asyncio
import psutil
from datetime import datetime, timedelta
from collections import deque
import statistics

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self, window_size: int = 3600):
        self.window_size = window_size  # 1 hour default
        
        # Performance metrics storage
        self.response_times = deque(maxlen=window_size)
        self.cpu_usage = deque(maxlen=window_size)
        self.memory_usage = deque(maxlen=window_size)
        self.request_rates = deque(maxlen=window_size)
        
        # Endpoint specific metrics
        self.endpoint_metrics: Dict[str, Dict] = {}
        
        # Background task for collecting system metrics
        self.running = False
        self.collection_task = None

    async def start(self):
        """Start performance monitoring"""
        self.running = True
        self.collection_task = asyncio.create_task(self._collect_system_metrics())

    async def stop(self):
        """Stop performance monitoring"""
        self.running = False
        if self.collection_task:
            await self.collection_task

    async def _collect_system_metrics(self):
        """Collect system metrics periodically"""
        while self.running:
            try:
                # CPU Usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_usage.append((time.time(), cpu_percent))

                # Memory Usage
                memory = psutil.virtual_memory()
                self.memory_usage.append((time.time(), memory.percent))

                # Wait before next collection
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(5)  # Wait longer on error

    def track_request(
        self,
        endpoint: str,
        method: str,
        duration: float,
        status_code: int
    ):
        """Track HTTP request performance"""
        try:
            timestamp = time.time()
            
            # Overall response times
            self.response_times.append((timestamp, duration))
            
            # Update request rate
            self.request_rates.append(timestamp)
            
            # Update endpoint specific metrics
            if endpoint not in self.endpoint_metrics:
                self.endpoint_metrics[endpoint] = {
                    "response_times": deque(maxlen=self.window_size),
                    "status_codes": deque(maxlen=self.window_size),
                    "methods": deque(maxlen=self.window_size)
                }
            
            metrics = self.endpoint_metrics[endpoint]
            metrics["response_times"].append((timestamp, duration))
            metrics["status_codes"].append((timestamp, status_code))
            metrics["methods"].append((timestamp, method))
        except Exception as e:
            logger.error(f"Error tracking request: {e}")

    def get_current_metrics(self) -> Dict:
        """Get current performance metrics"""
        try:
            current_time = time.time()
            cutoff_time = current_time - 60  # Last minute
            
            # Calculate request rate
            recent_requests = sum(
                1 for t in self.request_rates
                if t > cutoff_time
            )
            
            # Get recent response times
            recent_response_times = [
                duration for t, duration in self.response_times
                if t > cutoff_time
            ]
            
            metrics = {
                "request_rate": recent_requests / 60,  # requests per second
                "response_time": {
                    "avg": statistics.mean(recent_response_times) if recent_response_times else 0,
                    "p95": statistics.quantiles(recent_response_times, n=20)[18] if recent_response_times else 0,
                    "max": max(recent_response_times) if recent_response_times else 0
                },
                "system": {
                    "cpu": self.cpu_usage[-1][1] if self.cpu_usage else 0,
                    "memory": self.memory_usage[-1][1] if self.memory_usage else 0
                }
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {}

    def get_endpoint_metrics(self, endpoint: str) -> Dict:
        """Get metrics for specific endpoint"""
        try:
            if endpoint not in self.endpoint_metrics:
                return {}
            
            metrics = self.endpoint_metrics[endpoint]
            current_time = time.time()
            cutoff_time = current_time - 60
            
            # Get recent data
            recent_times = [
                duration for t, duration in metrics["response_times"]
                if t > cutoff_time
            ]
            
            recent_status = [
                status for t, status in metrics["status_codes"]
                if t > cutoff_time
            ]
            
            recent_methods = [
                method for t, method in metrics["methods"]
                if t > cutoff_time
            ]
            
            return {
                "response_time": {
                    "avg": statistics.mean(recent_times) if recent_times else 0,
                    "p95": statistics.quantiles(recent_times, n=20)[18] if recent_times else 0,
                    "max": max(recent_times) if recent_times else 0
                },
                "status_codes": {
                    str(status): recent_status.count(status)
                    for status in set(recent_status)
                },
                "methods": {
                    method: recent_methods.count(method)
                    for method in set(recent_methods)
                }
            }
        except Exception as e:
            logger.error(f"Error getting endpoint metrics: {e}")
            return {}

    def get_performance_history(
        self,
        duration: timedelta = timedelta(hours=1)
    ) -> Dict:
        """Get historical performance data"""
        try:
            current_time = time.time()
            cutoff_time = current_time - duration.total_seconds()
            
            # Prepare time series data
            time_series = []
            interval = duration.total_seconds() / 60  # 60 data points
            
            for i in range(60):
                start_time = cutoff_time + (i * interval)
                end_time = start_time + interval
                
                # Get data for this interval
                response_times = [
                    duration for t, duration in self.response_times
                    if start_time <= t < end_time
                ]
                
                cpu = [
                    usage for t, usage in self.cpu_usage
                    if start_time <= t < end_time
                ]
                
                memory = [
                    usage for t, usage in self.memory_usage
                    if start_time <= t < end_time
                ]
                
                time_series.append({
                    "timestamp": datetime.fromtimestamp(start_time).isoformat(),
                    "response_time": statistics.mean(response_times) if response_times else 0,
                    "cpu_usage": statistics.mean(cpu) if cpu else 0,
                    "memory_usage": statistics.mean(memory) if memory else 0,
                    "request_count": len(response_times)
                })
            
            return {
                "interval": interval,
                "data_points": time_series
            }
        except Exception as e:
            logger.error(f"Error getting performance history: {e}")
            return {}

performance_monitor = PerformanceMonitor()
