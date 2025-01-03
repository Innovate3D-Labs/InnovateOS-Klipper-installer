from typing import Dict, Optional, List
import logging
import traceback
import json
import time
from datetime import datetime
from pathlib import Path
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class ErrorTracker:
    def __init__(self, log_dir: Path, sentry_dsn: Optional[str] = None):
        self.log_dir = log_dir
        self.sentry_dsn = sentry_dsn
        self.error_log_path = log_dir / "errors.log"
        self.error_queue: asyncio.Queue = asyncio.Queue()
        self.processing = False
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

    async def start(self):
        """Start error processing"""
        self.processing = True
        asyncio.create_task(self._process_error_queue())

    async def stop(self):
        """Stop error processing"""
        self.processing = False
        await self.error_queue.join()

    async def track_error(
        self,
        error: Exception,
        component: str,
        user_id: Optional[str] = None,
        context: Optional[Dict] = None
    ):
        """Track an error occurrence"""
        try:
            error_data = self._prepare_error_data(error, component, user_id, context)
            await self.error_queue.put(error_data)
            
            # Log error immediately
            logger.error(
                f"Error in {component}: {str(error)}",
                exc_info=error,
                extra={"context": context}
            )
        except Exception as e:
            logger.error(f"Failed to track error: {e}")

    def _prepare_error_data(
        self,
        error: Exception,
        component: str,
        user_id: Optional[str],
        context: Optional[Dict]
    ) -> Dict:
        """Prepare error data for tracking"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "message": str(error),
            "stacktrace": traceback.format_exc(),
            "component": component,
            "user_id": user_id,
            "context": context or {},
            "environment": "production"  # TODO: Make configurable
        }

    async def _process_error_queue(self):
        """Process queued errors"""
        while self.processing:
            try:
                error_data = await self.error_queue.get()
                
                # Write to local log
                await self._write_to_log(error_data)
                
                # Send to Sentry if configured
                if self.sentry_dsn:
                    await self._send_to_sentry(error_data)
                
                self.error_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing error queue: {e}")
            await asyncio.sleep(0.1)

    async def _write_to_log(self, error_data: Dict):
        """Write error to local log file"""
        try:
            async with aiofiles.open(self.error_log_path, "a") as f:
                await f.write(json.dumps(error_data) + "\n")
        except Exception as e:
            logger.error(f"Failed to write error to log: {e}")

    async def _send_to_sentry(self, error_data: Dict):
        """Send error to Sentry"""
        if not self.sentry_dsn:
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.sentry_dsn,
                    json=error_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"Failed to send error to Sentry: {response.status}"
                        )
        except Exception as e:
            logger.error(f"Failed to send error to Sentry: {e}")

    async def get_recent_errors(
        self,
        limit: int = 100,
        component: Optional[str] = None
    ) -> List[Dict]:
        """Get recent errors from log"""
        try:
            errors = []
            async with aiofiles.open(self.error_log_path, "r") as f:
                async for line in f:
                    try:
                        error = json.loads(line)
                        if component and error["component"] != component:
                            continue
                        errors.append(error)
                        if len(errors) >= limit:
                            break
                    except json.JSONDecodeError:
                        continue
            return errors
        except Exception as e:
            logger.error(f"Failed to get recent errors: {e}")
            return []

    async def get_error_stats(
        self,
        time_range: int = 3600
    ) -> Dict:
        """Get error statistics for the specified time range"""
        try:
            stats = {
                "total_errors": 0,
                "error_types": {},
                "components": {},
                "users_affected": set()
            }
            
            current_time = time.time()
            cutoff_time = current_time - time_range
            
            async with aiofiles.open(self.error_log_path, "r") as f:
                async for line in f:
                    try:
                        error = json.loads(line)
                        error_time = datetime.fromisoformat(
                            error["timestamp"]
                        ).timestamp()
                        
                        if error_time < cutoff_time:
                            continue
                        
                        stats["total_errors"] += 1
                        
                        # Track error types
                        error_type = error["error_type"]
                        stats["error_types"][error_type] = \
                            stats["error_types"].get(error_type, 0) + 1
                        
                        # Track components
                        component = error["component"]
                        stats["components"][component] = \
                            stats["components"].get(component, 0) + 1
                        
                        # Track affected users
                        if error["user_id"]:
                            stats["users_affected"].add(error["user_id"])
                    except json.JSONDecodeError:
                        continue
            
            # Convert user set to count
            stats["users_affected"] = len(stats["users_affected"])
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get error stats: {e}")
            return {
                "total_errors": 0,
                "error_types": {},
                "components": {},
                "users_affected": 0
            }

error_tracker = ErrorTracker(Path("logs"))
