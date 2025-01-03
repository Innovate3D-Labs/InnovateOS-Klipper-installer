from enum import Enum

class EventTypes(str, Enum):
    INSTALLATION_STATUS = "installation_status"
    INSTALLATION_LOG = "installation_log"
    BOARD_DETECTED = "board_detected"
    CONFIG_UPDATED = "config_updated"
    ERROR = "error"

class InstallationStatus(str, Enum):
    NOT_STARTED = "not_started"
    DOWNLOADING = "downloading"
    BUILDING = "building"
    FLASHING = "flashing"
    CONFIGURING = "configuring"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class LogLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"
