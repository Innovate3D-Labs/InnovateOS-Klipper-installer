# InnovateOS Klipper Installer

Ein moderner, benutzerfreundlicher Installer für Klipper 3D-Drucker-Firmware mit Weboberfläche.

## 🌟 Features

- 🖨️ Automatische Board-Erkennung
- 🔧 Unterstützung für verschiedene Drucker-Boards (STM32, AVR)
- 🌐 Integration von Fluidd und Mainsail
- ⚡ Echtzeit-Installation mit Fortschrittsanzeige
- 📊 Detailliertes Logging und Fehlerbehandlung
- 🛠️ Automatische Firmware-Kompilierung

## 🚀 Unterstützte Drucker

- Creality Ender 3 (STM32F103)
- Voron 2.4 (STM32F446)
- RatRig V-Core 3 (STM32F407)

## 📋 Systemanforderungen

- Linux-basiertes Betriebssystem
- Python 3.7 oder höher
- Node.js 14 oder höher
- Git

## 🛠️ Installation

1. Repository klonen:
```bash
git clone https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer.git
cd InnovateOS-Klipper-installer
```

2. Backend-Abhängigkeiten installieren:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Frontend-Abhängigkeiten installieren:
```bash
cd frontend
npm install
```

## 🚀 Entwicklungsserver starten

1. Backend-Server:
```bash
cd backend
python -m uvicorn main:app --reload
```

2. Frontend-Server:
```bash
cd frontend
npm run serve
```

Die Anwendung ist dann unter `http://localhost:8080` verfügbar.

## 🏗️ Architektur

### Backend (FastAPI)

- `main.py`: FastAPI-Server und API-Endpunkte
- `installer.py`: Klipper-Installationslogik
- `board_detector.py`: Board-Erkennung
- `firmware_config.py`: Board-Konfigurationen
- `websocket_manager.py`: WebSocket-Verwaltung

### Frontend (Vue.js)

- `App.vue`: Hauptkomponente
- `components/`: UI-Komponenten
- `tests/`: Frontend-Tests

## 🔧 Konfiguration

### Board-Konfiguration

Neue Board-Konfigurationen können in `firmware_config.py` hinzugefügt werden:

```python
PRINTER_CONFIGS = {
    "printer_id": {
        "board": "BOARD_TYPE",
        "processor": "PROCESSOR_TYPE",
        "bootloader": BOOTLOADER_SIZE,
        "compiler_flags": [
            "CONFIG_FLAGS"
        ]
    }
}
```

### Weboberflächen

Unterstützte Weboberflächen:
- Fluidd: Moderne und intuitive Oberfläche
- Mainsail: Leistungsstarke Oberfläche mit erweiterten Funktionen

## 🧪 Tests

### Backend-Tests

```bash
cd backend
pytest
```

### Frontend-Tests

```bash
cd frontend
npm run test:unit
```

## 🔍 Fehlerbehandlung

### Bekannte Probleme

1. **Board nicht erkannt**
   - USB-Verbindung überprüfen
   - Board in DFU-Modus versetzen
   - Treiber installieren

2. **Kompilierung schlägt fehl**
   - Systemabhängigkeiten überprüfen
   - Board-Konfiguration prüfen
   - Log-Dateien analysieren

3. **Flash-Fehler**
   - Board-Modus überprüfen
   - USB-Verbindung überprüfen
   - Bootloader-Größe prüfen

## 🤝 Beitragen

1. Fork erstellen
2. Feature Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagung

- [Klipper](https://github.com/Klipper3d/klipper) für die großartige Firmware
- [Fluidd](https://github.com/fluidd-core/fluidd) und [Mainsail](https://github.com/mainsail-crew/mainsail) für die Weboberflächen
- Alle Mitwirkenden und Tester

## 📞 Support

Bei Fragen oder Problemen:
1. [Issues](https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/issues) auf GitHub erstellen
2. [Dokumentation](https://docs.innovate3d-labs.com) konsultieren
3. [Community-Forum](https://forum.innovate3d-labs.com) besuchen
