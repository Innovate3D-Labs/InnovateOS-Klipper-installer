import serial.tools.list_ports
import logging
import platform
import subprocess
import re
from typing import Optional, Dict, List, Tuple
import usb.core
import usb.util

logger = logging.getLogger(__name__)

class BoardDetector:
    def __init__(self):
        self.system = platform.system().lower()

    async def detect_board(self) -> Optional[Dict[str, str]]:
        """Erkennt das angeschlossene Drucker-Board"""
        try:
            # USB-Geräte scannen
            usb_devices = self._scan_usb_devices()
            if usb_devices:
                return usb_devices

            # Serielle Ports scannen
            serial_devices = self._scan_serial_ports()
            if serial_devices:
                return serial_devices

            return None
        except Exception as e:
            logger.error(f"Fehler bei der Board-Erkennung: {str(e)}")
            return None

    def _scan_usb_devices(self) -> Optional[Dict[str, str]]:
        """Scannt nach USB-Geräten"""
        try:
            # Nach allen USB-Geräten suchen
            devices = usb.core.find(find_all=True)
            
            for device in devices:
                try:
                    # Vendor und Product ID im Format XXXX:XXXX
                    vid = f"{device.idVendor:04x}"
                    pid = f"{device.idProduct:04x}"
                    usb_id = f"{vid}:{pid}"

                    # Bekannte Board-IDs
                    if usb_id == "1a86:7523":  # CH340 (Ender 3)
                        return {
                            "board": "STM32F103",
                            "interface": "serial",
                            "vid": vid,
                            "pid": pid,
                            "manufacturer": "Creality"
                        }
                    elif usb_id == "0483:5740":  # STM32 Virtual COM
                        return {
                            "board": "STM32F446",
                            "interface": "virtual_com",
                            "vid": vid,
                            "pid": pid,
                            "manufacturer": "STMicroelectronics"
                        }
                    elif usb_id == "0483:df11":  # STM32 DFU
                        return {
                            "board": "STM32F407",
                            "interface": "dfu",
                            "vid": vid,
                            "pid": pid,
                            "manufacturer": "STMicroelectronics"
                        }
                except Exception as e:
                    logger.warning(f"Fehler beim Lesen eines USB-Geräts: {str(e)}")
                    continue

            return None
        except Exception as e:
            logger.error(f"Fehler beim USB-Scan: {str(e)}")
            return None

    def _scan_serial_ports(self) -> Optional[Dict[str, str]]:
        """Scannt nach seriellen Ports"""
        try:
            for port in serial.tools.list_ports.comports():
                # Hardware-ID analysieren
                hwid = port.hwid.lower()
                
                # CH340-Erkennung (häufig bei Creality)
                if "ch340" in hwid or "1a86:7523" in hwid:
                    return {
                        "board": "STM32F103",
                        "port": port.device,
                        "description": port.description,
                        "manufacturer": "Creality",
                        "interface": "serial"
                    }
                
                # STM32 Virtual COM Port
                elif "0483:5740" in hwid:
                    return {
                        "board": "STM32F446",
                        "port": port.device,
                        "description": port.description,
                        "manufacturer": "STMicroelectronics",
                        "interface": "virtual_com"
                    }

            return None
        except Exception as e:
            logger.error(f"Fehler beim Scannen der seriellen Ports: {str(e)}")
            return None

    def _get_dfu_devices(self) -> List[Dict[str, str]]:
        """Erkennt DFU-Geräte (nur Linux)"""
        if self.system != "linux":
            return []

        try:
            result = subprocess.run(
                ["dfu-util", "--list"],
                capture_output=True,
                text=True
            )
            
            devices = []
            current_device = {}
            
            for line in result.stdout.split('\n'):
                if "Found DFU" in line:
                    if current_device:
                        devices.append(current_device)
                    current_device = {}
                    
                    # VID:PID extrahieren
                    match = re.search(r'([0-9a-fA-F]{4}):([0-9a-fA-F]{4})', line)
                    if match:
                        current_device["vid"] = match.group(1)
                        current_device["pid"] = match.group(2)
                
                elif "Product" in line:
                    match = re.search(r'Product.*: (.*)', line)
                    if match:
                        current_device["product"] = match.group(1)
            
            if current_device:
                devices.append(current_device)
                
            return devices
        except Exception as e:
            logger.error(f"Fehler bei der DFU-Geräteerkennung: {str(e)}")
            return []

    def get_port_info(self, port_device: str) -> Optional[Dict[str, str]]:
        """Detaillierte Informationen zu einem seriellen Port"""
        try:
            for port in serial.tools.list_ports.comports():
                if port.device == port_device:
                    return {
                        "device": port.device,
                        "name": port.name,
                        "description": port.description,
                        "hwid": port.hwid,
                        "vid": port.vid,
                        "pid": port.pid,
                        "serial_number": port.serial_number,
                        "manufacturer": port.manufacturer
                    }
            return None
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Port-Informationen: {str(e)}")
            return None
