"""Klipper Installer Modul"""
import os
import asyncio
import logging
from typing import Dict, Optional, List
from pathlib import Path

from .board_detector import BoardDetector
from .websocket_manager import WebSocketManager
from .firmware_config import PRINTER_CONFIGS

class KlipperInstaller:
    """Klasse für die Installation und Konfiguration von Klipper"""

    def __init__(self, websocket_manager: WebSocketManager):
        self.ws_manager = websocket_manager
        self.board_detector = BoardDetector()
        self.current_step = ""
        self.install_path = Path.home() / "klipper"
        self.config_path = Path.home() / "printer_data" / "config"
        
        # Logger einrichten
        self.logger = logging.getLogger("klipper_installer")
        self.logger.setLevel(logging.DEBUG)

    async def send_status(self, message: str, progress: int, error: str = None):
        """Sendet Status-Updates über WebSocket"""
        await self.ws_manager.broadcast({
            "step": self.current_step,
            "message": message,
            "progress": progress,
            "error": error
        })

    async def run_command(self, command: List[str], cwd: str = None) -> bool:
        """Führt einen Shell-Befehl aus und gibt das Ergebnis zurück"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unbekannter Fehler"
                self.logger.error(f"Befehl fehlgeschlagen: {error_msg}")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Ausführen des Befehls: {str(e)}")
            return False

    async def compile_firmware(self, printer_model: str, board_config: Optional[Dict] = None) -> bool:
        """Kompiliert die Firmware für das spezifische Board"""
        self.current_step = "firmware"
        try:
            await self.send_status("Kompiliere Firmware...", 50)
            
            # Board-Konfiguration laden
            if not board_config:
                if printer_model not in PRINTER_CONFIGS:
                    raise ValueError(f"Keine Konfiguration für {printer_model} gefunden")
                board_config = PRINTER_CONFIGS[printer_model]

            # make clean
            if not await self.run_command(["make", "clean"], str(self.install_path)):
                raise RuntimeError("make clean fehlgeschlagen")

            # menuconfig generieren
            config_commands = [f"{flag}=y" for flag in board_config["compiler_flags"]]
            if not await self.run_command(["make", "menuconfig"] + config_commands, str(self.install_path)):
                raise RuntimeError("make menuconfig fehlgeschlagen")

            # Firmware kompilieren
            if not await self.run_command(["make"], str(self.install_path)):
                raise RuntimeError("make fehlgeschlagen")

            await self.send_status("Firmware erfolgreich kompiliert", 60)
            return True

        except Exception as e:
            error_msg = f"Fehler beim Kompilieren der Firmware: {str(e)}"
            self.logger.error(error_msg)
            await self.send_status("Kompilierung fehlgeschlagen", 50, error_msg)
            return False

    async def flash_firmware(self, printer_model: str, board_config: Optional[Dict] = None) -> bool:
        """Flasht die kompilierte Firmware auf das Board"""
        self.current_step = "flash"
        try:
            await self.send_status("Flashe Firmware...", 70)

            if not board_config:
                if printer_model not in PRINTER_CONFIGS:
                    raise ValueError(f"Keine Konfiguration für {printer_model} gefunden")
                board_config = PRINTER_CONFIGS[printer_model]

            # Board erkennen
            board_info = await self.board_detector.detect_board()
            if not board_info:
                raise RuntimeError("Kein Board gefunden")

            # Flash-Methode wählen
            if board_info["interface"] == "dfu":
                # DFU-Modus
                if not await self.run_command([
                    "dfu-util", "-d", f"{board_info['vid']}:{board_info['pid']}",
                    "-a", "0", "-s", "0x08000000:leave",
                    "-D", str(self.install_path / "out" / "klipper.bin")
                ]):
                    raise RuntimeError("dfu-util fehlgeschlagen")
            else:
                # Serieller Port
                if not await self.run_command([
                    "stm32flash", "-w",
                    str(self.install_path / "out" / "klipper.bin"),
                    "-v", "-S", "0x8008000",
                    board_info["port"]
                ]):
                    raise RuntimeError("stm32flash fehlgeschlagen")

            await self.send_status("Firmware erfolgreich geflasht", 80)
            return True

        except Exception as e:
            error_msg = f"Fehler beim Flashen der Firmware: {str(e)}"
            self.logger.error(error_msg)
            await self.send_status("Flash fehlgeschlagen", 70, error_msg)
            return False
