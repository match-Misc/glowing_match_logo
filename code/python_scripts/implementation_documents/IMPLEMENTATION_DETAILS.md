# Serial/BLE Integration - Implementation Details for Developers

## Architecture Overview

### Core Design Pattern: Strategy Pattern with Worker Threads

The implementation uses a **Strategy Pattern** where connection logic is abstracted behind two worker classes:
- `ConnectionWorker`: BLE connection strategy
- `SerialConnectionWorker`: Serial connection strategy

Both workers implement identical signal interfaces, allowing the GUI to treat them as interchangeable.

```
┌──────────────────────────────────────┐
│   LEDControllerGUI (Main Window)     │
└────────────────┬─────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
    ┌────▼─────────┐  ┌──▼───────────────┐
    │ ConnectionWorker  │ SerialConnection  │
    │ (BLE scanning)    │ Worker (Serial)   │
    └────┬─────────┘  └──┬───────────────┘
         │                │
         ├───────────┬────┤
         │           │    │
    ┌────▼──┐  ┌────▼───┐ │
    │ BLE    │  │ Serial │ │
    │Ctrl    │  │ Ctrl   │ │
    └────────┘  └────────┘ │
                            │
                    ┌───────▼────────┐
                    │ AsyncWorker    │
                    │ (Event loop)   │
                    └────────────────┘
```

### Thread Model

```
Main GUI Thread (Qt Event Loop)
  ├─ UI updates (always here)
  ├─ Signal/slot connections
  └─ Direct user interaction handling
      │
      └─ Spawns QThread for:
         ├─ ConnectionWorker.connect_device()
         ├─ ConnectionWorker.disconnect_device()
         ├─ SerialConnectionWorker.connect_device()
         ├─ SerialConnectionWorker.disconnect_device()
         └─ CommandWorker.send_command()
             │
             └─ Each worker's AsyncWorker runs:
                ├─ Device scanning (BLE)
                ├─ Connection establishment
                └─ Async command execution
```

**Key Thread Safety Points:**
1. All GUI updates happen in main thread via Qt signals
2. Async operations run in worker's event loop (separate thread)
3. Worker threads communicate with main thread through Qt signals
4. No direct Qt object manipulation from worker threads

## Class Architecture

### 1. AsyncWorker (Utility Worker)
**Purpose:** Run asyncio coroutines in a non-blocking way from Qt

**Key Method:**
```python
def run_async(self, coro):
    """Run async coroutine and return result synchronously"""
    future = asyncio.run_coroutine_threadsafe(coro, self.loop)
    return future.result(timeout=30)
```

**Signals:** None (internal use only)

**Thread:** Runs in its own event loop thread

### 2. ConnectionWorker (BLE Strategy)
**Purpose:** Handle BLE-specific connection operations

**Signals:**
- `finished`: Emitted when operation completes (success or failure)
- `error(str)`: Emitted on error with error message
- `success`: Emitted on successful connection
- `log(str)`: Emitted for logging/UI feedback

**Key Methods:**
```python
def connect_device(self):
    # Scan for BLE devices
    # Find target device by name
    # Connect to device
    # Emit success or error
    
def disconnect_device(self):
    # Call controller.disconnect()
    # Emit success
```

**Controller Used:** `LEDControllerBLE`

### 3. SerialConnectionWorker (Serial Strategy)
**Purpose:** Handle Serial-specific connection operations

**Signals:** Identical to ConnectionWorker

**Key Methods:**
```python
def connect_device(self):
    # Validate port is specified
    # Call controller.connect()
    # Emit success or error
    
def disconnect_device(self):
    # Call controller.disconnect()
    # Emit success
```

**Controller Used:** `LEDControllerSerial`

**Key Difference:** No scanning phase (port is pre-specified)

### 4. LEDControllerGUI (Main Window)
**Purpose:** Provide user interface and coordinate between workers and controllers

**Key Attributes:**
```python
self.connection_type: str          # "BLE" or "Serial"
self.controller: LEDController*    # BLE or Serial controller
self.connected: bool               # Connection state
self.conn_thread: QThread          # Worker thread
self.conn_worker: QObject          # ConnectionWorker or SerialConnectionWorker
```

