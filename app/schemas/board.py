from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class BoardType(str, Enum):
    MEGA = "arduino_mega"
    DUE = "arduino_due"
    SKR = "stm32_skr"
    RAMPS = "ramps"
    EINSY = "einsy"
    OCTOPUS = "octopus"
    SPIDER = "spider"

class Board(BaseModel):
    port: str
    name: str
    types: List[BoardType]
    vid: str
    pid: Optional[str] = None
    serial_number: Optional[str] = None
    description: Optional[str] = None
