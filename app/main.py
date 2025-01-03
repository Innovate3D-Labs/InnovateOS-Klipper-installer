from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import logging
import os

from app.routers import boards, config, installation
from app.core.config import settings
from app.core.logging import setup_logging
from app.websocket.connection import ConnectionManager
from app.websocket.events import EventTypes

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="InnovateOS Klipper Installer",
    description="API for installing and configuring Klipper firmware",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
manager = ConnectionManager()

# Include routers
app.include_router(boards.router, prefix="/api/boards", tags=["boards"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(installation.router, prefix="/api/install", tags=["installation"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")
            event_data = data.get("data")

            if event_type == EventTypes.INSTALLATION_STATUS:
                # Broadcast installation status to all connected clients
                await manager.broadcast_json({
                    "type": EventTypes.INSTALLATION_STATUS,
                    "data": event_data
                })
            elif event_type == EventTypes.INSTALLATION_LOG:
                # Broadcast log message to all connected clients
                await manager.broadcast_json({
                    "type": EventTypes.INSTALLATION_LOG,
                    "data": event_data
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await manager.disconnect(websocket)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "message": "An unexpected error occurred",
            "details": str(exc) if settings.DEBUG else None
        }
    )

@app.on_event("startup")
async def startup_event():
    logger.info("Starting InnovateOS Klipper Installer API")
    # Initialize any required services here

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down InnovateOS Klipper Installer API")
    # Cleanup any resources here