**Key Methods for Connection Management:**
```python
def connect_device(self):
    # Dispatcher - routes to appropriate connect method
    
def connect_ble(self):
    # Create LEDControllerBLE
    # Create ConnectionWorker
    # Start worker thread
    
def connect_serial(self):
    # Create LEDControllerSerial
    # Create SerialConnectionWorker
    # Start worker thread
    
def disconnect_device(self):
    # Create appropriate worker based on type
    # Run disconnect in worker thread
    
def on_connection_type_changed(self, type: str):
    # Validate not connected
    # Toggle input field visibility
    # Log mode switch
```

## Data Flow: Connection Establishment

### BLE Path (Step-by-Step)

```
1. User clicks "Connect" (BLE mode)
   └─ connect_device() called
   
2. connect_device() dispatcher
   └─ connection_type = "BLE"
   └─ connect_ble() called
   
3. connect_ble() setup
   └─ Extract device_name from input field
   └─ Validate device_name not empty
   └─ Create LEDControllerBLE(device_name)
   └─ Create ConnectionWorker(controller)
   └─ Create QThread
   
4. Connect signals
   └─ thread.started → worker.connect_device()
   └─ worker.log → GUI.log_output()
   └─ worker.error → GUI.on_connection_error()
   └─ worker.success → GUI.on_connect_success()
   └─ worker.finished → GUI.on_connection_finished()
   
5. thread.start()
   └─ Spawns new thread
   
6. Worker thread executes:
   ConnectionWorker.connect_device()
   ├─ Emit log: "Scanning for devices..."
   ├─ AsyncWorker.run_async(controller.scan_devices())
   │  ├─ Scan BLE devices
   │  └─ Return (list, target_device)
   ├─ Check if target found
   │  ├─ If not found:
   │  │  ├─ Emit error with device name
   │  │  ├─ Emit finished
   │  │  └─ Return
   │  └─ If found:
   │     └─ Emit log: "Connecting to {name}..."
   ├─ AsyncWorker.run_async(controller.connect(device))
   │  ├─ Establish BLE connection
   │  ├─ Load device info (word_mode, effects, brightness)
   │  └─ Return success boolean
   ├─ Emit log: "✓ Connected successfully!"
   ├─ Emit success
   └─ Emit finished
   
7. GUI thread receives success signal
   └─ on_connect_success() called
   ├─ Set self.connected = True
   ├─ update_connection_status(True)
   │  ├─ Show "Connected ✓" (green)
   │  ├─ Disable input fields and connection type combo
   │  ├─ Enable all control widgets
   │  └─ Enable disconnect button
   ├─ update_device_info()
   │  ├─ Format and display effects list
   │  ├─ Display word mode setting
   │  └─ Display current brightness
   └─ Populate effect dropdowns from device data
   
8. Worker cleanup
   └─ on_connection_finished() called
   ├─ Delete worker (deleteLater())
   ├─ Quit and wait for thread
   └─ Clear conn_worker and conn_thread references
```

### Serial Path (Step-by-Step)

```
1. User clicks "Connect" (Serial mode)
   └─ connect_device() called
   
2. connect_device() dispatcher
   └─ connection_type = "Serial"
   └─ connect_serial() called
   
3. connect_serial() setup
   └─ Extract com_port from input field
   └─ Validate com_port not empty
   └─ Create LEDControllerSerial(port=com_port)
   └─ Create SerialConnectionWorker(controller)
   └─ Create QThread
   
4. Connect signals
   └─ thread.started → worker.connect_device()
   └─ worker.log → GUI.log_output()
   └─ worker.error → GUI.on_connection_error()
   └─ worker.success → GUI.on_connect_success()
   └─ worker.finished → GUI.on_connection_finished()
   
5. thread.start()
   └─ Spawns new thread
   
6. Worker thread executes:
   SerialConnectionWorker.connect_device()
   ├─ Validate controller.port is set
   │  └─ If not: Emit error "COM port not specified"
   ├─ Emit log: "Connecting to {port}..."
   ├─ AsyncWorker.run_async(controller.connect())
   │  ├─ Open serial port (baudrate 115200)
   │  ├─ Load device info (word_mode, effects, brightness)
   │  └─ Return success
   ├─ Emit log: "✓ Connected to {port}"
   ├─ Emit success
   └─ Emit finished
   
7. GUI thread receives success signal
   └─ [Same as BLE step 7]
   
8. Worker cleanup
   └─ [Same as BLE step 8]
```

