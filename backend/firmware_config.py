"""
Konfigurationen für verschiedene Drucker-Boards
"""

# Mapping von Druckermodellen zu ihren Standard-Board-Konfigurationen
PRINTER_CONFIGS = {
    "ender3": {
        "board": "STM32F103",
        "processor": "stm32f103",
        "bootloader": 28672,  # 28KiB bootloader
        "clock_reference": "8000000",
        "serial": "/dev/ttyUSB0",
        "baud": 250000,
        "compiler_flags": [
            "CONFIG_MACH_STM32F103=y",
            "CONFIG_CLOCK_FREQ=72000000",
            "CONFIG_FLASH_START=0x8000000",
            "CONFIG_FLASH_SIZE=0x10000",
            "CONFIG_RAM_START=0x20000000",
            "CONFIG_RAM_SIZE=0x5000",
            "CONFIG_SMOOTHIEWARE_BOOTLOADER=y",
            "CONFIG_USBSERIAL=y",
            "CONFIG_SERIAL=y"
        ]
    },
    "voron2.4": {
        "board": "STM32F446",
        "processor": "stm32f446xx",
        "bootloader": 32768,  # 32KiB bootloader
        "clock_reference": "12000000",
        "serial": "/dev/ttyAMA0",
        "baud": 250000,
        "compiler_flags": [
            "CONFIG_MACH_STM32F446=y",
            "CONFIG_CLOCK_FREQ=180000000",
            "CONFIG_FLASH_START=0x8000000",
            "CONFIG_FLASH_SIZE=0x80000",
            "CONFIG_RAM_START=0x20000000",
            "CONFIG_RAM_SIZE=0x20000",
            "CONFIG_USBSERIAL=y",
            "CONFIG_SERIAL=y"
        ]
    },
    "ratrig_vcore3": {
        "board": "STM32F407",
        "processor": "stm32f407xx",
        "bootloader": 32768,  # 32KiB bootloader
        "clock_reference": "8000000",
        "serial": "/dev/ttyACM0",
        "baud": 250000,
        "compiler_flags": [
            "CONFIG_MACH_STM32F407=y",
            "CONFIG_CLOCK_FREQ=168000000",
            "CONFIG_FLASH_START=0x8000000",
            "CONFIG_FLASH_SIZE=0x100000",
            "CONFIG_RAM_START=0x20000000",
            "CONFIG_RAM_SIZE=0x20000",
            "CONFIG_USBSERIAL=y",
            "CONFIG_SERIAL=y"
        ]
    }
}

# Unterstützte USB-IDs für automatische Board-Erkennung
USB_IDS = {
    "1a86:7523": "STM32F103",  # CH340 Serial Converter (Ender 3)
    "0483:5740": "STM32F446",  # STM32 Virtual COM Port (Voron)
    "0483:df11": "STM32F407",  # STM32 DFU Mode
}
