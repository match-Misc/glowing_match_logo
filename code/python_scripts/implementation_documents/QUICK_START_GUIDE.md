# LED App Quick Start Guide

## Overview
The LED Control Application is a PyQt6 GUI for managing an ESP32-C6 based Glowing Match LED display. It supports both Bluetooth Low Energy (BLE) and USB Serial connections.

## Prerequisites

### For BLE Connection
- Bluetooth 5.0+ compatible device (laptop, desktop, Raspberry Pi)
- Glowing Match device powered on and in range
- Device name set to "GlowingMatch" (or configured in app)

### For Serial Connection
- USB cable connected to ESP32-C6
- Device Manager showing COM port (Windows)
- No other application using the COM port

### Python Requirements
```bash
pip install PyQt6 bleak pyserial asyncio
```

## Running the Application

### Windows
```powershell
python led_app.py
```

### macOS/Linux
```bash
python3 led_app.py
```

## First Time Setup

### BLE Connection (Default)

1. **Launch the app** - Default mode is BLE
2. **Check device name** - Default is "GlowingMatch"
   - Change if your device has different name
3. **Click "Connect to Device"**
   - App will scan for devices
   - Scanning takes 2-5 seconds
   - If successful, status shows "Connected ✓" (green)

### Serial Connection

1. **Launch the app**
2. **Switch connection type:**
   - Click "Connection Type" dropdown
   - Select "Serial"
   - Device name field disappears
   - COM port field appears
3. **Enter COM port:**
   - Default: COM3
   - Check Device Manager if unsure (Windows)
   - Or use serial port listing tool
4. **Click "Connect to Device"**
   - Connection should be instant
   - Status shows "Connected ✓" (green)

## Using the Application

### Connection Panel (Top)
```
Connection Type: [BLE ▼]        Device Name: [GlowingMatch]
                                              Status: Not Connected
                            [Connect to Device]  [Disconnect]
```

- **Connection Type**: Switch between BLE and Serial
- **Device Name** (BLE): Name of your Glowing Match device
- **COM Port** (Serial): USB serial port number
- **Status**: Shows connection state (red=disconnected, green=connected)
- **Buttons**: Connect or disconnect from device

### Device Information
After connecting, you'll see:
- **Word Mode**: ON or OFF
- **Effects Available**: Number of effects (usually 14)
- **Current Brightness**: Percentage and 8-bit value

### Word Mode Effect
Set the display effect for the entire word (if word mode is ON):
1. Select effect from dropdown
2. Display updates immediately

### Brightness Control
Adjust overall brightness:
1. Drag slider from 0-100%
2. Display updates as you drag
3. Brightness persists on device

### Letter Effects (M/A/T/C/H)
Set individual effect for each letter:
1. Each letter has independent dropdown
2. Select effect for M, A, T, C, H
3. Display shows all effects simultaneously

### Direct Command
Send custom commands directly:
1. Type command (e.g., `get_brightness`)
2. Click "Send Command"
3. Response appears in output
4. Useful for testing and diagnostics

## Switching Between Connections

### To Switch from BLE to Serial:

```
1. Make sure device is DISCONNECTED
   ↓
2. Click Connection Type dropdown
   ↓
3. Select "Serial"
   ↓
   Device name input disappears
   COM port input appears
   ↓
4. Enter your COM port (e.g., COM3)
   ↓
5. Click "Connect to Device"
```

### To Switch from Serial to BLE:

```
1. Make sure device is DISCONNECTED
   ↓
2. Click Connection Type dropdown
   ↓
3. Select "BLE"
   ↓
   COM port input disappears
   Device name input appears
   ↓
4. Verify device name is correct
   ↓
5. Click "Connect to Device"
```

**Important:** Cannot change connection type while connected. App will show warning if you try.

## Troubleshooting

### "Device Not Found" Error (BLE)

**Symptoms:**
```
Connection Error
Target device 'GlowingMatch' not found!
Make sure the device name is correct and the device is powered on.
```

**Solutions:**
1. Check device is powered on
2. Check device is within Bluetooth range
3. Verify device name is correct
   - Default: "GlowingMatch"
   - Check device settings if different
4. Restart Bluetooth on your computer
5. Restart the Glowing Match device

### "Access Denied" Error (Serial)

**Symptoms:**
```
Connection Error
Connection error: [Errno 5] Access is denied: 'COM3'
```

**Solutions:**
1. Check correct COM port:
   - Windows: Device Manager → Ports (COM & LPT)
   - macOS: `ls /dev/tty.usbserial*`
   - Linux: `ls /dev/ttyUSB*`
2. Close any other applications using the port
3. Try different COM port if available
4. Check USB cable connection
5. Try different USB port on computer

### No Connection Type Dropdown Visible

**Symptom:** Only see "Device Name" field, no connection type selector

**Solution:**
- Update `led_app.py` - the file may be outdated
- Ensure latest version is running

