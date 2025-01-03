from fastapi import APIRouter, WebSocket, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging
from ..hardware.installation_manager import InstallationManager, InstallationStatus
from ..hardware.board_manager import Board
from ..core.websocket import WebSocketManager

router = APIRouter()
logger = logging.getLogger(__name__)

class InstallationRequest(BaseModel):
    board: Board
    config: dict

class InstallationResponse(BaseModel):
    installation_id: str

class InstallationStatusResponse(BaseModel):
    id: str
    status: str
    progress: int
    message: str
    start_time: datetime
    end_time: Optional[datetime]
    error: Optional[str]

@router.post("/installation/start")
async def start_installation(
    request: InstallationRequest,
    installation_manager: InstallationManager = Depends()
) -> InstallationResponse:
    """Start a new installation"""
    try:
        installation_id = await installation_manager.start_installation(
            request.board,
            request.config,
            "master"  # TODO: Make version configurable
        )
        
        if not installation_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to start installation"
            )
            
        return InstallationResponse(installation_id=installation_id)
    
    except Exception as e:
        logger.error(f"Failed to start installation: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/installation/{installation_id}/status")
async def get_installation_status(
    installation_id: str,
    installation_manager: InstallationManager = Depends()
) -> InstallationStatusResponse:
    """Get status of an installation"""
    status = installation_manager.get_status(installation_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail="Installation not found"
        )
        
    return InstallationStatusResponse(
        id=status.id,
        status=status.status,
        progress=status.progress,
        message=status.message,
        start_time=status.start_time,
        end_time=status.end_time,
        error=status.error
    )

@router.post("/installation/{installation_id}/cancel")
async def cancel_installation(
    installation_id: str,
    installation_manager: InstallationManager = Depends()
) -> dict:
    """Cancel an ongoing installation"""
    success = await installation_manager.cancel_installation(installation_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to cancel installation"
        )
        
    return {"status": "cancelled"}

@router.get("/installation/active")
async def get_active_installations(
    installation_manager: InstallationManager = Depends()
) -> List[InstallationStatusResponse]:
    """Get all active installations"""
    statuses = installation_manager.get_all_statuses()
    return [
        InstallationStatusResponse(
            id=status.id,
            status=status.status,
            progress=status.progress,
            message=status.message,
            start_time=status.start_time,
            end_time=status.end_time,
            error=status.error
        )
        for status in statuses
    ]

@router.websocket("/ws/installation/{installation_id}")
async def installation_websocket(
    websocket: WebSocket,
    installation_id: str,
    installation_manager: InstallationManager = Depends(),
    websocket_manager: WebSocketManager = Depends()
):
    """WebSocket endpoint for installation status updates"""
    await websocket_manager.connect(websocket)
    
    try:
        def status_callback(status: InstallationStatus):
            """Callback for installation status updates"""
            websocket_manager.broadcast({
                "type": "status_update",
                "installation_id": status.id,
                "status": status.status,
                "progress": status.progress,
                "message": status.message,
                "error": status.error
            })
        
        # Register callback
        installation_manager.register_status_callback(status_callback)
        
        # Send initial status
        status = installation_manager.get_status(installation_id)
        if status:
            await websocket.send_json({
                "type": "status_update",
                "installation_id": status.id,
                "status": status.status,
                "progress": status.progress,
                "message": status.message,
                "error": status.error
            })
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        installation_manager.status_callbacks.remove(status_callback)
        await websocket_manager.disconnect(websocket)
