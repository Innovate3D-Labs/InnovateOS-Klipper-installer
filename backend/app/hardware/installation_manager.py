import asyncio
import logging
from typing import Optional, Dict, List, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from .board_manager import BoardManager, Board
from .firmware_manager import FirmwareManager

logger = logging.getLogger(__name__)

@dataclass
class InstallationStatus:
    id: str
    board: Board
    status: str
    progress: int
    message: str
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None

class InstallationManager:
    def __init__(
        self,
        board_manager: BoardManager,
        firmware_manager: FirmwareManager,
        work_dir: Path
    ):
        self.board_manager = board_manager
        self.firmware_manager = firmware_manager
        self.work_dir = work_dir
        self.active_installations: Dict[str, InstallationStatus] = {}
        self.status_callbacks: List[Callable] = []

    def register_status_callback(self, callback: Callable):
        """Register callback for status updates"""
        self.status_callbacks.append(callback)

    def _notify_status_update(self, status: InstallationStatus):
        """Notify all registered callbacks of status update"""
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")

    async def start_installation(
        self,
        board: Board,
        config: Dict,
        version: str
    ) -> Optional[str]:
        """Start installation process"""
        try:
            installation_id = f"install_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            status = InstallationStatus(
                id=installation_id,
                board=board,
                status="starting",
                progress=0,
                message="Starting installation",
                start_time=datetime.now()
            )
            
            self.active_installations[installation_id] = status
            self._notify_status_update(status)

            # Start installation process in background
            asyncio.create_task(
                self._run_installation(installation_id, board, config, version)
            )

            return installation_id
        except Exception as e:
            logger.error(f"Failed to start installation: {e}")
            return None

    async def _run_installation(
        self,
        installation_id: str,
        board: Board,
        config: Dict,
        version: str
    ):
        """Run installation process"""
        try:
            status = self.active_installations[installation_id]

            # Step 1: Download firmware
            self._update_status(status, "downloading", 10, "Downloading firmware")
            firmware_dir = await self.firmware_manager.download_firmware(version)
            if not firmware_dir:
                raise Exception("Failed to download firmware")

            # Step 2: Build firmware
            self._update_status(status, "building", 30, "Building firmware")
            firmware_path = await self.firmware_manager.build_firmware(
                version, board.board_type, config
            )
            if not firmware_path:
                raise Exception("Failed to build firmware")

            # Step 3: Verify firmware
            self._update_status(status, "verifying", 50, "Verifying firmware")
            if not await self.firmware_manager.verify_firmware(firmware_path):
                raise Exception("Firmware verification failed")

            # Step 4: Prepare board
            self._update_status(status, "preparing", 70, "Preparing board")
            if not await self.board_manager.prepare_for_update(board):
                raise Exception("Failed to prepare board")

            # Step 5: Flash firmware
            self._update_status(status, "flashing", 90, "Flashing firmware")
            if not await self.board_manager.flash_firmware(board, firmware_path):
                raise Exception("Failed to flash firmware")

            # Installation complete
            self._update_status(
                status, "completed", 100, "Installation completed successfully"
            )

        except Exception as e:
            logger.error(f"Installation failed: {e}")
            self._update_status(
                status, "failed", 0, "Installation failed", str(e)
            )

        finally:
            status.end_time = datetime.now()
            self._notify_status_update(status)

    def _update_status(
        self,
        status: InstallationStatus,
        new_status: str,
        progress: int,
        message: str,
        error: Optional[str] = None
    ):
        """Update installation status"""
        status.status = new_status
        status.progress = progress
        status.message = message
        status.error = error
        self._notify_status_update(status)

    def get_status(self, installation_id: str) -> Optional[InstallationStatus]:
        """Get status of specific installation"""
        return self.active_installations.get(installation_id)

    def get_all_statuses(self) -> List[InstallationStatus]:
        """Get status of all installations"""
        return list(self.active_installations.values())

    async def cancel_installation(self, installation_id: str) -> bool:
        """Cancel ongoing installation"""
        try:
            status = self.active_installations.get(installation_id)
            if not status or status.status in ["completed", "failed"]:
                return False

            self._update_status(
                status, "cancelled", 0, "Installation cancelled by user"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to cancel installation: {e}")
            return False

    def cleanup_old_installations(self, max_age_days: int = 7):
        """Cleanup old installation records"""
        try:
            current_time = datetime.now()
            to_remove = []

            for installation_id, status in self.active_installations.items():
                if status.end_time:
                    age = current_time - status.end_time
                    if age.days >= max_age_days:
                        to_remove.append(installation_id)

            for installation_id in to_remove:
                del self.active_installations[installation_id]

        except Exception as e:
            logger.error(f"Failed to cleanup installations: {e}")

    def cleanup(self):
        """Cleanup all resources"""
        self.active_installations.clear()
        self.status_callbacks.clear()
