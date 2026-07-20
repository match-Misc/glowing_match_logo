# 🎆 Glowing Match LED Display Controller

A PyQt6 GUI application for controlling an ESP32-C6 based LED display via Bluetooth Low Energy (BLE) or USB Serial.

## Features

- **Dual Connection**: BLE or USB Serial with runtime switching
- **LED Control**: ON/OFF buttons, brightness slider (0-100%)
- **Effects**: Word mode and individual letter effects (M/A/T/C/H)
- **Direct Commands**: Send custom commands to device
- **Auto-Detection**: COM port and device name auto-discovery
- **Error Handling**: Helpful messages with suggested solutions

## Installation

```bash
cd code/python_scripts
pip install -r requirements.txt
python led_app.py
```

## Usage

### BLE Connection (Default)
1. Power on device
2. Ensure Bluetooth is enabled
3. Device name defaults to "GlowingMatch"
4. Click **"Connect to Device"**

### Serial Connection
1. Connect ESP32 via USB
2. Select **"Serial"** from Connection Type dropdown
3. COM port auto-detects (or enter manually, e.g., COM3)
4. Click **"Connect to Device"**

### Controls

- **Power**: ON/OFF buttons
- **Brightness**: Drag slider for real-time adjustment
- **Word Effect**: Select effect for entire display → Apply
- **Letter Effects**: Independent effect selection for each letter
- **Custom Commands**: Use Direct Command section for testing

## Command Reference

```
on                 # Turn display on
off                # Turn display off
get_brightness     # Get current brightness
set_brightness,50  # Set brightness to 50%
get_word_mode      # Get word mode status
set_word_mode,ON   # Enable word mode
set_letter_effect,0,PULSE  # Set M to PULSE effect
```

See "Device Information" panel for complete list of available effects after connecting.

## Troubleshooting

**BLE: Device not found**
- Verify device is powered on
- Check device name is correct
- Restart Bluetooth on your computer

**Serial: COM Port Not Available**
- Check USB cable connection
- Verify device is powered
- Check Device Manager for correct COM port

**Serial: COM Port In Use**
- Close other applications using the port
- Disconnect and reconnect USB cable

**Status "Connected" but no response**
- Disconnect and reconnect
- Power cycle the device

## File Structure

```
glowing_match_logo/
├── README.md
├── .gitignore
├── list_of_components.xlsx
├── code/
│   ├── arduino_glowing_match_logo/      # ESP32 firmware
│   ├── python_scripts/                  # Python GUI and controllers
│   │   ├── led_app.py                   # Main GUI application
│   │   ├── ble_controller.py            # BLE communication
│   │   ├── serial_controller.py         # Serial communication
│   │   ├── requirements.txt             # Dependencies
│   │   └── implementation_documents/
│   └── ros2_pkg_glowing_match_logo/     # ROS2 package
├── cad/                                  # CAD design files
├── pcb/                                  # PCB design files
├── datasheets/                           # Component datasheets
├── photos/                               # Project photos
└── video/                                # Project videos
```

## Requirements

- Python 3.7+
- ESP32-C6 microcontroller
- USB cable (serial) or Bluetooth 4.0+ (BLE)

```bash
pip install PyQt6 bleak pyserial
```

## License

Personal project for Glowing Match LED Display Control

---

Viel Spaß mit deinem Glowing Match! 🎆
