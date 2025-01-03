from typing import List, Optional
from pydantic import BaseModel, Field

class PrinterDimensions(BaseModel):
    x: float = Field(..., gt=0, description="X-axis size in millimeters")
    y: float = Field(..., gt=0, description="Y-axis size in millimeters")
    z: float = Field(..., gt=0, description="Z-axis size in millimeters")

class PrinterFeatures(BaseModel):
    pressure_advance: bool = Field(
        default=False,
        description="Enable pressure advance"
    )
    input_shaping: bool = Field(
        default=False,
        description="Enable input shaping"
    )

class PrinterConfig(BaseModel):
    printer_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Name of the printer"
    )
    kinematics: str = Field(
        default="cartesian",
        description="Printer kinematics type"
    )
    bed_size: PrinterDimensions
    max_velocity: float = Field(
        ...,
        gt=0,
        description="Maximum velocity in mm/s"
    )
    max_accel: float = Field(
        ...,
        gt=0,
        description="Maximum acceleration in mm/s^2"
    )
    max_z_velocity: float = Field(
        ...,
        gt=0,
        description="Maximum Z velocity in mm/s"
    )
    max_z_accel: float = Field(
        ...,
        gt=0,
        description="Maximum Z acceleration in mm/s^2"
    )
    board_type: str = Field(
        ...,
        description="Type of control board"
    )
    mcu_path: str = Field(
        ...,
        description="Path to MCU device"
    )
    features: PrinterFeatures = Field(
        default_factory=PrinterFeatures,
        description="Enabled printer features"
    )

class ConfigValidation(BaseModel):
    valid: bool
    issues: List[str] = []
