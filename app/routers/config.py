from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging
import os
import yaml

from app.core.config import settings
from app.schemas.config import PrinterConfig, ConfigValidation
from app.core.logging import LoggerMixin

router = APIRouter()
logger = logging.getLogger(__name__)

class ConfigManager(LoggerMixin):
    def __init__(self):
        self.config_dir = settings.CONFIG_DIR

    def save_config(self, config: PrinterConfig) -> str:
        """Save printer configuration to a file."""
        try:
            config_path = os.path.join(self.config_dir, f"{config.printer_name}.cfg")
            
            # Convert config to Klipper format
            klipper_config = self._convert_to_klipper_config(config)
            
            with open(config_path, 'w') as f:
                yaml.safe_dump(klipper_config, f, default_flow_style=False)
            
            self.logger.info(f"Saved configuration for {config.printer_name}")
            return config_path
        except Exception as e:
            self.logger.error(f"Error saving config: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save printer configuration"
            )

    def load_config(self, printer_name: str) -> PrinterConfig:
        """Load printer configuration from file."""
        try:
            config_path = os.path.join(self.config_dir, f"{printer_name}.cfg")
            
            if not os.path.exists(config_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Configuration not found for {printer_name}"
                )
            
            with open(config_path, 'r') as f:
                klipper_config = yaml.safe_load(f)
            
            # Convert Klipper format to our schema
            config = self._convert_from_klipper_config(klipper_config)
            return config
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to load printer configuration"
            )

    def validate_config(self, config: PrinterConfig) -> ConfigValidation:
        """Validate printer configuration."""
        try:
            # Perform basic validation
            issues = []
            
            # Check printer dimensions
            if config.bed_size.x <= 0 or config.bed_size.y <= 0 or config.bed_size.z <= 0:
                issues.append("Invalid printer dimensions")
            
            # Check velocities
            if config.max_velocity <= 0:
                issues.append("Invalid maximum velocity")
            if config.max_z_velocity <= 0:
                issues.append("Invalid maximum Z velocity")
            
            # Check accelerations
            if config.max_accel <= 0:
                issues.append("Invalid maximum acceleration")
            if config.max_z_accel <= 0:
                issues.append("Invalid maximum Z acceleration")
            
            return ConfigValidation(
                valid=len(issues) == 0,
                issues=issues
            )
        except Exception as e:
            self.logger.error(f"Error validating config: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to validate printer configuration"
            )

    def _convert_to_klipper_config(self, config: PrinterConfig) -> Dict[str, Any]:
        """Convert our config schema to Klipper format."""
        return {
            "printer": {
                "kinematics": config.kinematics,
                "max_velocity": config.max_velocity,
                "max_accel": config.max_accel,
                "max_z_velocity": config.max_z_velocity,
                "max_z_accel": config.max_z_accel,
            },
            "stepper_x": {
                "position_max": config.bed_size.x,
            },
            "stepper_y": {
                "position_max": config.bed_size.y,
            },
            "stepper_z": {
                "position_max": config.bed_size.z,
            },
            "board": {
                "type": config.board_type,
                "mcu": config.mcu_path,
            },
            "features": {
                "pressure_advance": config.features.pressure_advance,
                "input_shaping": config.features.input_shaping,
            }
        }

    def _convert_from_klipper_config(self, klipper_config: Dict[str, Any]) -> PrinterConfig:
        """Convert Klipper format to our config schema."""
        from app.schemas.config import PrinterDimensions, PrinterFeatures
        
        return PrinterConfig(
            printer_name=klipper_config.get("printer", {}).get("name", "Unknown"),
            kinematics=klipper_config.get("printer", {}).get("kinematics", "cartesian"),
            bed_size=PrinterDimensions(
                x=klipper_config.get("stepper_x", {}).get("position_max", 0),
                y=klipper_config.get("stepper_y", {}).get("position_max", 0),
                z=klipper_config.get("stepper_z", {}).get("position_max", 0),
            ),
            max_velocity=klipper_config.get("printer", {}).get("max_velocity", settings.DEFAULT_MAX_VELOCITY),
            max_accel=klipper_config.get("printer", {}).get("max_accel", settings.DEFAULT_MAX_ACCEL),
            max_z_velocity=klipper_config.get("printer", {}).get("max_z_velocity", settings.DEFAULT_MAX_Z_VELOCITY),
            max_z_accel=klipper_config.get("printer", {}).get("max_z_accel", settings.DEFAULT_MAX_Z_ACCEL),
            board_type=klipper_config.get("board", {}).get("type", "unknown"),
            mcu_path=klipper_config.get("board", {}).get("mcu", "/dev/ttyUSB0"),
            features=PrinterFeatures(
                pressure_advance=klipper_config.get("features", {}).get("pressure_advance", False),
                input_shaping=klipper_config.get("features", {}).get("input_shaping", False),
            )
        )

config_manager = ConfigManager()

@router.post("/validate", response_model=ConfigValidation)
async def validate_config(config: PrinterConfig):
    """
    Validate printer configuration.
    """
    return config_manager.validate_config(config)

@router.post("/save")
async def save_config(config: PrinterConfig):
    """
    Save printer configuration.
    """
    config_path = config_manager.save_config(config)
    return {"message": "Configuration saved successfully", "path": config_path}

@router.get("/{printer_name}", response_model=PrinterConfig)
async def get_config(printer_name: str):
    """
    Get printer configuration.
    """
    return config_manager.load_config(printer_name)
