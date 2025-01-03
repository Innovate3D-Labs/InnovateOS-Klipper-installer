import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import asyncio
from ..websocket_manager import WebSocketManager
from ..main import app

class MockWebSocket:
    def __init__(self):
        self.sent_messages = []
        self.closed = False
        self.accepted = False

    async def accept(self):
        self.accepted = True

    async def send_json(self, data):
        self.sent_messages.append(data)

    async def receive_text(self):
        return '{"type": "test"}'

    def __eq__(self, other):
        return id(self) == id(other)

@pytest.fixture
def ws_manager():
    return WebSocketManager()

@pytest.mark.asyncio
async def test_websocket_connection(ws_manager):
    """Test WebSocket-Verbindungsaufbau"""
    ws = MockWebSocket()
    await ws_manager.connect(ws)
    assert ws in ws_manager.active_connections
    assert ws.accepted

def test_websocket_disconnect(ws_manager):
    """Test WebSocket-Verbindungstrennung"""
    ws = MockWebSocket()
    ws_manager.active_connections.add(ws)
    ws_manager.disconnect(ws)
    assert ws not in ws_manager.active_connections

@pytest.mark.asyncio
async def test_broadcast_message(ws_manager):
    """Test Broadcast-Nachricht an alle Clients"""
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    await ws_manager.connect(ws1)
    await ws_manager.connect(ws2)

    test_message = {
        "step": "test",
        "message": "Test message",
        "progress": 50
    }
    await ws_manager.broadcast(test_message)

    assert len(ws1.sent_messages) == 2  # Initial status + broadcast
    assert len(ws2.sent_messages) == 2
    assert ws1.sent_messages[-1]["step"] == "test"
    assert ws2.sent_messages[-1]["step"] == "test"

@pytest.mark.asyncio
async def test_installation_update(ws_manager):
    """Test Installation-Updates"""
    ws = MockWebSocket()
    await ws_manager.connect(ws)

    await ws_manager.send_installation_update(
        step="test_step",
        message="Testing installation",
        progress=75,
        log="Test log message"
    )

    assert len(ws.sent_messages) == 2  # Initial status + update
    last_message = ws.sent_messages[-1]
    assert last_message["step"] == "test_step"
    assert last_message["progress"] == 75
    assert "Test log message" in last_message["log"]

@pytest.mark.asyncio
async def test_error_handling(ws_manager):
    """Test Fehlerbehandlung"""
    class FailingWebSocket(MockWebSocket):
        async def send_json(self, data):
            raise Exception("Test error")

    ws = FailingWebSocket()
    await ws_manager.connect(ws)
    
    # Sollte keine Exception werfen
    await ws_manager.broadcast({"test": "message"})
    assert ws not in ws_manager.active_connections

@pytest.mark.asyncio
async def test_status_management(ws_manager):
    """Test Statusverwaltung"""
    initial_status = ws_manager.get_status()
    assert initial_status["progress"] == 0
    assert not initial_status["error"]

    await ws_manager.send_installation_update(
        step="test",
        message="test",
        progress=25,
        error="Test error"
    )

    updated_status = ws_manager.get_status()
    assert updated_status["progress"] == 25
    assert updated_status["error"] == "Test error"

    await ws_manager.clear_status()
    cleared_status = ws_manager.get_status()
    assert cleared_status["progress"] == 0
    assert not cleared_status["error"]
