import serial
import serial.tools.list_ports
from typing import List, Optional, Dict
import logging
import json
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class Board:
    port: str
    vid: int
    pid: int
    serial_number: str
    manufacturer: str
    description: str
    board_type: Optional[str] = None

class BoardManager:
    # Known board identifiers (VID:PID)
    KNOWN_BOARDS = {
        "0483:5740": "BTT SKR",
        "1D50:6029": "BTT Octopus",
        "2341:0042": "Arduino Mega",
        "2341:003D": "Arduino Due",
        "1D50:6015": "Einsy Rambo",
        "1D50:6028": "BTT Spider"
    }

    def __init__(self):
        self.detected_boards: Dict[str, Board] = {}
        self._load_board_configs()

    def _load_board_configs(self):
        """Load board configurations from JSON file"""
        config_path = Path(__file__).parent / "board_configs.json"
        try:
            with open(config_path) as f:
                self.board_configs = json.load(f)
        except FileNotFoundError:
            logger.warning("Board configs not found, using defaults")
            self.board_configs = {}

    def detect_boards(self) -> List[Board]:
        """Detect all connected printer boards"""
        self.detected_boards.clear()
        
        for port in serial.tools.list_ports.comports():
            try:
                board_id = f"{port.vid:04x}:{port.pid:04x}".upper()
                
                if board_id in self.KNOWN_BOARDS:
                    board = Board(
                        port=port.device,
                        vid=port.vid,
                        pid=port.pid,
                        serial_number=port.serial_number or "",
                        manufacturer=port.manufacturer or "",
                        description=port.description or "",
                        board_type=self.KNOWN_BOARDS[board_id]
                    )
                    self.detected_boards[port.device] = board
                    logger.info(f"Detected board: {board}")
            
            except Exception as e:
                logger.error(f"Error detecting board on port {port}: {e}")

        return list(self.detected_boards.values())

    async def test_connection(self, port: str) -> bool:
        """Test if we can establish a connection to the board"""
        try:
            with serial.Serial(port, baudrate=115200, timeout=1) as ser:
                ser.write(b'\r\n')  # Send newline
                response = ser.readline()
                return bool(response)
        except Exception as e:
            logger.error(f"Connection test failed for port {port}: {e}")
            return False

    def get_board_config(self, board_type: str) -> dict:
        """Get configuration for specific board type"""
        return self.board_configs.get(board_type, {})

    async def prepare_for_update(self, board: Board) -> bool:
        """Prepare board for firmware update"""
        try:
            config = self.get_board_config(board.board_type)
            if not config:
                raise ValueError(f"No configuration found for board type {board.board_type}")

            # Set bootloader mode if required
            if config.get("requires_bootloader"):
                await self._enter_bootloader_mode(board)

            return True
        except Exception as e:
            logger.error(f"Failed to prepare board for update: {e}")
            return False

    async def _enter_bootloader_mode(self, board: Board):
        """Put board into bootloader mode"""
        try:
            with serial.Serial(board.port, baudrate=115200, timeout=1) as ser:
                # Send bootloader command (board specific)
                if "BTT" in board.board_type:
                    ser.write(b'M997\n')  # BTT boards bootloader command
                elif "Arduino" in board.board_type:
                    ser.setDTR(False)  # Toggle DTR for Arduino
                    await asyncio.sleep(0.1)
                    ser.setDTR(True)
        except Exception as e:
            logger.error(f"Failed to enter bootloader mode: {e}")
            raise

    async def flash_firmware(self, board: Board, firmware_path: Path) -> bool:
        """Flash firmware to board"""
        try:
            config = self.get_board_config(board.board_type)
            if not config:
                raise ValueError(f"No configuration found for board type {board.board_type}")

            # Prepare board for flashing
            if not await self.prepare_for_update(board):
                return False

            # Flash firmware using appropriate method
            if "BTT" in board.board_type:
                success = await self._flash_btt(board, firmware_path)
            elif "Arduino" in board.board_type:
                success = await self._flash_arduino(board, firmware_path)
            else:
                success = await self._flash_generic(board, firmware_path)

            return success
        except Exception as e:
            logger.error(f"Firmware flash failed: {e}")
            return False

    async def _flash_btt(self, board: Board, firmware_path: Path) -> bool:
        """Flash firmware to BTT boards"""
        try:
            # BTT specific flashing logic
            # Typically uses DFU mode
            return True
        except Exception as e:
            logger.error(f"BTT flash failed: {e}")
            return False

    async def _flash_arduino(self, board: Board, firmware_path: Path) -> bool:
        """Flash firmware to Arduino boards"""
        try:
            # Arduino specific flashing logic
            # Uses avrdude for Mega, bossac for Due
            return True
        except Exception as e:
            logger.error(f"Arduino flash failed: {e}")
            return False

    async def _flash_generic(self, board: Board, firmware_path: Path) -> bool:
        """Generic firmware flashing method"""
        try:
            # Generic flashing logic
            return True
        except Exception as e:
            logger.error(f"Generic flash failed: {e}")
            return False

    def cleanup(self):
        """Cleanup resources"""
        self.detected_boards.clear()