## Data Flow: Connection Type Switch

```
User selects different type in combo
  │
  └─ currentTextChanged signal
     └─ on_connection_type_changed(selected_type)
        │
        ├─ Check: if self.connected?
        │  ├─ YES:
        │  │  ├─ Show warning dialog
        │  │  ├─ Block combo signals
        │  │  ├─ Set combo to previous selection
        │  │  ├─ Unblock combo signals
        │  │  └─ Return (no change made)
        │  │
        │  └─ NO:
        │     ├─ Update self.connection_type = selected_type
        │     │
        │     ├─ if selected_type == "BLE":
        │     │  ├─ Show device_name_input
        │     │  ├─ Hide com_port_label and com_port_input
        │     │  └─ Log "Switched to BLE connection mode"
        │     │
        │     └─ else (Serial):
        │        ├─ Hide device_name_input
        │        ├─ Show com_port_label and com_port_input
        │        └─ Log "Switched to Serial connection mode"
        │
        └─ GUI instantly reflects changes
           User can now enter appropriate connection details
```

## Data Flow: Disconnection

```
User clicks "Disconnect"
  │
  └─ disconnect_device()
     │
     ├─ Disable disconnect button (prevent double-click)
     │
     ├─ if self.conn_thread exists:
     │  ├─ Quit thread
     │  └─ Wait for thread termination
     │
     ├─ Create appropriate worker:
     │  ├─ if self.connection_type == "BLE":
     │  │  └─ Create ConnectionWorker(controller)
     │  └─ else:
     │     └─ Create SerialConnectionWorker(controller)
     │
     ├─ Create QThread and move worker to it
     │
     ├─ Connect signals
     │  ├─ thread.started → worker.disconnect_device()
     │  ├─ worker.log → GUI.log_output()
     │  ├─ worker.error → GUI.on_disconnect_error()
     │  ├─ worker.success → GUI.on_disconnect_success()
     │  └─ worker.finished → GUI.on_connection_finished()
     │
     └─ thread.start()
        │
        └─ Worker thread:
           worker.disconnect_device()
           ├─ AsyncWorker.run_async(controller.disconnect())
           │  ├─ Close BLE/Serial connection
           │  └─ Clean up resources
           ├─ Emit log: "✓ Disconnected"
           ├─ Emit success
           └─ Emit finished
              │
              └─ GUI thread receives success signal
                 on_disconnect_success()
                 ├─ Set self.connected = False
                 ├─ update_connection_status(False)
                 │  ├─ Show "Not Connected" (red)
                 │  ├─ Enable input fields and connection type combo
                 │  ├─ Disable all control widgets
                 │  └─ Disable disconnect button
                 └─ Clear device info display
                    │
                    └─ on_connection_finished() cleanup
                       ├─ Delete worker
                       ├─ Quit and wait for thread
                       └─ Clear references
```

## Error Handling Strategy

### Connection Errors

```
1. Input Validation Errors
   ├─ Empty device name (BLE)
   │  └─ Show warning: "Please enter a device name"
   ├─ Empty COM port (Serial)
   │  └─ Show warning: "Please enter a COM port"
   └─ No error signal emitted (caught before worker creation)

2. Device/Port Availability Errors
   ├─ BLE device not found
   │  └─ Worker emits error: "Target device 'X' not found!..."
   ├─ Serial port unavailable
   │  └─ Worker emits error: "Connection error: [Errno 5]..."
   └─ Error signal → on_connection_error()
      ├─ Show error dialog
      ├─ Log error to output
      └─ Keep connect button enabled (for retry)

3. Connection Establishment Errors
   ├─ BLE connection fails mid-transfer
   │  └─ Worker catches exception
   └─ Serial connection fails mid-transfer
      └─ Worker catches exception
      │
      └─ Error signal → on_connection_error()
         ├─ Show error details dialog
         ├─ Log full exception
         └─ Allow retry with same or different type
```

