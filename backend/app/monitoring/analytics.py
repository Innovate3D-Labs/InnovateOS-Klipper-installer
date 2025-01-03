from typing import Dict, Optional, List
import logging
import json
from datetime import datetime, timedelta
import aiofiles
from pathlib import Path
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)

class UserAnalytics:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.events_path = data_dir / "events.log"
        self.sessions_path = data_dir / "sessions.log"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def track_event(
        self,
        event_type: str,
        user_id: Optional[str],
        properties: Optional[Dict] = None
    ):
        """Track a user event"""
        try:
            event_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "user_id": user_id,
                "properties": properties or {}
            }
            
            async with aiofiles.open(self.events_path, "a") as f:
                await f.write(json.dumps(event_data) + "\n")
        except Exception as e:
            logger.error(f"Failed to track event: {e}")

    async def track_session(
        self,
        user_id: str,
        session_id: str,
        action: str,
        properties: Optional[Dict] = None
    ):
        """Track session activity"""
        try:
            session_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "session_id": session_id,
                "action": action,
                "properties": properties or {}
            }
            
            async with aiofiles.open(self.sessions_path, "a") as f:
                await f.write(json.dumps(session_data) + "\n")
        except Exception as e:
            logger.error(f"Failed to track session: {e}")

    async def get_event_stats(
        self,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict:
        """Get event statistics"""
        try:
            stats = {
                "total_events": 0,
                "event_types": defaultdict(int),
                "unique_users": set(),
                "hourly_distribution": defaultdict(int)
            }
            
            cutoff_time = datetime.utcnow() - time_range
            
            async with aiofiles.open(self.events_path, "r") as f:
                async for line in f:
                    try:
                        event = json.loads(line)
                        event_time = datetime.fromisoformat(event["timestamp"])
                        
                        if event_time < cutoff_time:
                            continue
                        
                        stats["total_events"] += 1
                        stats["event_types"][event["event_type"]] += 1
                        
                        if event["user_id"]:
                            stats["unique_users"].add(event["user_id"])
                        
                        hour = event_time.hour
                        stats["hourly_distribution"][hour] += 1
                    except json.JSONDecodeError:
                        continue
            
            # Convert sets to counts
            stats["unique_users"] = len(stats["unique_users"])
            
            return dict(stats)
        except Exception as e:
            logger.error(f"Failed to get event stats: {e}")
            return {
                "total_events": 0,
                "event_types": {},
                "unique_users": 0,
                "hourly_distribution": {}
            }

    async def get_session_stats(
        self,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict:
        """Get session statistics"""
        try:
            stats = {
                "total_sessions": 0,
                "unique_users": set(),
                "session_duration": [],
                "bounce_rate": 0
            }
            
            sessions = defaultdict(list)
            cutoff_time = datetime.utcnow() - time_range
            
            async with aiofiles.open(self.sessions_path, "r") as f:
                async for line in f:
                    try:
                        session = json.loads(line)
                        session_time = datetime.fromisoformat(session["timestamp"])
                        
                        if session_time < cutoff_time:
                            continue
                        
                        session_id = session["session_id"]
                        sessions[session_id].append(session)
                        
                        if session["user_id"]:
                            stats["unique_users"].add(session["user_id"])
                    except json.JSONDecodeError:
                        continue
            
            # Calculate session metrics
            for session_id, events in sessions.items():
                stats["total_sessions"] += 1
                
                if len(events) == 1:
                    stats["bounce_rate"] += 1
                    continue
                
                # Sort events by timestamp
                events.sort(key=lambda x: datetime.fromisoformat(x["timestamp"]))
                
                # Calculate duration
                start_time = datetime.fromisoformat(events[0]["timestamp"])
                end_time = datetime.fromisoformat(events[-1]["timestamp"])
                duration = (end_time - start_time).total_seconds()
                stats["session_duration"].append(duration)
            
            # Calculate averages and rates
            stats["unique_users"] = len(stats["unique_users"])
            stats["bounce_rate"] = (
                stats["bounce_rate"] / stats["total_sessions"]
                if stats["total_sessions"] > 0 else 0
            )
            stats["avg_session_duration"] = (
                sum(stats["session_duration"]) / len(stats["session_duration"])
                if stats["session_duration"] else 0
            )
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {
                "total_sessions": 0,
                "unique_users": 0,
                "bounce_rate": 0,
                "avg_session_duration": 0
            }

    async def get_user_journey(self, user_id: str) -> List[Dict]:
        """Get user journey/flow through the application"""
        try:
            journey = []
            
            async with aiofiles.open(self.events_path, "r") as f:
                async for line in f:
                    try:
                        event = json.loads(line)
                        if event["user_id"] == user_id:
                            journey.append({
                                "timestamp": event["timestamp"],
                                "event_type": event["event_type"],
                                "properties": event["properties"]
                            })
                    except json.JSONDecodeError:
                        continue
            
            # Sort by timestamp
            journey.sort(key=lambda x: datetime.fromisoformat(x["timestamp"]))
            return journey
        except Exception as e:
            logger.error(f"Failed to get user journey: {e}")
            return []

analytics = UserAnalytics(Path("data/analytics"))
