# API-Dokumentation

## 🔌 Endpunkte

### 1. Drucker-API

#### GET `/api/printers`
Liste aller verfügbaren Drucker.

**Response:**
```json
{
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
    }
  ]
}
```

#### GET `/api/printer-config/{printer_id}`
Board-Konfiguration für einen bestimmten Drucker.

**Parameter:**
- `printer_id`: ID des Druckers (string, required)

**Response:**
```json
{
  "board_config": {
    "board": "STM32F103",
    "processor": "stm32f103",
    "bootloader": 28672,
    "compiler_flags": [
      "CONFIG_MACH_STM32F103=y",
      "CONFIG_CLOCK_FREQ=72000000"
    ]
  }
}
```

### 2. Board-API

#### GET `/api/detect-board`
Automatische Board-Erkennung.

**Response:**
```json
{
  "board": "STM32F103",
  "interface": "serial",
  "port": "/dev/ttyUSB0",
  "manufacturer": "Creality",
  "vid": "1a86",
  "pid": "7523"
}
```

#### GET `/api/serial-ports`
Liste verfügbarer serieller Ports.

**Response:**
```json
{
  "ports": [
    {
      "device": "/dev/ttyUSB0",
      "description": "USB Serial",
      "hwid": "USB VID:PID=1A86:7523",
      "manufacturer": "Creality"
    }
  ]
}
```

### 3. Installation-API

#### POST `/api/install`
Startet die Installation.

**Request Body:**
```json
{
  "printer_id": "ender3",
  "webInterface_id": "fluidd",
  "board_config": {
    "board": "STM32F103",
    "serial": "/dev/ttyUSB0",
    "baud": 250000,
    "bootloader": 28672
  }
}
```

**Response:**
```json
{
  "status": "started",
  "install_id": "abc123"
}
```

#### GET `/api/status/{install_id}`
Aktueller Installationsstatus.

**Parameter:**
- `install_id`: ID der Installation (string, required)

**Response:**
```json
{
  "progress": 50,
  "step": "firmware",
  "message": "Kompiliere Firmware...",
  "error": null,
  "log": [
    "Abhängigkeiten installiert",
    "Klipper geklont",
    "Kompiliere Firmware..."
  ]
}
```

### 4. WebSocket-API

#### WebSocket `/ws`
Echtzeit-Updates während der Installation.

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws')
```

**Nachrichten-Format:**
```json
{
  "type": "status",
  "data": {
    "step": "firmware",
    "message": "Kompiliere Firmware...",
    "progress": 50,
    "error": null,
    "log": "Kompilierung gestartet..."
  }
}
```

## 🔒 Authentifizierung

Aktuell keine Authentifizierung erforderlich. Für Produktionsumgebungen wird Basic Auth oder Token-basierte Authentifizierung empfohlen.

## 📝 Fehler-Responses

### 400 Bad Request
```json
{
  "detail": "Ungültige Anfrage-Parameter",
  "errors": [
    {
      "field": "printer_id",
      "message": "Unbekannter Drucker"
    }
  ]
}
```

### 404 Not Found
```json
{
  "detail": "Drucker nicht gefunden",
  "printer_id": "unknown_printer"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Interner Server-Fehler",
  "error": "Kompilierung fehlgeschlagen"
}
```

## 🚀 Beispiele

### cURL

```bash
# Drucker abrufen
curl https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/api/printers

# Board erkennen
curl https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/api/detect-board

# Installation starten
curl -X POST https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/api/install \
  -H "Content-Type: application/json" \
  -d '{
    "printer_id": "ender3",
    "webInterface_id": "fluidd"
  }'
```

### Python

```python
import requests
import websockets
import json
import asyncio

async def install_klipper():
    # Drucker abrufen
    printers = requests.get(
        "https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/api/printers"
    ).json()

    # Installation starten
    response = requests.post(
        "https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/api/install",
        json={
            "printer_id": "ender3",
            "webInterface_id": "fluidd"
        }
    ).json()

    # WebSocket-Updates
    async with websockets.connect(
        "wss://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/ws"
    ) as ws:
        while True:
            message = await ws.recv()
            print(json.loads(message))

# Ausführen
asyncio.run(install_klipper())
```

### JavaScript

```javascript
// Drucker abrufen
fetch('https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/api/printers')
  .then(response => response.json())
  .then(data => console.log(data));

// Installation starten
fetch('https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/api/install', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    printer_id: 'ender3',
    webInterface_id: 'fluidd'
  }),
})
  .then(response => response.json())
  .then(data => console.log(data));

// WebSocket-Updates
const ws = new WebSocket('wss://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/ws');
ws.onmessage = (event) => {
  console.log(JSON.parse(event.data));
};
```

## 📈 Rate Limiting

- 100 Anfragen pro Minute pro IP
- WebSocket-Verbindungen: maximal 10 pro IP
- Installation: maximal 2 gleichzeitige Installationen pro IP

## 🔐 Sicherheit

### CORS
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://innovate3d-labs.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SSL/TLS
Alle Produktions-Endpoints müssen über HTTPS/WSS erreichbar sein.

## 📚 Versionierung

Die API verwendet Semantic Versioning (MAJOR.MINOR.PATCH).
Aktuelle Version: v1.0.0

### Breaking Changes
- v2.0.0: Neue Authentifizierung (geplant)
- v3.0.0: GraphQL-Support (geplant)
