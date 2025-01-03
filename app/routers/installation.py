from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket
from typing import Optional
import asyncio
import logging
import os
import subprocess

from app.core.config import settings
from app.schemas.installation import InstallationRequest, InstallationStatus
from app.websocket.events import EventTypes, LogLevel
from app.core.logging import LoggerMixin

router = APIRouter()
logger = logging.getLogger(__name__)

class InstallationManager(LoggerMixin):
    def __init__(self):
        self.installation_tasks = {}
        self.firmware_dir = settings.FIRMWARE_DIR

    async def start_installation(
        self,
        request: InstallationRequest,
        websocket_manager,
        background_tasks: BackgroundTasks
    ):
        """Start Klipper installation process."""
        try:
            installation_id = f"install_{request.board_port}_{request.board_type}"
            
            if installation_id in self.installation_tasks:
                raise HTTPException(
                    status_code=400,
                    detail="Installation already in progress for this board"
                )
            
            # Create installation task
            task = asyncio.create_task(
                self._run_installation(installation_id, request, websocket_manager)
            )
            self.installation_tasks[installation_id] = task
            
            # Add cleanup to background tasks
            background_tasks.add_task(
                self._cleanup_installation,
                installation_id,
                task
            )
            
            return {"installation_id": installation_id}
            
        except Exception as e:
            self.logger.error(f"Error starting installation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to start installation"
            )

    async def cancel_installation(self, installation_id: str):
        """Cancel ongoing installation."""
        if installation_id not in self.installation_tasks:
            raise HTTPException(
                status_code=404,
                detail="Installation not found"
            )
        
        try:
            task = self.installation_tasks[installation_id]
            task.cancel()
            await self._cleanup_installation(installation_id, task)
            return {"message": "Installation cancelled successfully"}
        except Exception as e:
            self.logger.error(f"Error cancelling installation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to cancel installation"
            )

    async def _run_installation(
        self,
        installation_id: str,
        request: InstallationRequest,
        websocket_manager
    ):
        """Run the installation process."""
        try:
            # Step 1: Clone/Update Klipper repository
            await self._send_status(
                websocket_manager,
                "downloading",
                "Downloading Klipper firmware"
            )
            
            if not os.path.exists(os.path.join(self.firmware_dir, "klipper")):
                await self._run_command(
                    ["git", "clone", settings.KLIPPER_REPO],
                    cwd=self.firmware_dir,
                    websocket_manager=websocket_manager
                )
            else:
                await self._run_command(
                    ["git", "pull"],
                    cwd=os.path.join(self.firmware_dir, "klipper"),
                    websocket_manager=websocket_manager
                )

            # Step 2: Configure and build firmware
            await self._send_status(
                websocket_manager,
                "building",
                "Building firmware"
            )
            
            # Generate Klipper config
            config_path = os.path.join(self.firmware_dir, "klipper", ".config")
            self._generate_klipper_config(request.board_type, config_path)
            
            # Build firmware
            await self._run_command(
                ["make"],
                cwd=os.path.join(self.firmware_dir, "klipper"),
                websocket_manager=websocket_manager
            )

            # Step 3: Flash firmware
            await self._send_status(
                websocket_manager,
                "flashing",
                "Flashing firmware"
            )
            
            flash_command = self._get_flash_command(request.board_type, request.board_port)
            await self._run_command(
                flash_command,
                cwd=os.path.join(self.firmware_dir, "klipper"),
                websocket_manager=websocket_manager
            )

            # Step 4: Complete
            await self._send_status(
                websocket_manager,
                "completed",
                "Installation completed successfully"
            )

        except asyncio.CancelledError:
            await self._send_status(
                websocket_manager,
                "cancelled",
                "Installation cancelled"
            )
            raise
        except Exception as e:
            self.logger.error(f"Installation failed: {str(e)}")
            await self._send_status(
                websocket_manager,
                "failed",
                f"Installation failed: {str(e)}"
            )
            raise

    async def _run_command(
        self,
        command: list,
        cwd: str,
        websocket_manager,
        timeout: Optional[int] = None
    ):
        """Run a shell command and stream output."""
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        async def read_stream(stream, level: LogLevel):
            while True:
                line = await stream.readline()
                if not line:
                    break
                await self._send_log(
                    websocket_manager,
                    line.decode().strip(),
                    level
                )

        await asyncio.gather(
            read_stream(process.stdout, LogLevel.INFO),
            read_stream(process.stderr, LogLevel.ERROR)
        )

        if timeout:
            try:
                await asyncio.wait_for(process.wait(), timeout)
            except asyncio.TimeoutError:
                process.kill()
                raise Exception(f"Command timed out after {timeout} seconds")
        else:
            await process.wait()

        if process.returncode != 0:
            raise Exception(f"Command failed with exit code {process.returncode}")

    def _generate_klipper_config(self, board_type: str, config_path: str):
        """Generate Klipper firmware configuration."""
        # Implementation depends on board type
        # This is a simplified example
        config = {
            "CONFIG_LOW_LEVEL_OPTIONS": "y",
            "CONFIG_MACH_AVR": "y" if "arduino" in board_type.lower() else "n",
            "CONFIG_MACH_STM32": "y" if "stm" in board_type.lower() else "n",
            "CONFIG_BOARD_DIRECTORY": board_type,
        }
        
        with open(config_path, 'w') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")

    def _get_flash_command(self, board_type: str, board_port: str) -> list:
        """Get the appropriate flash command for the board type."""
        if "arduino" in board_type.lower():
            return ["make", "flash", f"FLASH_DEVICE={board_port}"]
        elif "stm" in board_type.lower():
            return ["make", "flash", f"FLASH_DEVICE={board_port}"]
        else:
            raise Exception(f"Unsupported board type: {board_type}")

    async def _send_status(
        self,
        websocket_manager,
        status: str,
        message: str
    ):
        """Send installation status update."""
        await websocket_manager.broadcast_json({
            "type": EventTypes.INSTALLATION_STATUS,
            "data": {
                "status": status,
                "message": message
            }
        })

    async def _send_log(
        self,
        websocket_manager,
        message: str,
        level: LogLevel
    ):
        """Send log message."""
        await websocket_manager.broadcast_json({
            "type": EventTypes.INSTALLATION_LOG,
            "data": {
                "message": message,
                "level": level,
                "timestamp": datetime.now().isoformat()
            }
        })

    async def _cleanup_installation(self, installation_id: str, task: asyncio.Task):
        """Clean up installation task."""
        try:
            await task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Installation task failed: {str(e)}")
        finally:
            self.installation_tasks.pop(installation_id, None)

installation_manager = InstallationManager()

@router.post("/start")
async def start_installation(
    request: InstallationRequest,
    background_tasks: BackgroundTasks,
    websocket_manager=Depends(get_websocket_manager)
):
    """
    Start Klipper installation process.
    """
    return await installation_manager.start_installation(
        request,
        websocket_manager,
        background_tasks
    )

@router.post("/cancel/{installation_id}")
async def cancel_installation(installation_id: str):
    """
    Cancel ongoing installation.
    """
    return await installation_manager.cancel_installation(installation_id)