### Disconnect Errors

```
1. Unexpected Disconnection During Operation
   ├─ CommandWorker detects connection loss
   │  ├─ Check controller.is_connected()
   │  ├─ If false, emit connection_lost signal
   │  └─ on_device_disconnected() called
   │     ├─ Reset UI to disconnected state
   │     ├─ Show warning: "Device disconnected!..."
   │     └─ Attempt auto-reconnect (BLE only)

2. Graceful Disconnect
   └─ User clicks Disconnect
      ├─ Worker runs controller.disconnect()
      ├─ Emit success signal
      └─ on_disconnect_success() updates UI
```

### Thread Cleanup Errors

```
Error: "QThread: Destroyed while thread is still running"
├─ Cause: Worker didn't finish before cleanup
└─ Solution:
   ├─ Wrap deleteLater() in try-except
   ├─ Catch RuntimeError if worker already deleted
   └─ Ensure thread.quit() and wait() before deletion
```

## Signal Flow Diagram

```
Qt Signal → Slot Connections for BLE Connection:

Worker Thread                    Main GUI Thread
────────────────────────────────────────────────────
ConnectionWorker
├─ log.emit("Scanning...")   ──→ log_output()
├─ log.emit("Connecting...")  ──→ log_output()
├─ success.emit()             ──→ on_connect_success()
│                                 ├─ update_connection_status(True)
│                                 ├─ update_device_info()
│                                 └─ populate controls
├─ finished.emit()            ──→ on_connection_finished()
│                                 └─ Cleanup thread/worker
└─ [if error]
   └─ error.emit("Message")   ──→ on_connection_error()
                                  ├─ show_error()
                                  ├─ log_output()
                                  └─ keep UI in error state

Identical pattern for SerialConnectionWorker
```

## State Machine

### Connection States

```
                    ┌─────────────────┐
                    │  NOT_CONNECTED  │
                    └────────┬────────┘
                             │
                 click Connect or reconnect logic
                             │
                             ▼
                    ┌─────────────────┐
                    │  CONNECTING     │
         ┌─────────▶│  (worker busy)  │◀─────────┐
         │          └────────┬────────┘          │
         │                   │                   │
    error.emit()      success.emit()        timeout/crash
         │                   │                   │
         ▼                   ▼                   │
    ┌─────────┐      ┌──────────────┐           │
    │  ERROR  │      │  CONNECTED   │───────────┘
    │  STATE  │      │ (user can    │
    └────┬────┘      │  use app)    │
         │           └──────┬───────┘
    retry button              │
         │              click Disconnect
         │                   │
         │                   ▼
         │          ┌─────────────────┐
         │          │ DISCONNECTING   │
         │          │  (worker busy)  │
         │          └────────┬────────┘
         │                   │
         │           finished.emit()
         │                   │
         └───────────────────┘
```

### Connection Type States

```
         Initial
            │
            ▼
        ┌─────────┐
        │   BLE   │ ◀─────────┐
        └────┬────┘           │
             │                │
             │ User selects   │ User selects
             │ Serial & not   │ BLE & not
             │ connected      │ connected
             │                │
             ▼                │
        ┌─────────┐           │
        │ SERIAL  │───────────┘
        └─────────┘

(Cannot change type while connected)
```

## Testing Scenarios

### Unit Test Coverage Areas

1. **SerialConnectionWorker**
   - Port validation
   - Connection success path
   - Connection failure path
   - Disconnect operation
   - Signal emissions

2. **on_connection_type_changed()**
   - Type switching while disconnected ✓
   - Type switching while connected (blocked) ✓
   - UI visibility toggling ✓
   - Logging on switch ✓

