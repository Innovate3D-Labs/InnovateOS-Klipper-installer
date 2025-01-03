# Benutzeranleitung

## 🚀 Erste Schritte

### 1. Installation

1. Installer herunterladen:
```bash
git clone https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer.git
cd InnovateOS-Klipper-installer
```

2. Installer starten:
```bash
./install.sh  # Linux
# oder
install.bat   # Windows
```

### 2. Weboberfläche öffnen

- Browser öffnen
- `http://localhost:8080` aufrufen

## 🖨️ Drucker einrichten

### 1. Drucker auswählen

1. Aus der Liste wählen:
   - Ender 3
   - Voron 2.4
   - RatRig V-Core 3
   - Andere...

2. Board konfigurieren:
   - Automatische Erkennung nutzen
   - Oder manuell konfigurieren:
     - Board-Typ
     - Serieller Port
     - Baudrate

### 2. Weboberfläche wählen

- **Fluidd**
  - Modern und intuitiv
  - Perfekt für Einsteiger
  - Einfache Konfiguration

- **Mainsail**
  - Erweiterte Funktionen
  - Umfangreiche Anpassungen
  - Für fortgeschrittene Benutzer

## 📝 Installation

### 1. Vorbereitung

- Drucker ausschalten
- USB-Kabel anschließen
- Board in Flash-Modus versetzen (falls nötig)

### 2. Installationsprozess

1. **Systemabhängigkeiten**
   - Automatische Installation
   - Fortschritt abwarten

2. **Klipper**
   - Repository wird geklont
   - Python-Umgebung wird eingerichtet

3. **Firmware**
   - Wird für Ihr Board kompiliert
   - Automatisch geflasht

4. **Konfiguration**
   - Drucker wird konfiguriert
   - Dienst wird eingerichtet

### 3. Abschluss

- Drucker neu starten
- Weboberfläche öffnen
- Verbindung testen

## ⚙️ Konfiguration

### 1. Grundeinstellungen

- **Drucker-Einstellungen**
  - Geschwindigkeiten
  - Beschleunigungen
  - Endstops

- **Extruder**
  - Schrittmotor
  - Heizer
  - Thermistor

- **Druckbett**
  - Größe
  - Heizung
  - Leveling

### 2. Erweiterte Einstellungen

- **Input Shaper**
  - Resonanzmessung
  - Filter-Einstellung

- **Pressure Advance**
  - Kalibrierung
  - Feinabstimmung

## 🔍 Fehlersuche

### 1. Installation

| Problem | Lösung |
|---------|--------|
| Board nicht erkannt | - USB-Kabel prüfen<br>- Treiber installieren |
| Kompilierung fehlgeschlagen | - Log prüfen<br>- Dependencies installieren |
| Flash fehlgeschlagen | - Board-Modus prüfen<br>- Neu starten |

### 2. Klipper

| Problem | Lösung |
|---------|--------|
| Verbindungsfehler | - Port prüfen<br>- Service neustarten |
| Drucker reagiert nicht | - USB prüfen<br>- Firmware-Flash |
| Konfigurationsfehler | - Config prüfen<br>- Syntax validieren |

## 🛠️ Wartung

### 1. Updates

```bash
# Klipper aktualisieren
cd ~/klipper
git pull

# Firmware neu flashen
make clean
make
make flash
```

### 2. Backups

```bash
# Konfiguration sichern
cp ~/printer_data/config/printer.cfg backup/

# Vollständiges Backup
tar -czf backup.tar.gz ~/printer_data/
```

## 📱 Mobile Nutzung

1. **Lokales Netzwerk**
   - IP-Adresse finden
   - Port 80 öffnen

2. **Remote-Zugriff**
   - VPN einrichten
   - oder
   - Reverse Proxy konfigurieren

## 🔒 Sicherheit

### 1. Grundlagen

- Starke Passwörter verwenden
- Regelmäßige Updates
- Firewall konfigurieren

### 2. Netzwerk

- Separates WLAN
- Port-Forwarding vermeiden
- VPN für Remote-Zugriff

## 📞 Support

### 1. Community

- [GitHub Issues](https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/issues)
- [Discord Server](https://discord.gg/Innovate3D-Labs)
- [Forum](https://forum.innovate3d-labs.com)

### 2. Dokumentation

- [FAQ](https://docs.innovate3d-labs.com/faq)
- [Troubleshooting Guide](https://docs.innovate3d-labs.com/troubleshooting)
- [Video-Tutorials](https://docs.innovate3d-labs.com/tutorials)
