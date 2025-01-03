import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from .mocks.hardware import MockHardwareManager, MOCK_BOARDS

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_client() -> Generator:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_hardware() -> MockHardwareManager:
    """Create a mock hardware manager with some test boards."""
    manager = MockHardwareManager()
    
    # Add some test boards
    for board in MOCK_BOARDS.values():
        manager.add_mock_board(board)
    
    return manager

@pytest.fixture
def mock_serial():
    """Mock serial port communications."""
    with patch('serial.Serial') as mock:
        yield mock

@pytest.fixture
def mock_gpio():
    """Mock GPIO operations for board control."""
    with patch('RPi.GPIO') as mock:
        yield mock

@pytest.fixture
def mock_firmware_builder():
    """Mock the Klipper firmware builder."""
    with patch('app.services.firmware.KlipperFirmwareBuilder') as mock:
        instance = mock.return_value
        instance.build.return_value = True
        instance.get_build_path.return_value = "/tmp/klipper.bin"
        yield instance

@pytest.fixture
def mock_config_validator():
    """Mock the configuration validator."""
    with patch('app.services.config.ConfigValidator') as mock:
        instance = mock.return_value
        instance.validate.return_value = (True, [])
        yield instance

@pytest.fixture
def mock_installation_service():
    """Mock the installation service."""
    with patch('app.services.installation.InstallationService') as mock:
        instance = mock.return_value
        instance.start.return_value = "test_installation_id"
        instance.get_status.return_value = {
            "status": "completed",
            "progress": 100,
            "message": "Installation complete"
        }
        yield instance

@pytest.fixture
def test_config():
    """Test printer configuration."""
    return {
        "printer_name": "Test Printer",
        "kinematics": "cartesian",
        "bed_size": {
            "x": 200,
            "y": 200,
            "z": 200
        },
        "max_velocity": 300,
        "max_accel": 3000,
        "max_z_velocity": 5,
        "max_z_accel": 100,
        "board_type": "SKR_V1.4",
        "mcu_path": "/dev/ttyUSB0",
        "features": {
            "pressure_advance": True,
            "input_shaping": True
        }
    }

@pytest.fixture
def test_board():
    """Test board configuration."""
    return MOCK_BOARDS["SKR_V1.4"]
