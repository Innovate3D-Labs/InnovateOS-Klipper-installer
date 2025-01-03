from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application settings
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # CORS settings
    ALLOW_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # File paths
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    CONFIG_DIR: str = os.path.join(DATA_DIR, "config")
    FIRMWARE_DIR: str = os.path.join(DATA_DIR, "firmware")
    LOG_DIR: str = os.path.join(DATA_DIR, "logs")
    
    # Klipper settings
    KLIPPER_REPO: str = "https://github.com/Klipper3d/klipper.git"
    KLIPPER_BRANCH: str = "master"
    
    # Default printer settings
    DEFAULT_MAX_VELOCITY: float = 300.0  # mm/s
    DEFAULT_MAX_ACCEL: float = 3000.0    # mm/s^2
    DEFAULT_MAX_Z_VELOCITY: float = 5.0   # mm/s
    DEFAULT_MAX_Z_ACCEL: float = 100.0    # mm/s^2
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create required directories
        for directory in [self.DATA_DIR, self.CONFIG_DIR, self.FIRMWARE_DIR, self.LOG_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)

settings = Settings()
