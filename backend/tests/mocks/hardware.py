from typing import List, Optional, Dict
from unittest.mock import MagicMock
import random
import time
from dataclasses import dataclass

@dataclass
class MockSerialPort:
    device: str
    vid: int
    pid: int
    serial_number: str
    description: str
    manufacturer: Optional[str] = None
    product: Optional[str] = None
    location: Optional[str] = None

class MockHardwareManager:
    """Mock hardware manager for testing without real hardware access"""
    
    def __init__(self):
        self.connected_boards: Dict[str, MockSerialPort] = {}
        self.firmware_versions: Dict[str, str] = {}
        self.board_states: Dict[str, str] = {}
        
    def add_mock_board(self, board: MockSerialPort) -> None:
        """Add a mock board to the connected devices"""
        self.connected_boards[board.device] = board
        self.board_states[board.device] = "ready"
        self.firmware_versions[board.device] = "v0.0.0"
    
    def remove_mock_board(self, port: str) -> None:
        """Remove a mock board from connected devices"""
        self.connected_boards.pop(port, None)
        self.board_states.pop(port, None)
        self.firmware_versions.pop(port, None)
    
    def get_connected_boards(self) -> List[MockSerialPort]:
        """Get list of currently connected boards"""
        return list(self.connected_boards.values())
    
    def is_board_connected(self, port: str) -> bool:
        """Check if a board is connected on the specified port"""
        return port in self.connected_boards
    
    def get_board_state(self, port: str) -> str:
        """Get the current state of a board"""
        return self.board_states.get(port, "disconnected")
    
    def get_firmware_version(self, port: str) -> Optional[str]:
        """Get the firmware version of a board"""
        return self.firmware_versions.get(port)
    
    async def update_firmware(
        self,
        port: str,
        firmware_path: str,
        progress_callback: Optional[callable] = None
    ) -> bool:
        """Simulate firmware update process"""
        if not self.is_board_connected(port):
            raise Exception(f"No board found on port {port}")
        
        self.board_states[port] = "updating"
        
        # Simulate update process
        total_steps = 10
        for i in range(total_steps):
            if progress_callback:
                progress_callback(i * 10)
            await asyncio.sleep(0.5)
            
            # Simulate random errors
            if random.random() < 0.1:
                self.board_states[port] = "error"
                raise Exception("Firmware update failed")
        
        self.firmware_versions[port] = "v1.0.0"
        self.board_states[port] = "ready"
        
        if progress_callback:
            progress_callback(100)
            
        return True
    
    def test_connection(self, port: str) -> bool:
        """Test connection to a board"""
        return self.is_board_connected(port)
    
    def reset_board(self, port: str) -> bool:
        """Reset a board to default state"""
        if not self.is_board_connected(port):
            return False
            
        self.board_states[port] = "resetting"
        time.sleep(1)  # Simulate reset time
        self.board_states[port] = "ready"
        return True

class MockSerialConnection:
    """Mock serial connection for testing"""
    
    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.is_open = False
        self.rx_buffer = []
        self.tx_buffer = []
    
    def open(self) -> None:
        """Open the serial connection"""
        if not self.is_open:
            self.is_open = True
    
    def close(self) -> None:
        """Close the serial connection"""
        if self.is_open:
            self.is_open = False
    
    def write(self, data: bytes) -> int:
        """Write data to the serial connection"""
        if not self.is_open:
            raise Exception("Port not open")
        self.tx_buffer.append(data)
        return len(data)
    
    def read(self, size: int = 1) -> bytes:
        """Read data from the serial connection"""
        if not self.is_open:
            raise Exception("Port not open")
        if not self.rx_buffer:
            return b""
        return self.rx_buffer.pop(0)[:size]
    
    def flush(self) -> None:
        """Flush the serial buffers"""
        self.rx_buffer = []
        self.tx_buffer = []
    
    def add_response(self, data: bytes) -> None:
        """Add data to the receive buffer for testing"""
        self.rx_buffer.append(data)

# Common mock boards for testing
MOCK_BOARDS = {
    "SKR_V1.4": MockSerialPort(
        device="/dev/ttyUSB0",
        vid=0x1D50,  # BTT VID
        pid=0x6029,
        serial_number="123456",
        description="BTT SKR V1.4",
        manufacturer="BigTreeTech"
    ),
    "MEGA_2560": MockSerialPort(
        device="/dev/ttyACM0",
        vid=0x2341,  # Arduino VID
        pid=0x0042,
        serial_number="789012",
        description="Arduino Mega 2560",
        manufacturer="Arduino"
    ),
    "OCTOPUS": MockSerialPort(
        device="/dev/ttyUSB1",
        vid=0x1D50,
        pid=0x614E,
        serial_number="345678",
        description="BTT Octopus",
        manufacturer="BigTreeTech"
    )
}
