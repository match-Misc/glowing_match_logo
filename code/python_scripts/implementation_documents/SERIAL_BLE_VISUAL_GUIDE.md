# LED App Serial/BLE GUI - Visual Guide

## Connection Panel Layout

### BLE Mode (Default)
```
┌─────────────────────────────────────────────────────────────────┐
│ Connection Type: [BLE ▼]  Device Name: [GlowingMatch    ]      │
│                                          Status: Not Connected   │
│                          [Connect to Device]  [Disconnect]      │
└─────────────────────────────────────────────────────────────────┘
```

### Serial Mode
```
┌─────────────────────────────────────────────────────────────────┐
│ Connection Type: [Serial ▼]  COM Port: [COM3  ]                │
│                                          Status: Not Connected   │
│                          [Connect to Device]  [Disconnect]      │
└─────────────────────────────────────────────────────────────────┘
```

## UI State Transitions

### Switching from BLE to Serial (While Disconnected)
```
Before:
  Device Name input: VISIBLE, enabled
  COM Port input: HIDDEN, disabled
  
User action: Select "Serial" from combo
  ↓
After:
  Device Name input: HIDDEN, disabled
  COM Port input: VISIBLE, enabled
  Log: "Switched to Serial connection mode"
```

### Switching Types While Connected
```
User action: Select different type while connected
  ↓
Warning dialog: "Connection Active - Please disconnect first"
  ↓
Result:
  - Connection type combo reverts to previous selection
  - UI remains unchanged
  - No state modification
```

## Connection Status Indicators

### Visual States

#### Not Connected (Initial)
```
Status: Not Connected        [Color: RED]
Connect button: ENABLED
Disconnect button: DISABLED
Input fields: ENABLED
Connection type combo: ENABLED
All control widgets: DISABLED (word mode, brightness, effects, etc.)
```

#### Connecting (In Progress)
```
Status: Connecting...        [Color: BLUE - if implemented]
Connect button: DISABLED
Output log shows:
  - "Scanning for devices..." (BLE mode)
  - "Connecting to {port}..." (Serial mode)
```

#### Connected
```
Status: Connected ✓          [Color: GREEN]
Connect button: DISABLED
Disconnect button: ENABLED
Device name/COM port input: DISABLED (can't change while connected)
Connection type combo: DISABLED (can't switch while connected)
All control widgets: ENABLED
Output log shows:
  - "✓ Connected successfully!" (BLE)
  - "✓ Connected to {port}" (Serial)
  - Device info loaded
```

#### Connection Error
```
Status: Not Connected        [Color: RED]
Error dialog: Shows specific error message
Output log shows: Error details
Connect button: ENABLED (for retry)
Disconnect button: DISABLED
Connection type combo: ENABLED (can try different mode)
```

## Device Information Display

### After Successful Connection
```
┌─────────────────────────────────────────────────────────────────┐
│ Device Information                                              │
├─────────────────────────────────────────────────────────────────┤
│ DEVICE INFORMATION                                              │
│ =====================================================================│
│                                                                  │
│ Word Mode: OFF                                                  │
│ Effects available: 14                                           │
│   - Effect 0: RAINBOW                                           │
│   - Effect 1: SOLID_COLOR                                       │
│   - Effect 2: PULSE                                             │
│   ... (complete list)                                           │
│                                                                  │
│ Current Brightness: 28% (71/255)                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Control Sections (Enabled After Connection)

### Word Mode Effect
```
Word Effect: [EFFECT_NAME ▼]
  - Shows effect name (e.g., "RAINBOW")
  - Dropdown populated from device
  - Updates on selection
```

### Brightness Control
```
Brightness: [════════░░░░░░░░░░░] 28%
  - Slider range: 0-100%
  - Display shows percentage
  - Updates on slider change
```

### Letter Effects (M/A/T/C/H)
```
M: [EFFECT ▼]  A: [EFFECT ▼]  T: [EFFECT ▼]  C: [EFFECT ▼]  H: [EFFECT ▼]
  - Each letter has independent effect selector
  - Effects populate from device list
  - Width scales with window