### Device Connects But No Response

**Symptoms:**
- Shows "Connected ✓" but commands don't work
- Device info not loading

**Solutions (BLE):**
1. Check device is responsive (LED should show signs of life)
2. Try disconnecting and reconnecting
3. Check device software version
4. Restart both device and computer

**Solutions (Serial):**
1. Check baud rate is 115200
2. Verify USB cable is fully connected
3. Check device responds to serial commands
4. Use `serial_controller.py` test script

### App Crashes on Connect

**Solution:**
1. Check Python version (requires 3.7+)
2. Verify all packages installed: `pip list | grep -E "PyQt6|bleak|pyserial"`
3. Try updating packages: `pip install --upgrade PyQt6 bleak pyserial`
4. Check for error messages in console output
5. Report issue with console output

## Common Commands

### Getting Device Information
```
get_word_mode       → Get current word mode (ON/OFF)
get_brightness      → Get current brightness (percent and 8-bit)
get_effects         → Get list of available effects
```

### Setting Device Information
```
set_brightness,50       → Set brightness to 50%
set_word_mode,ON        → Enable word mode
set_word_mode,OFF       → Disable word mode
set_word_effect,RAINBOW → Set word effect
set_letter_effect,0,RAINBOW  → Set M effect to RAINBOW
```

### Effect Names (Common)
```
RAINBOW
SOLID_COLOR
PULSE
TWINKLE
CHASE
WAVE
STROBE
FADE
SPARKLE
```

## Tips and Tricks

### 1. Persistent Settings
- Device remembers last settings
- Brightness persists after power off
- Effect settings are temporary (reset on power)

### 2. Finding Your COM Port (Windows)
1. Open Device Manager (Win+X → Device Manager)
2. Expand "Ports (COM & LPT)"
3. USB device should show as "COM#"
4. Use that number (e.g., COM3)

### 3. Finding Your COM Port (macOS/Linux)
```bash
# macOS
ls /dev/tty.usbserial*

# Linux
ls /dev/ttyUSB*
dmesg | grep ttyUSB
```

### 4. Device Name Configuration
If your device has custom name:
1. Check device settings
2. Update device name in app
3. Leave "GlowingMatch" default if unsure

### 5. Testing with Direct Command
Great way to verify connection:
1. Connect to device
2. Enter: `get_brightness`
3. Send command
4. Should see response with current brightness
5. If this works, app is communicating correctly

### 6. Switching Devices
To use app with different device:
1. Disconnect from current device
2. Change connection type (if needed)
3. Update device name or COM port
4. Click "Connect to Device"

## Performance Notes

### BLE (Bluetooth)
- **Pros:** Wireless, no cables, wider range
- **Cons:** Slower (2-5s scan, 1-2s per command)
- **Use case:** Mobile devices, Raspberry Pi, laptops in different rooms

### Serial (USB)
- **Pros:** Fast, reliable, no pairing needed
- **Cons:** Requires USB cable, range limited by cable
- **Use case:** Desktop setup, development, high-volume command sending

## Advanced Usage

### Terminal Testing (BLE)
```bash
# Run BLE controller directly
python ble_controller.py

# (Choose option to test connection)
```

### Terminal Testing (Serial)
```bash
# Run serial controller directly
python serial_controller.py

# Select your COM port when prompted
```

### Check Device Compatibility
```bash
# BLE compatibility
python -c "from bleak import BleakClient; print('BLE OK')"

# Serial compatibility
python -c "import serial; print('Serial OK')"

# PyQt6 compatibility
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Alt+C | Focus to Connect button |
| Alt+D | Focus to Disconnect button |
| Tab | Move between fields |
| Enter | In command field, send command |

## Settings Reset

To reset to defaults:
1. Close application
2. Edit `led_app.py`
3. Change line with `self.device_name_input.setText("GlowingMatch")`
4. Change line with `self.com_port_input.setText("COM3")`
5. Save and restart

## Getting Help

### Check Log Output
- All messages appear in output area at bottom
- Scroll through output for error details
- Copy error message for support

### Basic Checks
1. Is device powered on?
2. Is device within Bluetooth range (BLE)?
3. Is USB cable connected properly (Serial)?
4. Are other apps using the connection?
5. Does device respond to manual commands?

### For Support
- Check IMPLEMENTATION_DETAILS.md for technical info
- Review error messages carefully
- Note exact error text
- Describe what connection type you're using
- Provide output log excerpt

## Next Steps

After successful connection, try:
1. **View device info** - See what effects are available
2. **Test brightness** - Drag brightness slider
3. **Try word effect** - Select effect from dropdown
4. **Set letter effects** - Create custom patterns
5. **Send commands** - Test with direct command input
6. **Switch connection types** - Verify both work
7. **Disconnect/reconnect** - Verify reliability

Enjoy controlling your Glowing Match display!
