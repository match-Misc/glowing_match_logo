# 🎆 Glowing Match LED Display Controller

A professional PyQt6 GUI application for controlling an ESP32-C6 based LED display via Bluetooth Low Energy (BLE) or USB Serial connection.

## Features

### 🔌 Dual Connection Support
- **Bluetooth Low Energy (BLE)** - Wireless control with device name detection
- **USB Serial** - Direct wired connection with auto port detection
- Runtime switching between connection types without restarting

### 🎨 LED Display Control
- **Power Control** - ON/OFF buttons with visual feedback
- **Brightness Control** - Slider-based adjustment (0-100%)
- **Word Mode Effects** - Set single effect for entire display
- **Individual Letter Effects** - Control M/A/T/C/H letters independently
- **Effect Library** - Full list of available effects loaded from device

### 📊 Device Information
- Real-time device status and information display
- Auto-detection of available effects
- Current brightness monitoring
- Word mode status

### 🛠️ Advanced Features
- Direct command input for custom control
- Responsive UI with scalable components
- Comprehensive error handling with helpful messages
- Available COM port listing on connection errors
- Device connection logging and debugging

## Installation

### Requirements
- Python 3.7+
- Windows, macOS, or Linux

### Setup

1. **Clone or download the repository**
```bash
cd glowing_match_logo
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python led_app.py
```

## Usage

### BLE Connection (Default)

1. Power on your Glowing Match device
2. Ensure Bluetooth is enabled on your computer
3. Leave "Connection Type" as **BLE**
4. Device name defaults to "GlowingMatch" (change if different)
5. Click **"Connect to Device"**

### Serial Connection

1. Connect ESP32 via USB cable
2. Select **"Serial"** from "Connection Type" dropdown
3. COM port auto-detects (or enter manually, e.g., COM3)
4. Click **"Connect to Device"**

### Switching Connection Types

- Disconnect first if currently connected
- Select new connection type from dropdown
- Device name/COM port field updates automatically
- Reconnect with new type

### Controlling the Display

#### Power
- **ON** - Turn display on (green button)
- **OFF** - Turn display off (red button)

#### Brightness
- Drag the brightness slider (0-100%)
- Changes apply in real-time

#### Word Effect (Entire Display)
1. Select effect from "Word Mode Effect" dropdown
2. Click **"Apply"**

#### Letter Effects (Individual Control)
1. Select effect for each letter: M, A, T, C, H
2. Dropdown auto-selects based on available effects
3. Changes apply immediately

#### Custom Commands
- Use "Direct Command" section to send custom commands
- Examples: `get_brightness`, `set_brightness,50`, `on`, `off`
- Response appears in output area

## File Structure

```
glowing_match_logo/
├── led_app.py              # Main PyQt6 GUI application
├── ble_controller.py       # BLE communication handler
├── serial_controller.py    # Serial communication handler
├── requirements.txt        # Python package dependencies
├── README.md              # This file
└── arduino_glowing_match_logo/
    ├── arduino_glowing_match_logo.ino
    ├── BLECommandHandler.cpp/h
    ├── ButtonHandler.cpp/h
    ├── Config.h
    ├── DisplayObjects.cpp/h
    ├── Effects.cpp/h
    ├── PersistentState.h
    ├── SerialCommandHandler.cpp/h
    └── StateManager.cpp/h
```

## Troubleshooting

### BLE Connection Issues

**"Device not found" error**
- Ensure device is powered on
- Check device name is correct (default: "GlowingMatch")
- Verify Bluetooth is enabled on your computer
- Try restarting device and computer

### Serial Connection Issues

**"COM Port Not Available"**
- Check USB cable is properly connected
- Verify device is powered on
- Check Device Manager for correct COM port
- Ensure no other application is using the port

**"COM Port In Use"**
- Close other applications using the port
- Disconnect and reconnect USB cable
- Restart the application

