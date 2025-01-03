from fastapi import APIRouter, HTTPException
from typing import List, Optional
import serial.tools.list_ports
import logging

from app.schemas.board import Board, BoardType
from app.core.logging import LoggerMixin

router = APIRouter()
logger = logging.getLogger(__name__)

class BoardDetector(LoggerMixin):
    def __init__(self):
        self.known_boards = {
            "2341": {"name": "Arduino", "types": [BoardType.MEGA, BoardType.DUE]},
            "1D50": {"name": "STM32", "types": [BoardType.SKR]},
            "0483": {"name": "STM32", "types": [BoardType.SKR]},
        }

    def detect_boards(self) -> List[Board]:
        detected_boards = []
        try:
            ports = list(serial.tools.list_ports.comports())
            for port in ports:
                board = self._identify_board(port)
                if board:
                    detected_boards.append(board)
        except Exception as e:
            self.logger.error(f"Error detecting boards: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to detect boards")

        return detected_boards

    def _identify_board(self, port) -> Optional[Board]:
        if not port.vid:
            return None

        vid = f"{port.vid:04X}"
        board_info = self.known_boards.get(vid)

        if not board_info:
            return None

        return Board(
            port=port.device,
            name=board_info["name"],
            types=board_info["types"],
            vid=vid,
            pid=f"{port.pid:04X}" if port.pid else None,
            serial_number=port.serial_number,
            description=port.description
        )

board_detector = BoardDetector()

@router.get("/detect", response_model=List[Board])
async def detect_boards():
    """
    Detect connected printer control boards.
    """
    try:
        boards = board_detector.detect_boards()
        logger.info(f"Detected {len(boards)} boards")
        return boards
    except Exception as e:
        logger.error(f"Error in detect_boards endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to detect boards"
        )

@router.get("/types", response_model=List[str])
async def get_board_types():
    """
    Get list of supported board types.
    """
    return [board_type.value for board_type in BoardType]
