from typing import Optional
from pydantic import BaseModel, Field

class InstallationRequest(BaseModel):
    board_type: str = Field(
        ...,
        description="Type of control board"
    )
    board_port: str = Field(
        ...,
        description="Serial port of the board"
    )
    firmware_version: Optional[str] = Field(
        default="master",
        description="Klipper firmware version to install"
    )

class InstallationStatus(BaseModel):
    status: str
    message: str
    progress: Optional[float] = None
    error: Optional[str] = None
