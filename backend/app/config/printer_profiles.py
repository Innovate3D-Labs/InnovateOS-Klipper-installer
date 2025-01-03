from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from pathlib import Path
import yaml
import json
import shutil
import logging

logger = logging.getLogger(__name__)

class PrinterDimensions(BaseModel):
    x: float = Field(..., gt=0)
    y: float = Field(..., gt=0)
    z: float = Field(..., gt=0)

class PrinterSpeeds(BaseModel):
    max_velocity: float = Field(..., gt=0)
    max_accel: float = Field(..., gt=0)
    max_z_velocity: float = Field(..., gt=0)
    max_z_accel: float = Field(..., gt=0)

class PrinterFeatures(BaseModel):
    pressure_advance: bool = False
    input_shaping: bool = False
    bed_mesh: bool = False
    bltouch: bool = False

class PrinterProfile(BaseModel):
    name: str
    manufacturer: str
    model: str
    board_type: str
    dimensions: PrinterDimensions
    speeds: PrinterSpeeds
    features: PrinterFeatures
    config_template: str
    description: Optional[str] = None

class ProfileManager:
    def __init__(self, profiles_dir: Path):
        self.profiles_dir = profiles_dir
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir = profiles_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._load_profiles()

    def _load_profiles(self):
        """Load all printer profiles"""
        self.profiles: Dict[str, PrinterProfile] = {}
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file) as f:
                    data = json.load(f)
                    profile = PrinterProfile(**data)
                    self.profiles[profile.name] = profile
            except Exception as e:
                logger.error(f"Failed to load profile {profile_file}: {e}")

    def get_profile(self, name: str) -> Optional[PrinterProfile]:
        """Get printer profile by name"""
        return self.profiles.get(name)

    def get_all_profiles(self) -> List[PrinterProfile]:
        """Get all printer profiles"""
        return list(self.profiles.values())

    def save_profile(self, profile: PrinterProfile):
        """Save printer profile"""
        try:
            file_path = self.profiles_dir / f"{profile.name}.json"
            with open(file_path, "w") as f:
                json.dump(profile.dict(), f, indent=2)
            self.profiles[profile.name] = profile
        except Exception as e:
            logger.error(f"Failed to save profile {profile.name}: {e}")
            raise

    def delete_profile(self, name: str) -> bool:
        """Delete printer profile"""
        try:
            file_path = self.profiles_dir / f"{name}.json"
            if file_path.exists():
                file_path.unlink()
                del self.profiles[name]
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete profile {name}: {e}")
            return False

    def backup_profile(self, name: str) -> Optional[Path]:
        """Backup printer profile"""
        try:
            profile = self.get_profile(name)
            if not profile:
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"{name}_{timestamp}.json"
            
            with open(backup_path, "w") as f:
                json.dump(profile.dict(), f, indent=2)
            
            return backup_path
        except Exception as e:
            logger.error(f"Failed to backup profile {name}: {e}")
            return None

    def restore_profile(self, backup_path: Path) -> Optional[PrinterProfile]:
        """Restore printer profile from backup"""
        try:
            with open(backup_path) as f:
                data = json.load(f)
                profile = PrinterProfile(**data)
                self.save_profile(profile)
                return profile
        except Exception as e:
            logger.error(f"Failed to restore profile from {backup_path}: {e}")
            return None

    def get_config_template(self, profile: PrinterProfile) -> str:
        """Get config template for printer profile"""
        try:
            template_path = self.profiles_dir / "templates" / profile.config_template
            with open(template_path) as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load config template for {profile.name}: {e}")
            raise

class ConfigGenerator:
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def generate_config(self, profile: PrinterProfile, custom_settings: Dict = None) -> str:
        """Generate printer configuration"""
        try:
            # Load base template
            template = self._load_template(profile.config_template)
            
            # Apply profile settings
            config = self._apply_profile_settings(template, profile)
            
            # Apply custom settings if provided
            if custom_settings:
                config = self._apply_custom_settings(config, custom_settings)
            
            return config
        except Exception as e:
            logger.error(f"Failed to generate config: {e}")
            raise

    def _load_template(self, template_name: str) -> str:
        """Load config template"""
        template_path = self.template_dir / template_name
        with open(template_path) as f:
            return f.read()

    def _apply_profile_settings(self, template: str, profile: PrinterProfile) -> str:
        """Apply profile settings to template"""
        replacements = {
            "{{printer_name}}": profile.name,
            "{{max_velocity}}": str(profile.speeds.max_velocity),
            "{{max_accel}}": str(profile.speeds.max_accel),
            "{{max_z_velocity}}": str(profile.speeds.max_z_velocity),
            "{{max_z_accel}}": str(profile.speeds.max_z_accel),
            "{{bed_size_x}}": str(profile.dimensions.x),
            "{{bed_size_y}}": str(profile.dimensions.y),
            "{{bed_size_z}}": str(profile.dimensions.z)
        }
        
        config = template
        for key, value in replacements.items():
            config = config.replace(key, value)
        
        return config

    def _apply_custom_settings(self, config: str, settings: Dict) -> str:
        """Apply custom settings to config"""
        for key, value in settings.items():
            config = config.replace(f"{{{{{key}}}}}", str(value))
        
        return config

    def validate_config(self, config: str) -> List[str]:
        """Validate printer configuration"""
        errors = []
        
        try:
            # Parse config
            parsed_config = self._parse_config(config)
            
            # Validate required sections
            required_sections = ["printer", "stepper_x", "stepper_y", "stepper_z"]
            for section in required_sections:
                if section not in parsed_config:
                    errors.append(f"Missing required section: {section}")
            
            # Validate values
            if "printer" in parsed_config:
                if "max_velocity" not in parsed_config["printer"]:
                    errors.append("Missing max_velocity in printer section")
                if "max_accel" not in parsed_config["printer"]:
                    errors.append("Missing max_accel in printer section")
            
        except Exception as e:
            errors.append(f"Config parsing error: {str(e)}")
        
        return errors

    def _parse_config(self, config: str) -> Dict:
        """Parse Klipper config string"""
        try:
            return yaml.safe_load(config)
        except Exception as e:
            logger.error(f"Failed to parse config: {e}")
            raise
