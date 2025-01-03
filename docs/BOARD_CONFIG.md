# Board-Konfigurationsanleitung

## 🔧 Neue Boards hinzufügen

### 1. Board-Information sammeln

Benötigte Informationen:
- Board-Typ (z.B. STM32F103, STM32F446)
- Prozessor-Details
- Bootloader-Größe
- USB-IDs (VID:PID)

### 2. Konfigurationsdatei erstellen

Erstelle eine neue JSON-Datei unter `configs/boards/`:

```json
{
  "board_id": "skr_mini_e3_v2",
  "name": "SKR Mini E3 V2.0",
  "manufacturer": "BIGTREETECH",
  "website": "https://github.com/bigtreetech/BIGTREETECH-SKR-mini-E3",
  "chip": {
    "family": "STM32F103",
    "variant": "STM32F103RC",
    "clock": 72000000
  },
  "bootloader": {
    "size": 28672,
    "offset": "0x8000000"
  },
  "flash": {
    "total": 256,
    "available": 228
  },
  "usb": {
    "vid": "1D50",
    "pid": "614E",
    "interface": "stm32f103"
  },
  "serial": {
    "interface": "USB",
    "baudrate": 250000
  },
  "pins": {
    "led": "PC13",
    "uart_rx": "PA10",
    "uart_tx": "PA9"
  }
}
```

### 3. Firmware-Konfiguration

Erstelle eine Klipper-Konfiguration unter `configs/firmware/`:

```ini
[board_pins skr_mini_e3_v2]
mcu: skr_mini_e3_v2
# Steppers
step_pins: PB13, PB10, PB0, PB3
dir_pins: PB12, PB2, PC5, PB4
enable_pins: PB14, PB11, PB1, PD2
# Endstops
endstop_pins: PC0, PC1, PC2
# Heaters
heater_pins: PC8, PC9
temp_pins: PC3, PC4
fan_pins: PA8
```

### 4. Testen

1. Board anschließen
2. Firmware kompilieren
3. Bootloader-Modus aktivieren
4. Firmware flashen
5. Klipper-Verbindung testen

## 🔍 Debugging

### 1. USB-Erkennung

```bash
# USB-Geräte anzeigen
lsusb

# Detaillierte USB-Info
lsusb -v -d 1D50:614E

# udev-Regeln
cat /etc/udev/rules.d/99-klipper.rules
```

### 2. Serielle Verbindung

```bash
# Serielle Ports anzeigen
ls /dev/ttyUSB*
ls /dev/ttyACM*

# Port-Info
udevadm info -a -n /dev/ttyUSB0

# Serielle Kommunikation testen
screen /dev/ttyUSB0 250000
```

### 3. Firmware

```bash
# Firmware-Build-Output
cat out/klipper.elf.hex

# Bootloader-Info
dfu-util -l

# Flash-Speicher
st-info --probe
```

## 📝 Board-Spezifikationen

### STM32F103
```json
{
  "skr_mini_e3_v2": {
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

### STM32F446
```json
{
  "btt_octopus_pro": {
    "board": "STM32F446",
    "processor": "stm32f446xx",
    "bootloader": 32768,
    "compiler_flags": [
      "CONFIG_MACH_STM32F446=y",
      "CONFIG_CLOCK_FREQ=180000000"
    ]
  }
}
```

## 🛠️ Werkzeuge

### 1. Firmware-Tools
- `make menuconfig`
- `make flash`
- `dfu-util`
- `stm32flash`

### 2. Debug-Tools
- `stm32cubeprog`
- `openocd`
- `gdb`
- `miniterm.py`

### 3. Analyse-Tools
- `lsusb`
- `udevadm`
- `st-info`
- `usb-devices`

## 🚨 Fehlerbehebung

### 1. USB-Probleme
- VID/PID nicht erkannt
- Bootloader-Modus nicht aktiv
- Falsche Treiber

### 2. Firmware-Probleme
- Kompilierungsfehler
- Flash-Fehler
- Bootloader-Probleme

### 3. Klipper-Probleme
- MCU-Verbindungsfehler
- Konfigurationsfehler
- Pin-Konflikte

## 📞 Support

### Community

- [GitHub Issues](https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/issues)
- [Discord Server](https://discord.gg/Innovate3D-Labs)
- [Forum](https://forum.innovate3d-labs.com)

### Dokumentation

- [FAQ](https://docs.innovate3d-labs.com/boards/faq)
- [Board-Liste](https://docs.innovate3d-labs.com/boards/supported)
- [Flash-Anleitung](https://docs.innovate3d-labs.com/boards/flashing)
