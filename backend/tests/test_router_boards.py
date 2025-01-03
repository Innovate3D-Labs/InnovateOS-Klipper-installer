import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from typing import List

from app.main import app
from app.routers import boards
from app.models.board import Board, BoardType

client = TestClient(app)

@pytest.fixture
def mock_serial_ports():
    with patch('serial.tools.list_ports.comports') as mock:
        # Mock USB devices that could be 3D printer boards
        mock_ports = [
            MagicMock(
                device='/dev/ttyUSB0',
                vid=0x1D50,  # BTT VID
                pid=0x6029,
                serial_number='123456',
                description='BTT SKR V1.4'
            ),
            MagicMock(
                device='/dev/ttyACM0',
                vid=0x2341,  # Arduino VID
                pid=0x0042,
                serial_number='789012',
                description='Arduino Mega 2560'
            )
        ]
        mock.return_value = mock_ports
        yield mock

def test_detect_boards(mock_serial_ports):
    response = client.get("/api/boards/detect")
    assert response.status_code == 200
    
    boards = response.json()
    assert len(boards) == 2
    
    # Verify BTT SKR board
    skr_board = next(b for b in boards if 'SKR' in b['description'])
    assert skr_board['port'] == '/dev/ttyUSB0'
    assert skr_board['types'] == [BoardType.SKR.value]
    
    # Verify Arduino Mega board
    mega_board = next(b for b in boards if 'Mega' in b['description'])
    assert mega_board['port'] == '/dev/ttyACM0'
    assert mega_board['types'] == [BoardType.MEGA.value]

def test_detect_boards_no_devices(mock_serial_ports):
    mock_serial_ports.return_value = []
    response = client.get("/api/boards/detect")
    assert response.status_code == 200
    assert response.json() == []

def test_detect_boards_error(mock_serial_ports):
    mock_serial_ports.side_effect = Exception("Serial port error")
    response = client.get("/api/boards/detect")
    assert response.status_code == 500
    assert "error" in response.json()

def test_get_board_types():
    response = client.get("/api/boards/types")
    assert response.status_code == 200
    
    types = response.json()
    assert all(t in [bt.value for bt in BoardType] for t in types)
    assert BoardType.MEGA.value in types
    assert BoardType.SKR.value in types

@pytest.mark.parametrize("board_type,expected_status", [
    (BoardType.MEGA.value, 200),
    (BoardType.SKR.value, 200),
    ("invalid_board", 400)
])
def test_validate_board_type(board_type: str, expected_status: int):
    response = client.post(
        "/api/boards/validate",
        json={"board_type": board_type}
    )
    assert response.status_code == expected_status

@patch('app.routers.boards.test_board_connection')
def test_test_connection(mock_test_connection):
    test_board = {
        "port": "/dev/ttyUSB0",
        "board_type": BoardType.SKR.value
    }
    
    # Test successful connection
    mock_test_connection.return_value = True
    response = client.post(
        "/api/boards/test-connection",
        json=test_board
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Test failed connection
    mock_test_connection.return_value = False
    response = client.post(
        "/api/boards/test-connection",
        json=test_board
    )
    assert response.status_code == 200
    assert response.json()["success"] is False

    # Test invalid port
    response = client.post(
        "/api/boards/test-connection",
        json={"port": "invalid_port", "board_type": BoardType.SKR.value}
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_board_firmware_update():
    test_board = {
        "port": "/dev/ttyUSB0",
        "board_type": BoardType.SKR.value,
        "firmware_version": "v1.0.0"
    }
    
    with patch('app.routers.boards.update_board_firmware') as mock_update:
        mock_update.return_value = True
        response = await client.post(
            "/api/boards/firmware",
            json=test_board
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        mock_update.side_effect = Exception("Update failed")
        response = await client.post(
            "/api/boards/firmware",
            json=test_board
        )
        assert response.status_code == 500
        assert "error" in response.json()