**"Device Not Responding"**
- Verify ESP32 device is powered
- Check device firmware is running
- Try resetting the device

### General Issues

**Status shows "Connected" but commands don't work**
- Disconnect and reconnect
- Check device is functioning (check LED display)
- Try power cycling the device

**GUI window is unresponsive**
- Wait a few seconds (scanning/connection can take time)
- Click "Disconnect" to reset state
- Restart the application

## Command Reference

### Basic Commands
```
on                 # Turn display on
off                # Turn display off
get_brightness     # Get current brightness
set_brightness,50  # Set brightness to 50%
get_word_mode      # Get word mode status
set_word_mode,ON   # Enable word mode
set_word_mode,OFF  # Disable word mode
```

### Effect Commands
```
get_effects                    # List all available effects
set_word_effect,RAINBOW        # Set word effect
set_letter_effect,0,PULSE      # Set M (letter 0) to PULSE effect
```

## Supported Effects

Common effects (varies by device):
- RAINBOW
- SOLID_COLOR
- PULSE
- TWINKLE
- CHASE
- WAVE
- STROBE
- FADE
- SPARKLE
- (and more based on device firmware)

See "Device Information" panel for complete list after connecting.

## Connection Modes Comparison

| Feature | BLE | Serial |
|---------|-----|--------|
| Range | Up to 100m | Limited by cable |
| Speed | Slower (2-5s scan) | Fast (<1s) |
| Cables | None | USB required |
| Pairing | Yes | No |
| Best for | Mobile, Remote | Desktop, Development |

## Architecture

### Threading Model
- **Main GUI Thread** - Handles all UI updates
- **Connection Worker Thread** - Manages device connections
- **Command Worker Thread** - Sends/receives commands
- **Async Event Loop** - Handles async operations

All communication is thread-safe using Qt signals/slots.

### Error Handling
- Specific error detection for serial issues
- Helpful error messages with suggestions
- Graceful fallbacks for missing features
- State recovery on connection loss

## Development

### Adding New Commands

1. Use the "Direct Command" field to test
2. Once working, integrate into GUI
3. Add button/control as needed

### Modifying Connection Behavior

- Edit `connect_ble()` or `connect_serial()` methods
- Modify error handling in `format_serial_error()`
- Adjust timeout values in AsyncWorker

### Custom Effects

Edit the ESP32 firmware and update the effects list in:
- `ble_controller.py` - effects loading logic
- `serial_controller.py` - effects loading logic

## Known Limitations

1. **Type switching requires disconnect** - Can't switch connection type while connected
2. **Single device at a time** - Only one connection active
3. **Serial baudrate fixed** - Set to 115200 (matches ESP32 default)
4. **No connection profiles** - Settings not saved between sessions

## Performance

### BLE Connection
- Scan time: 2-5 seconds
- Command latency: 200-500ms
- Bandwidth: ~100 bytes/second

### Serial Connection
- Connection time: <100ms
- Command latency: 100-300ms
- Bandwidth: ~10KB/second

## Requirements

### Python Packages
- **PyQt6** (≥6.0.0) - GUI framework
- **bleak** (≥0.20.0) - Bluetooth Low Energy
- **pyserial** (≥3.5) - Serial communication

### Hardware
- ESP32-C6 microcontroller (or compatible)
- USB cable (for serial connection)
- Bluetooth 5.0+ radio (for BLE connection)

## License

Project for Glowing Match LED Display Control

## Support

For issues or questions:
1. Check troubleshooting section
2. Review device information in app
3. Test with direct command input
4. Check device firmware on ESP32

## Credits

**GUI Application**: PyQt6 LED Controller  
**BLE Support**: Bleak library  
**Serial Support**: PySerial library  
**Hardware**: ESP32-C6 microcontroller  

---

**Version**: 1.0.0  
**Last Updated**: April 20, 2026

Viel Spaß mit deinem Glowing Match LED Display! 🎆