3. **connect_ble() / connect_serial()**
   - Input validation ✓
   - Controller initialization ✓
   - Worker creation ✓
   - Signal connection ✓
   - Thread management ✓

4. **disconnect_device()**
   - Worker type selection ✓
   - BLE worker creation ✓
   - Serial worker creation ✓
   - Signal emission ✓

5. **update_connection_status()**
   - Both input fields disabled when connected ✓
   - Connection type combo disabled when connected ✓
   - All controls enabled when disconnected ✓
   - Status label color and text ✓

## Future Extensions

### 1. Connection Profiles
```python
class ConnectionProfile:
    name: str           # "Home BLE", "Office Serial", etc.
    type: str           # "BLE" or "Serial"
    device_name: str    # For BLE
    com_port: str       # For Serial
    auto_connect: bool
    last_used: datetime
```

### 2. Port Auto-Discovery (Serial)
```python
def discover_serial_ports(self):
    """List available COM ports with descriptions"""
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    return [(p.device, p.description) for p in ports]
```

### 3. Intelligent Reconnection
```python
def setup_auto_reconnect(self, max_attempts=5, interval=2):
    """Attempt automatic reconnection on disconnect"""
    # Use QTimer for periodic reconnection
    # Different strategies for BLE vs Serial
    # Backoff on repeated failures
```

### 4. Device Scanning (Serial)
```python
def scan_serial_devices(self):
    """Discover ESP32 devices on serial ports"""
    # Send identification command to each port
    # Collect device info
    # Return list of available devices with names
```

### 5. Baudrate Configuration
```python
# Add UI control for serial baudrate
self.baudrate_combo = QComboBox()
self.baudrate_combo.addItems(["9600", "115200", "230400"])

# Pass to LEDControllerSerial
self.controller = LEDControllerSerial(
    port=com_port,
    baudrate=int(self.baudrate_combo.currentText())
)
```

## Performance Characteristics

### Connection Times (Typical)
- BLE scanning: 2-5 seconds (device dependent)
- BLE connection: 1-2 seconds
- BLE device info load: 1-2 seconds
- **Total BLE**: 4-9 seconds

- Serial port open: <100ms
- Serial device info load: 500-1000ms
- **Total Serial**: 500-1100ms

### UI Response
- Connection type switch: Instant (~0ms)
- Command execution: 200-500ms (BLE), 100-300ms (Serial)
- Status update: <10ms (signal processing)
- Log message display: <20ms (text widget update)

### Memory Usage
- Main GUI window: ~5-10 MB
- Per worker thread: ~2-3 MB
- Per controller instance: ~1-2 MB
- Total (connected): ~15-20 MB

## Debugging Tips

### Enable Verbose Logging
```python
# In led_app.py, modify log_output():
def log_output(self, message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    full_message = f"[{timestamp}] {message}"
    # ... rest of method
```

### Monitor Signal Emissions
```python
# Temporarily connect additional logging slot:
self.conn_worker.log.connect(lambda msg: print(f"SIGNAL: {msg}"))
self.conn_worker.success.connect(lambda: print("SIGNAL: success"))
self.conn_worker.error.connect(lambda e: print(f"SIGNAL: error={e}"))
```

### Track Thread Lifecycle
```python
# Add to connect methods:
thread_id = threading.current_thread().ident
self.log_output(f"Creating worker thread ID: {thread_id}")

# In worker:
self.log.emit(f"Worker running in thread ID: {threading.current_thread().ident}")

# In cleanup:
self.log_output(f"Thread cleanup - thread ID: {thread_id}")
```

### Verify Controller Calls
```python
# Patch controller methods with logging:
original_connect = self.controller.connect
async def logged_connect(*args, **kwargs):
    print("TRACE: connect() called")
    try:
        result = await original_connect(*args, **kwargs)
        print(f"TRACE: connect() returned {result}")
        return result
    except Exception as e:
        print(f"TRACE: connect() raised {e}")
        raise
self.controller.connect = logged_connect
```
