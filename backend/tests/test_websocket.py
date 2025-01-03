import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from unittest.mock import AsyncMock, patch, MagicMock
import json
import asyncio
from typing import AsyncGenerator

from app.main import app
from app.websocket import WebSocketManager
from app.models.installation import InstallationStatus, InstallationLog

@pytest.fixture
def websocket_client():
    return TestClient(app)

@pytest.fixture
async def websocket_manager():
    manager = WebSocketManager()
    yield manager
    await manager.disconnect_all()

@pytest.fixture
def mock_websocket():
    ws = AsyncMock(spec=WebSocket)
    ws.send_text = AsyncMock()
    ws.receive_text = AsyncMock()
    ws.close = AsyncMock()
    return ws

@pytest.mark.asyncio
async def test_websocket_connection(websocket_manager, mock_websocket):
    # Test connection
    await websocket_manager.connect(mock_websocket)
    assert mock_websocket in websocket_manager.active_connections
    
    # Test disconnection
    await websocket_manager.disconnect(mock_websocket)
    assert mock_websocket not in websocket_manager.active_connections

@pytest.mark.asyncio
async def test_broadcast_message(websocket_manager):
    # Create multiple mock websockets
    mock_websockets = [AsyncMock(spec=WebSocket) for _ in range(3)]
    
    # Connect all mock websockets
    for ws in mock_websockets:
        await websocket_manager.connect(ws)
    
    # Test broadcasting
    test_message = {"type": "test", "data": "message"}
    await websocket_manager.broadcast(test_message)
    
    # Verify each websocket received the message
    for ws in mock_websockets:
        ws.send_text.assert_called_once_with(json.dumps(test_message))

@pytest.mark.asyncio
async def test_installation_status_updates(websocket_manager, mock_websocket):
    await websocket_manager.connect(mock_websocket)
    
    # Test status update
    status = InstallationStatus(
        status="downloading",
        message="Downloading firmware",
        progress=50
    )
    
    await websocket_manager.send_installation_status(status)
    
    expected_message = {
        "type": "installation_status",
        "data": status.dict()
    }
    mock_websocket.send_text.assert_called_once_with(
        json.dumps(expected_message)
    )

@pytest.mark.asyncio
async def test_installation_logs(websocket_manager, mock_websocket):
    await websocket_manager.connect(mock_websocket)
    
    # Test log message
    log = InstallationLog(
        level="info",
        message="Test log message",
        timestamp="2025-01-03T17:18:28Z"
    )
    
    await websocket_manager.send_installation_log(log)
    
    expected_message = {
        "type": "installation_log",
        "data": log.dict()
    }
    mock_websocket.send_text.assert_called_once_with(
        json.dumps(expected_message)
    )

@pytest.mark.asyncio
async def test_error_handling(websocket_manager, mock_websocket):
    await websocket_manager.connect(mock_websocket)
    
    # Simulate send error
    mock_websocket.send_text.side_effect = Exception("Send failed")
    
    # The manager should handle the error and remove the connection
    await websocket_manager.broadcast({"type": "test"})
    assert mock_websocket not in websocket_manager.active_connections

@pytest.mark.asyncio
async def test_concurrent_connections(websocket_manager):
    # Test multiple concurrent connections
    mock_websockets = [AsyncMock(spec=WebSocket) for _ in range(5)]
    
    # Connect all websockets concurrently
    await asyncio.gather(
        *[websocket_manager.connect(ws) for ws in mock_websockets]
    )
    
    assert len(websocket_manager.active_connections) == 5
    
    # Disconnect all websockets concurrently
    await asyncio.gather(
        *[websocket_manager.disconnect(ws) for ws in mock_websockets]
    )
    
    assert len(websocket_manager.active_connections) == 0

@pytest.mark.asyncio
async def test_message_queue(websocket_manager, mock_websocket):
    # Enable message queueing
    websocket_manager.enable_queue()
    
    # Queue some messages before connection
    test_messages = [
        {"type": "test", "id": i} for i in range(3)
    ]
    
    for msg in test_messages:
        await websocket_manager.broadcast(msg)
    
    # Connect websocket
    await websocket_manager.connect(mock_websocket)
    
    # Verify queued messages were sent
    assert mock_websocket.send_text.call_count == len(test_messages)
    for i, msg in enumerate(test_messages):
        mock_websocket.send_text.assert_any_call(json.dumps(msg))

@pytest.mark.asyncio
async def test_installation_progress_stream():
    async def mock_progress() -> AsyncGenerator[InstallationStatus, None]:
        statuses = [
            InstallationStatus(
                status="downloading",
                message="Downloading firmware",
                progress=0
            ),
            InstallationStatus(
                status="downloading",
                message="Downloading firmware",
                progress=50
            ),
            InstallationStatus(
                status="completed",
                message="Installation complete",
                progress=100
            )
        ]
        for status in statuses:
            yield status
            await asyncio.sleep(0.1)
    
    with patch('app.websocket.installation_progress', side_effect=mock_progress):
        mock_websocket = AsyncMock(spec=WebSocket)
        manager = WebSocketManager()
        
        # Start progress stream
        await manager.connect(mock_websocket)
        await manager.start_installation_progress("test_id")
        
        # Verify all status updates were sent
        assert mock_websocket.send_text.call_count == 3
        
        # Verify the final status was "completed"
        final_call = mock_websocket.send_text.call_args_list[-1]
        final_message = json.loads(final_call[0][0])
        assert final_message["data"]["status"] == "completed"