```

### Direct Command
```
┌─────────────────────────────────────────────────────────────────┐
│ Direct Command                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Command: [get_brightness                    ] [Send Command]   │
│                                                                  │
│ Output:                                                         │
│ ✓ Sent: get_brightness                                          │
│ ← Current brightness: 28% (71/255)                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Message Dialogs

### Connection Error Examples

#### BLE Device Not Found
```
╔════════════════════════════════════════════════╗
║           Connection Error                    ║
╠════════════════════════════════════════════════╣
║ Target device 'GlowingMatch' not found!       ║
║ Make sure the device name is correct and the  ║
║ device is powered on.                         ║
║                                              ║
║                          [OK]                ║
╚════════════════════════════════════════════════╝
```

#### Serial Connection Error
```
╔════════════════════════════════════════════════╗
║           Connection Error                    ║
╠════════════════════════════════════════════════╣
║ Connection error: [Errno 5] Access is denied: ║
║ 'COM3'                                        ║
║                                              ║
║                          [OK]                ║
╚════════════════════════════════════════════════╝
```

#### Invalid Input
```
╔════════════════════════════════════════════════╗
║            Invalid Input                      ║
╠════════════════════════════════════════════════╣
║ Please enter a COM port                       ║
║                                              ║
║                          [OK]                ║
╚════════════════════════════════════════════════╝
```

### Mid-Connection Type Switch
```
╔════════════════════════════════════════════════╗
║            Connection Active                  ║
╠════════════════════════════════════════════════╣
║ Please disconnect before switching connection ║
║ type.                                         ║
║                                              ║
║                          [OK]                ║
╚════════════════════════════════════════════════╝
```

## Output Log Examples

### BLE Connection Success
```
Scanning for devices...
Found device: GlowingMatch
Connecting to GlowingMatch...
✓ Connected successfully!
Loading device information...
✓ Device info loaded:
  Word Mode: OFF
  Effects: 14
  Brightness: 28%
```

### Serial Connection Success
```
Connecting to COM3...
✓ Connected to COM3
Loading device information...
✓ Device info loaded:
  Word Mode: OFF
  Effects: 14
  Brightness: 28%
```

### Type Switch Feedback
```
Switched to Serial connection mode
Switched to BLE connection mode
```

### Command Execution
```
✓ Sent: get_brightness
← Current brightness: 28% (71/255)

✓ Sent: set_word_effect,RAINBOW
← OK

✓ Sent: set_brightness,50
← OK
```

### Disconnection
```
✓ Disconnected
```

### Connection Loss
```
⚠ Device disconnected! (Reconnection failed)
```

## Window Behavior

### On Launch
```
1. Combo defaults to "BLE"
2. Device name field shown, COM port hidden
3. Status shows "Not Connected" (red)
4. All control buttons disabled
5. Output area empty
6. User can change connection type before connecting
```

### After Successful Connection
```
1. Device info populates
2. Status shows "Connected ✓" (green)
3. All control widgets become functional
4. Brightness slider shows current value
5. Effect combos show current selections
6. User can send commands
7. User can switch between tabs (word effect, letter effects, commands)
```

### After Disconnection
```
1. Status returns to "Not Connected" (red)
2. All control widgets disabled
3. Device info clears
4. User can change connection type again
5. User can reconnect (same type or different)
```

### On Connection Error
```
1. Error dialog appears with specific message
2. Status remains "Not Connected" (red)
3. Error logged to output area
4. Connection type remains as selected (user can try other type)
5. Connect button re-enabled for retry
```

## Responsive Design

### Window Resizing
```
- Connection panel: Full width, fixed height
- Controls scale: Letter effect combos expand with window width
- Device info: Grows vertically, text area expands
- Command section: Input field expands horizontally
- All buttons: Maintain relative proportions
```

### Text Wrapping
```
- Long device names: Truncated in display
- Long effect names: Shown in full in dropdowns
- Log messages: Wrapped to window width
- Error messages: Centered in dialog box
```
