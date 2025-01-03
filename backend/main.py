from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Optional
import asyncio
import json
from pathlib import Path
import logging
from .installer import KlipperInstaller
from .websocket_manager import WebSocketManager
from .firmware_config import PRINTER_CONFIGS
import serial.tools.list_ports

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="InnovateOS Klipper Installer")
ws_manager = WebSocketManager()

# CORS-Konfiguration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statische Dateien
app.mount("/static", StaticFiles(directory="../frontend/dist"), name="static")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket-Endpunkt für Live-Updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Hier können wir später Client-Nachrichten verarbeiten
    except Exception as e:
        logger.error(f"WebSocket-Fehler: {str(e)}")
    finally:
        ws_manager.disconnect(websocket)

@app.get("/api/printers")
async def get_printers():
    """Liste aller verfügbaren Drucker"""
    return {
        "printers": [
            {
                "id": "ender3",
                "name": "Ender 3",
                "manufacturer": "Creality",
                "board_configs": ["STM32F103"]
            },
            {
                "id": "voron2.4",
                "name": "Voron 2.4",
                "manufacturer": "Voron Design",
                "board_configs": ["STM32F446"]
            },
            {
                "id": "ratrig_vcore3",
                "name": "RatRig V-Core 3",
                "manufacturer": "RatRig",
                "board_configs": ["STM32F407"]
            }
        ]
    }

@app.get("/api/printer-config/{printer_id}")
async def get_printer_config(printer_id: str):
    """Board-Konfiguration für einen bestimmten Drucker"""
    if printer_id not in PRINTER_CONFIGS:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")
    
    return {"board_config": PRINTER_CONFIGS[printer_id]}

@app.get("/api/interfaces")
async def get_interfaces():
    """Liste der verfügbaren Weboberflächen"""
    return {
        "webInterfaces": [
            {
                "id": "fluidd",
                "name": "Fluidd",
                "description": "Moderne und intuitive Weboberfläche"
            },
            {
                "id": "mainsail",
                "name": "Mainsail",
                "description": "Leistungsstarke Weboberfläche mit vielen Funktionen"
            }
        ]
    }

@app.get("/api/serial-ports")
async def get_serial_ports():
    """Liste aller verfügbaren seriellen Ports"""
    ports = []
    try:
        for port in serial.tools.list_ports.comports():
            ports.append({
                "device": port.device,
                "description": port.description,
                "hwid": port.hwid
            })
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der seriellen Ports: {str(e)}")
    
    return {"ports": ports}

@app.get("/api/detect-board")
async def detect_board():
    """Automatische Board-Erkennung"""
    try:
        installer = KlipperInstaller(ws_manager.send_installation_update)
        board = await installer.detect_printer_board()
        return {"board": board}
    except Exception as e:
        logger.error(f"Fehler bei der Board-Erkennung: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/install")
async def start_installation(config: Dict):
    """Installation starten"""
    try:
        # Status zurücksetzen
        await ws_manager.clear_status()
        
        # Installer mit WebSocket-Callback erstellen
        installer = KlipperInstaller(ws_manager.send_installation_update)
        
        # Installation im Hintergrund starten
        asyncio.create_task(installer.install_klipper(
            printer_model=config["printer_id"],
            config_path=f"config/{config['printer_id']}/printer.cfg"
        ))
        
        return {"status": "started"}
    except Exception as e:
        logger.error(f"Fehler beim Starten der Installation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Aktuellen Installationsstatus abrufen"""
    return ws_manager.get_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
