import asyncio
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.installation_status: Dict[str, Any] = {
            "progress": 0,
            "step": "",
            "message": "",
            "error": None,
            "log": []
        }

    async def connect(self, websocket: WebSocket):
        """Neue WebSocket-Verbindung herstellen"""
        await websocket.accept()
        self.active_connections.add(websocket)
        # Aktuellen Status an den neuen Client senden
        await self.send_personal_message(self.installation_status, websocket)

    def disconnect(self, websocket: WebSocket):
        """WebSocket-Verbindung trennen"""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Nachricht an alle verbundenen Clients senden"""
        # Status aktualisieren
        self.installation_status.update(message)
        
        # Log-Einträge verwalten
        if "log" in message:
            self.installation_status["log"].append(message["log"])
            # Maximale Anzahl von Log-Einträgen begrenzen
            if len(self.installation_status["log"]) > 1000:
                self.installation_status["log"] = self.installation_status["log"][-1000:]

        # Nachricht an alle Clients senden
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(self.installation_status)
            except Exception as e:
                logger.error(f"Fehler beim Senden der Nachricht: {str(e)}")
                disconnected.add(connection)
        
        # Getrennte Verbindungen entfernen
        for connection in disconnected:
            self.disconnect(connection)

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Nachricht an einen spezifischen Client senden"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Fehler beim Senden der persönlichen Nachricht: {str(e)}")
            self.disconnect(websocket)

    async def send_installation_update(self, 
                                     step: str, 
                                     message: str, 
                                     progress: int, 
                                     error: Optional[str] = None,
                                     log: Optional[str] = None):
        """Installation-Update senden"""
        update = {
            "step": step,
            "message": message,
            "progress": progress
        }
        
        if error:
            update["error"] = error
        
        if log:
            update["log"] = log
        
        await self.broadcast(update)

    def get_status(self) -> Dict[str, Any]:
        """Aktuellen Installationsstatus abrufen"""
        return self.installation_status.copy()

    async def clear_status(self):
        """Installationsstatus zurücksetzen"""
        self.installation_status = {
            "progress": 0,
            "step": "",
            "message": "",
            "error": None,
            "log": []
        }
        await self.broadcast(self.installation_status)
