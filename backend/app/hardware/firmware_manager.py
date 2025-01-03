import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, List
import aiohttp
import git
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FirmwareVersion:
    version: str
    url: str
    release_notes: str
    date: str
    is_stable: bool

class FirmwareManager:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.firmware_dir = work_dir / "firmware"
        self.build_dir = work_dir / "build"
        self.cache_dir = work_dir / "cache"
        self._setup_directories()

    def _setup_directories(self):
        """Create necessary directories"""
        for directory in [self.firmware_dir, self.build_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    async def get_available_versions(self) -> List[FirmwareVersion]:
        """Get list of available Klipper versions"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.github.com/repos/Klipper3d/klipper/releases") as response:
                    if response.status == 200:
                        releases = await response.json()
                        return [
                            FirmwareVersion(
                                version=release["tag_name"],
                                url=release["html_url"],
                                release_notes=release["body"],
                                date=release["published_at"],
                                is_stable=not release["prerelease"]
                            )
                            for release in releases
                        ]
        except Exception as e:
            logger.error(f"Failed to fetch Klipper versions: {e}")
            return []

    async def download_firmware(self, version: str) -> Optional[Path]:
        """Download specific firmware version"""
        try:
            target_dir = self.firmware_dir / version
            if target_dir.exists():
                logger.info(f"Firmware version {version} already downloaded")
                return target_dir

            logger.info(f"Downloading Klipper version {version}")
            repo = git.Repo.clone_from(
                "https://github.com/Klipper3d/klipper.git",
                target_dir,
                branch=version
            )
            return target_dir
        except Exception as e:
            logger.error(f"Failed to download firmware: {e}")
            return None

    async def build_firmware(self, version: str, board_type: str, config: Dict) -> Optional[Path]:
        """Build firmware for specific board"""
        try:
            source_dir = self.firmware_dir / version
            if not source_dir.exists():
                source_dir = await self.download_firmware(version)
                if not source_dir:
                    return None

            build_dir = self.build_dir / f"{version}_{board_type}"
            build_dir.mkdir(parents=True, exist_ok=True)

            # Generate build config
            config_path = build_dir / "printer.cfg"
            self._generate_config(config_path, config)

            # Build firmware
            proc = await asyncio.create_subprocess_exec(
                "./scripts/build.sh",
                cwd=source_dir,
                env={
                    "KCONFIG_CONFIG": str(config_path),
                    "PYTHONPATH": str(source_dir)
                }
            )
            await proc.wait()

            if proc.returncode == 0:
                return build_dir / "out/klipper.bin"
            else:
                logger.error("Firmware build failed")
                return None
        except Exception as e:
            logger.error(f"Failed to build firmware: {e}")
            return None

    def _generate_config(self, config_path: Path, config: Dict):
        """Generate Klipper config file"""
        try:
            with open(config_path, "w") as f:
                for key, value in config.items():
                    f.write(f"CONFIG_{key}={value}\n")
        except Exception as e:
            logger.error(f"Failed to generate config: {e}")
            raise

    async def verify_firmware(self, firmware_path: Path) -> bool:
        """Verify firmware file integrity"""
        try:
            if not firmware_path.exists():
                return False

            # Check file size
            if firmware_path.stat().st_size < 1000:
                logger.error("Firmware file too small")
                return False

            # Additional verification could be added here
            # - Checksum verification
            # - Binary format validation
            # - etc.

            return True
        except Exception as e:
            logger.error(f"Firmware verification failed: {e}")
            return False

    def get_cached_firmware(self, version: str, board_type: str) -> Optional[Path]:
        """Get cached firmware if available"""
        cache_path = self.cache_dir / f"{version}_{board_type}.bin"
        return cache_path if cache_path.exists() else None

    def cache_firmware(self, firmware_path: Path, version: str, board_type: str):
        """Cache built firmware"""
        try:
            cache_path = self.cache_dir / f"{version}_{board_type}.bin"
            shutil.copy2(firmware_path, cache_path)
        except Exception as e:
            logger.error(f"Failed to cache firmware: {e}")

    def cleanup_old_versions(self, keep_versions: int = 3):
        """Cleanup old firmware versions"""
        try:
            # Keep only the most recent versions
            versions = sorted(
                [d for d in self.firmware_dir.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )

            for old_version in versions[keep_versions:]:
                shutil.rmtree(old_version)

            # Cleanup build directory
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
                self.build_dir.mkdir()

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    def cleanup(self):
        """Cleanup all resources"""
        try:
            shutil.rmtree(self.firmware_dir)
            shutil.rmtree(self.build_dir)
            shutil.rmtree(self.cache_dir)
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
