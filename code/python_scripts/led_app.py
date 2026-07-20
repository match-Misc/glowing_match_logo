#!/usr/bin/env python3
"""
LED Control Application for Glowing Match Display - PyQt6 GUI Version
Uses the LEDControllerBLE class from ble_controller.py

This app provides a graphical user interface for controlling
the LED display wirelessly via BLE.
"""

import asyncio
import sys
import threading
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QPushButton, QLabel, QComboBox, QSlider, QTextEdit,
    QLineEdit, QGridLayout, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor

# Add parent directory to path to import controllers
sys.path.insert(0, str(Path(__file__).parent))

from ble_controller import LEDControllerBLE
from serial_controller import LEDControllerSerial


def get_auto_detected_port() -> str:
    """Get the auto-detected serial port (same logic as serial_controller.py)"""
    try:
        ports = LEDControllerSerial.list_available_ports()
        if len(ports) == 1:
            return ports[0]['port']
    except:
        pass
    return "COM3"  # Fallback default


def get_available_ports_list() -> list:
    """Get list of available serial ports"""
    try:
        return LEDControllerSerial.list_available_ports()
    except:
        return []


def format_serial_error(port: str, error: Exception) -> tuple:
    """Format serial connection error into title and message"""
    error_str = str(error).lower()
    
    # Port not found / File not found
    if "could not open port" in error_str or "filenotfounderror" in error_str or "no such file" in error_str:
        available = get_available_ports_list()
        if available:
            port_list = ", ".join([p['port'] for p in available])
            return (
                "COM Port Not Available",
                f"The port '{port}' could not be opened.\n\n"
                f"Available ports: {port_list}\n\n"
                f"Please check that:\n"
                f"• The device is connected via USB\n"
                f"• No other application is using the port\n"
                f"• The correct port is selected"
            )
        else:
            return (
                "COM Port Not Available",
                f"The port '{port}' could not be opened.\n\n"
                f"No COM ports found on this system.\n\n"
                f"Please check that:\n"
                f"• The ESP32 device is connected via USB\n"
                f"• The USB driver is installed\n"
                f"• Try a different USB port on your computer"
            )
    
    # Port in use
    if "access denied" in error_str or "already in use" in error_str or "resource busy" in error_str:
        return (
            "COM Port In Use",
            f"The port '{port}' is already in use.\n\n"
            f"Please check that:\n"
            f"• No other application is using this port\n"
            f"• The previous connection was properly closed\n"
            f"• Try reconnecting the USB cable"
        )
    
    # Device not responding
    if "timeout" in error_str:
        return (
            "Device Not Responding",
            f"Connected to {port} but device is not responding.\n\n"
            f"Please check that:\n"
            f"• The ESP32 device is powered on\n"
            f"• The USB cable is properly connected\n"
            f"• The device firmware is functioning\n"
            f"• Try resetting the device"
        )
    
    # Generic error
    return (
        "Serial Connection Error",
        f"Failed to connect to {port}.\n\n"
        f"Error: {error_str}\n\n"
        f"Please check your connection and try again."
    )


class AsyncWorker(QObject):
    """Worker for running async operations in background"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def _run_loop(self):
        """Run the async event loop"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def run_async(self, coro):
        """Schedule coroutine and wait for result"""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()


class WorkerSignals(QObject):
    """Signals for worker thread"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    log = pyqtSignal(str)
    status = pyqtSignal(bool)


class ConnectionWorker(QObject):
    """Worker for connection operations"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    success = pyqtSignal()
    log = pyqtSignal(str)
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.worker = AsyncWorker()
    
    def connect_device(self):
        """Connect to BLE device"""
        try:
            self.log.emit("Scanning for devices...")
            devices, target_device = self.worker.run_async(self.controller.scan_devices())
            
            if not target_device:
                self.error.emit(f"Target device '{self.controller.device_name}' not found!\nMake sure the device name is correct and the device is powered on.")
                self.finished.emit()
                return
            
            self.log.emit(f"Connecting to {target_device.name}...")
            
            if self.worker.run_async(self.controller.connect(target_device)):
                self.log.emit("✓ Connected successfully!")
                self.success.emit()
            else:
                self.error.emit("Failed to connect to device")
        except Exception as e:
            self.error.emit(f"Connection error: {e}")
            self.log.emit(f"Error: {e}")
        finally:
            self.finished.emit()
    
    def disconnect_device(self):
        """Disconnect from device"""
        try:
            self.worker.run_async(self.controller.disconnect())
            self.log.emit("✓ Disconnected")
            self.success.emit()
        except Exception as e:
            self.error.emit(f"Disconnect error: {e}")
        finally:
            self.finished.emit()


class CommandWorker(QObject):
    """Worker for sending commands"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log = pyqtSignal(str)
    connection_lost = pyqtSignal()  # Signal when connection is lost
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.worker = AsyncWorker()
    
    def send_command(self, cmd):
        """Send command to device"""
        try:
            result = self.worker.run_async(self.controller.send_command(cmd))
            if result:
                self.log.emit(f"✓ Sent: {cmd}")
            else:
                # Command failed - check if it's a connection issue
                if not self.worker.run_async(self.controller.is_connected()):
                    self.connection_lost.emit()
                    self.error.emit("Connection lost and failed to reconnect")
        except Exception as e:
            self.error.emit(f"Failed: {e}")
            self.connection_lost.emit()
        finally:
            self.finished.emit()


class SerialConnectionWorker(QObject):
    """Worker for serial device connections"""
    finished = pyqtSignal()
    error = pyqtSignal(str)  # Format: "Title|Message"
    success = pyqtSignal()
    log = pyqtSignal(str)
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller  # LEDControllerSerial instance
        self.worker = AsyncWorker()
    
    def connect_device(self):
        """Connect to device via serial port"""
        try:
            port = self.controller.port
            if not port:
                self.error.emit("COM Port Not Specified|Please enter a COM port number")
                return
            
            # Validate port format
            if not self._validate_port_format(port):
                self.error.emit(f"Invalid Port Format|'{port}' is not a valid COM port format.\n\nExamples: COM3, COM4, /dev/ttyUSB0")
                return
            
            self.log.emit(f"Connecting to {port}...")
            
            # Try to connect - this will raise exceptions if port unavailable
            try:
                result = self.worker.run_async(self.controller.connect())
                if result:  # Connection successful
                    self.log.emit(f"✓ Connected to {port}")
                    self.success.emit()
                else:  # Connection returned False
                    self.error.emit(f"Connection Failed|Failed to connect to {port}")
                    self.log.emit(f"Connection failed: connect() returned False")
            except FileNotFoundError as e:
                # Port doesn't exist
                title, message = format_serial_error(port, e)
                self.error.emit(f"{title}|{message}")
                self.log.emit(f"Connection failed: Port not found")
            except PermissionError as e:
                # Port in use or permission denied
                title, message = format_serial_error(port, e)
                self.error.emit(f"{title}|{message}")
                self.log.emit(f"Connection failed: Permission denied")
            except Exception as e:
                # Other serial errors (including SerialException)
                title, message = format_serial_error(port, e)
                self.error.emit(f"{title}|{message}")
                self.log.emit(f"Connection failed: {str(e)}")
        except Exception as e:
            self.error.emit(f"Unexpected Error|An unexpected error occurred: {str(e)}")
            self.log.emit(f"Unexpected error: {e}")
    
    @staticmethod
    def _validate_port_format(port: str) -> bool:
        """Validate port format (basic check)"""
        import re
        port = port.strip().upper()
        # Allow COM1-COM256 and /dev/ttyUSB*, /dev/ttyACM*
        return bool(re.match(r'^(COM\d+|/dev/tty(USB|ACM)\d+)$', port, re.IGNORECASE))
    
    def disconnect_device(self):
        """Disconnect from device"""
        try:
            self.worker.run_async(self.controller.disconnect())
            self.log.emit("✓ Disconnected")
            self.success.emit()
        except Exception as e:
            self.error.emit(f"Disconnect error: {e}")
        finally:
            self.finished.emit()


class LEDControllerGUI(QMainWindow):
    """PyQt6 GUI for LED Controller"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glowing Match LED Controller")
        self.setGeometry(100, 100, 1000, 800)
        
        self.device_name = "GlowingMatch"
        self.connection_type = "BLE"  # "BLE" or "Serial"
        self.controller = None
        self.connected = False
        self.conn_thread = None
        self.conn_worker = None
        
        # Create UI
        self.create_ui()
        self.update_connection_status(False)
    
    def create_ui(self):
        """Create GUI widgets"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # --- CONNECTION SECTION ---
        conn_group = QGroupBox("Connection")
        conn_layout = QHBoxLayout()
        
        conn_layout.addWidget(QLabel("Connection Type:"))
        self.connection_type_combo = QComboBox()
        self.connection_type_combo.addItems(["BLE", "Serial"])
        self.connection_type_combo.currentTextChanged.connect(self.on_connection_type_changed)
        conn_layout.addWidget(self.connection_type_combo)
        
        # Device name input (for BLE)
        conn_layout.addWidget(QLabel("Device Name:"))
        self.device_name_input = QLineEdit()
        self.device_name_input.setText("GlowingMatch")
        self.device_name_input.setMaximumWidth(200)
        conn_layout.addWidget(self.device_name_input)
        
        # COM port input (for Serial)
        self.com_port_label = QLabel("COM Port:")
        self.com_port_label.setVisible(False)
        conn_layout.addWidget(self.com_port_label)
        self.com_port_input = QLineEdit()
        self.com_port_input.setText(get_auto_detected_port())  # Auto-detect port
        self.com_port_input.setMaximumWidth(100)
        self.com_port_input.setVisible(False)
        conn_layout.addWidget(self.com_port_input)
        
        self.status_label = QLabel("Status: Not Connected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        conn_layout.addWidget(self.status_label)
        
        conn_layout.addStretch()
        
        self.connect_btn = QPushButton("Connect to Device")
        self.connect_btn.clicked.connect(self.connect_device)
        conn_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_device)
        self.disconnect_btn.setEnabled(False)
        conn_layout.addWidget(self.disconnect_btn)
        
        conn_group.setLayout(conn_layout)
        main_layout.addWidget(conn_group)
        
        # --- DEVICE INFO SECTION ---
        info_group = QGroupBox("Device Information")
        info_layout = QVBoxLayout()
        
        self.device_info_text = QTextEdit()
        self.device_info_text.setReadOnly(True)
        # Allow text edit to expand/shrink with window
        info_layout.addWidget(self.device_info_text, 1)  # 1 = stretch factor
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group, 1)  # 1 = stretch factor for group box
        
        # --- WORD MODE EFFECT SECTION ---
        word_group = QGroupBox("Word Mode Effect")
        word_layout = QHBoxLayout()
        
        word_layout.addWidget(QLabel("Select Effect:"))
        
        self.word_effect_combo = QComboBox()
        self.word_effect_combo.setMinimumWidth(300)
        self.word_effect_combo.setEnabled(False)
        word_layout.addWidget(self.word_effect_combo)
        
        word_apply_btn = QPushButton("Apply")
        word_apply_btn.clicked.connect(self.apply_word_effect)
        word_layout.addWidget(word_apply_btn)
        
        word_layout.addStretch()
        
        word_group.setLayout(word_layout)
        main_layout.addWidget(word_group)
        
        # --- BRIGHTNESS & POWER SECTION ---
        brightness_group = QGroupBox("Brightness & Power")
        brightness_layout = QVBoxLayout()
        
        # Power buttons (ON/OFF)
        power_layout = QHBoxLayout()
        power_layout.addWidget(QLabel("Power:"))
        
        self.power_on_btn = QPushButton("ON")
        self.power_on_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.power_on_btn.setMaximumWidth(80)
        self.power_on_btn.setEnabled(False)
        self.power_on_btn.clicked.connect(self.turn_on_led)
        power_layout.addWidget(self.power_on_btn)
        
        self.power_off_btn = QPushButton("OFF")
        self.power_off_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.power_off_btn.setMaximumWidth(80)
        self.power_off_btn.setEnabled(False)
        self.power_off_btn.clicked.connect(self.turn_off_led)
        power_layout.addWidget(self.power_off_btn)
        
        power_layout.addStretch()
        brightness_layout.addLayout(power_layout)
        
        # Brightness slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Level:"))
        
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setEnabled(False)
        self.brightness_slider.valueChanged.connect(self.update_brightness)
        slider_layout.addWidget(self.brightness_slider)
        
        self.brightness_label = QLabel("100%")
        self.brightness_label.setMinimumWidth(50)
        slider_layout.addWidget(self.brightness_label)
        
        brightness_layout.addLayout(slider_layout)
        
        brightness_group.setLayout(brightness_layout)
        main_layout.addWidget(brightness_group)
        
        # --- LETTER EFFECTS SECTION ---
        letters_group = QGroupBox("Individual Letter Effects")
        letters_layout = QGridLayout()
        
        self.letter_vars = {}
        self.letter_combos = {}
        letters = ['M', 'A', 'T', 'C', 'H']
        
        for i, letter in enumerate(letters):
            letters_layout.addWidget(QLabel(f"{letter}:"), 0, i*2)
            
            combo = QComboBox()
            combo.setMinimumWidth(80)
            combo.setEnabled(False)
            combo.addItem("0 - Off")
            letters_layout.addWidget(combo, 0, i*2+1)
            letters_layout.setColumnStretch(i*2+1, 1)  # Make columns expand
            
            self.letter_combos[letter.lower()] = combo
        
        apply_all_btn = QPushButton("Apply All Letters")
        apply_all_btn.clicked.connect(self.apply_letter_effects)
        letters_layout.addWidget(apply_all_btn, 1, 0, 1, 10)
        
        letters_group.setLayout(letters_layout)
        main_layout.addWidget(letters_group)
        
        # --- DIRECT COMMAND SECTION ---
        cmd_group = QGroupBox("Direct Command")
        cmd_layout = QVBoxLayout()
        
        # Command input
        cmd_input_layout = QHBoxLayout()
        cmd_input_layout.addWidget(QLabel("Command:"))
        
        self.command_input = QLineEdit()
        self.command_input.setEnabled(False)
        self.command_input.returnPressed.connect(self.send_command)
        cmd_input_layout.addWidget(self.command_input)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_command)
        cmd_input_layout.addWidget(send_btn)
        
        cmd_layout.addLayout(cmd_input_layout)
        
        # Output text
        cmd_layout.addWidget(QLabel("Output:"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(150)
        cmd_layout.addWidget(self.output_text)
        
        cmd_group.setLayout(cmd_layout)
        main_layout.addWidget(cmd_group)
    
    def connect_device(self):
        """Connect to BLE device"""
        self.connect_btn.setEnabled(False)
        
        # Determine connection type
        self.connection_type = self.connection_type_combo.currentText()
        
        if self.connection_type == "BLE":
            self.connect_ble()
        else:
            self.connect_serial()
    
    def connect_ble(self):
        """Connect via BLE"""
        # Update device name from input
        device_name = self.device_name_input.text().strip()
        if not device_name:
            self.show_warning("Invalid Input", "Please enter a device name")
            self.connect_btn.setEnabled(True)
            return
        
        self.device_name = device_name
        self.controller = LEDControllerBLE(self.device_name)
        
        # Clean up previous thread if exists
        if self.conn_thread is not None:
            self.conn_thread.quit()
            self.conn_thread.wait()
        
        # Create worker in separate thread
        self.conn_worker = ConnectionWorker(self.controller)
        self.conn_thread = QThread()
        
        self.conn_worker.moveToThread(self.conn_thread)
        self.conn_thread.started.connect(self.conn_worker.connect_device)
        
        # Connect signals
        self.conn_worker.log.connect(self.log_output)
        self.conn_worker.error.connect(self.on_connection_error)
        self.conn_worker.success.connect(self.on_connect_success)
        self.conn_worker.finished.connect(self.on_connection_finished)
        
        self.conn_thread.start()
    
    def connect_serial(self):
        """Connect via Serial"""
        # Get COM port from input
        com_port = self.com_port_input.text().strip()
        if not com_port:
            self.show_warning("Invalid Input", "Please enter a COM port")
            self.connect_btn.setEnabled(True)
            return
        
        self.controller = LEDControllerSerial(port=com_port)
        
        # Clean up previous thread if exists
        if self.conn_thread is not None:
            self.conn_thread.quit()
            self.conn_thread.wait()
        
        # Create worker in separate thread
        self.conn_worker = SerialConnectionWorker(self.controller)
        self.conn_thread = QThread()
        
        self.conn_worker.moveToThread(self.conn_thread)
        self.conn_thread.started.connect(self.conn_worker.connect_device)
        
        # Connect signals
        self.conn_worker.log.connect(self.log_output)
        self.conn_worker.error.connect(self.on_connection_error)
        self.conn_worker.success.connect(self.on_connect_success)
        self.conn_worker.finished.connect(self.on_connection_finished)
        
        self.conn_thread.start()
    
    def on_connection_error(self, error_msg):
        """Handle connection error - parse Title|Message format"""
        # Reset connection state on error
        self.connected = False
        self.update_connection_status(False)
        
        if "|" in error_msg:
            title, message = error_msg.split("|", 1)
        else:
            title = "Connection Error"
            message = error_msg
        self.show_error(title, message)
        self.connect_btn.setEnabled(True)
    
    def on_connection_finished(self):
        """Handle connection worker finished"""
        try:
            if self.conn_worker:
                self.conn_worker.deleteLater()
        except RuntimeError:
            # Worker already deleted
            pass
        
        try:
            if self.conn_thread:
                self.conn_thread.quit()
                self.conn_thread.wait()
        except RuntimeError:
            # Thread already cleaned up
            pass
        
        # Re-enable connect button if connection failed
        if not self.connected:
            self.connect_btn.setEnabled(True)
    
    def on_connect_success(self):
        """Handle successful connection"""
        self.connected = True
        self.update_connection_status(True)
        self.update_device_info()
        self.update_effects_list()
        # Set brightness slider to device's current brightness
        self.brightness_slider.setValue(self.controller.brightness)
        self.show_info("Success", "Connected to device!")
        self.connect_btn.setEnabled(True)
    
    def disconnect_device(self):
        """Disconnect from device"""
        self.disconnect_btn.setEnabled(False)
        
        # Clean up previous thread if exists
        if self.conn_thread is not None:
            self.conn_thread.quit()
            self.conn_thread.wait()
        
        # Create appropriate worker based on connection type
        if self.connection_type == "BLE":
            self.conn_worker = ConnectionWorker(self.controller)
        else:  # Serial
            self.conn_worker = SerialConnectionWorker(self.controller)
        
        self.conn_thread = QThread()
        
        self.conn_worker.moveToThread(self.conn_thread)
        self.conn_thread.started.connect(self.conn_worker.disconnect_device)
        
        # Connect signals
        self.conn_worker.log.connect(self.log_output)
        self.conn_worker.error.connect(self.on_disconnect_error)
        self.conn_worker.success.connect(self.on_disconnect_success)
        self.conn_worker.finished.connect(self.on_connection_finished)
        
        self.conn_thread.start()
    
    def on_disconnect_error(self, error_msg):
        """Handle disconnect error"""
        self.show_error("Disconnect Error", error_msg)
    
    def on_disconnect_success(self):
        """Handle successful disconnection"""
        self.connected = False
        self.update_connection_status(False)
        self.show_info("Success", "Disconnected")
        self.disconnect_btn.setEnabled(True)
    
    def update_connection_status(self, connected):
        """Update connection status display"""
        if connected:
            self.status_label.setText("Status: Connected ✓")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.device_name_input.setEnabled(False)
            self.com_port_input.setEnabled(False)
            self.connection_type_combo.setEnabled(False)
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.power_on_btn.setEnabled(True)
            self.power_off_btn.setEnabled(True)
            self.word_effect_combo.setEnabled(True)
            self.brightness_slider.setEnabled(True)
            for combo in self.letter_combos.values():
                combo.setEnabled(True)
            self.command_input.setEnabled(True)
        else:
            self.status_label.setText("Status: Not Connected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.device_name_input.setEnabled(True)
            self.com_port_input.setEnabled(True)
            self.connection_type_combo.setEnabled(True)
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.power_on_btn.setEnabled(False)
            self.power_off_btn.setEnabled(False)
            self.word_effect_combo.setEnabled(False)
            self.brightness_slider.setEnabled(False)
            for combo in self.letter_combos.values():
                combo.setEnabled(False)
            self.command_input.setEnabled(False)
    
    def update_device_info(self):
        """Update device info display"""
        text = "DEVICE INFORMATION\n"
        text += "=" * 70 + "\n\n"
        
        if self.controller.word_mode:
            text += f"Word Mode: {self.controller.word_mode}\n\n"
        
        if self.controller.effects_list:
            text += f"Available Effects ({len(self.controller.effects_list)}):\n"
            for effect_num in sorted(self.controller.effects_list.keys()):
                text += f"  {effect_num:2d} - {self.controller.effects_list[effect_num]}\n"
        
        self.device_info_text.setText(text)
    
    def update_effects_list(self):
        """Populate effects combobox"""
        effects = sorted(self.controller.effects_list.keys())
        effect_options = [f"{num} - {self.controller.effects_list[num]}" for num in effects]
        
        # Update word effect combo
        self.word_effect_combo.clear()
        self.word_effect_combo.addItems(effect_options)
        
        # Update letter effect combos
        for combo in self.letter_combos.values():
            combo.clear()
            combo.addItems(effect_options)
    
    def apply_word_effect(self):
        """Apply selected word effect"""
        if not self.connected:
            self.show_warning("Not Connected", "Please connect to device first")
            return
        
        effect_str = self.word_effect_combo.currentText()
        if not effect_str:
            return
        
        effect_num = effect_str.split(' - ')[0]
        self.send_command_async(f"word.{effect_num}")
    
    def apply_letter_effects(self):
        """Apply individual letter effects"""
        if not self.connected:
            self.show_warning("Not Connected", "Please connect to device first")
            return
        
        commands = []
        for letter in ['m', 'a', 't', 'c', 'h']:
            effect_str = self.letter_combos[letter].currentText()
            if effect_str:
                effect_num = effect_str.split(' - ')[0]
                commands.append(f"{letter}.{effect_num}")
        
        if commands:
            self.send_command_async(" ".join(commands))
    
    def update_brightness(self, value):
        """Update brightness display"""
        self.brightness_label.setText(f"{value}%")
        
        if self.connected:
            self.send_command_async(f"brightness.{value}", silent=True)
    
    def turn_on_led(self):
        """Turn LED display on"""
        if not self.connected:
            self.show_warning("Not Connected", "Please connect to device first")
            return
        
        self.send_command_async("on")
        self.log_output("→ Sent: on")
    
    def turn_off_led(self):
        """Turn LED display off"""
        if not self.connected:
            self.show_warning("Not Connected", "Please connect to device first")
            return
        
        self.send_command_async("off")
        self.log_output("→ Sent: off")
    
    def send_command(self):
        """Send custom command"""
        if not self.connected:
            self.show_warning("Not Connected", "Please connect to device first")
            return
        
        cmd = self.command_input.text().strip()
        if not cmd:
            return
        
        self.send_command_async(cmd)
        self.command_input.clear()
    
    def send_command_async(self, cmd, silent=False):
        """Send command asynchronously"""
        # Create worker in separate thread
        worker = CommandWorker(self.controller)
        thread = QThread()
        
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.send_command(cmd))
        
        # Connect signals
        if not silent:
            worker.log.connect(self.log_output)
        worker.error.connect(lambda msg: self.log_output(f"❌ {msg}"))
        worker.connection_lost.connect(self.on_device_disconnected)
        
        # Cleanup when done
        def cleanup():
            try:
                worker.deleteLater()
            except RuntimeError:
                pass
            try:
                thread.quit()
                thread.wait()
            except RuntimeError:
                pass
        
        worker.finished.connect(cleanup)
        
        thread.start()
    
    def on_device_disconnected(self):
        """Handle unexpected device disconnection"""
        self.connected = False
        self.update_connection_status(False)
        self.log_output("⚠ Device disconnected! (Reconnection failed)")
        self.show_warning("Connection Lost", "Device disconnected and reconnection failed.\nPlease check your device and try connecting again.")
    
    def on_connection_type_changed(self, connection_type):
        """Handle connection type change (BLE vs Serial)"""
        if self.connected:
            self.show_warning("Connection Active", "Please disconnect before switching connection type.")
            # Reset the combo to previous selection
            self.connection_type_combo.blockSignals(True)
            self.connection_type_combo.setCurrentText(self.connection_type)
            self.connection_type_combo.blockSignals(False)
            return
        
        # Update connection type
        self.connection_type = connection_type
        
        # Toggle input field visibility
        if connection_type == "BLE":
            self.device_name_input.setVisible(True)
            self.com_port_label.setVisible(False)
            self.com_port_input.setVisible(False)
            self.log_output("Switched to BLE connection mode")
        else:  # Serial
            self.device_name_input.setVisible(False)
            self.com_port_label.setVisible(True)
            self.com_port_input.setVisible(True)
            self.log_output("Switched to Serial connection mode")
    
    def log_output(self, message):
        """Log message to output (thread-safe)"""
        current = self.output_text.toPlainText()
        if current:
            self.output_text.setText(current + "\n" + message)
        else:
            self.output_text.setText(message)
        
        # Scroll to bottom
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)
    
    def show_info(self, title, message):
        """Show info message box"""
        QMessageBox.information(self, title, message)
    
    def show_warning(self, title, message):
        """Show warning message box"""
        QMessageBox.warning(self, title, message)
    
    def show_error(self, title, message):
        """Show error message box"""
        try:
            QMessageBox.critical(self, title, message)
        except Exception as e:
            print(f"Error showing message box: {e}")
            print(f"{title}: {message}")
    
    def closeEvent(self, event):
        """Clean up threads on window close"""
        # Wait for connection thread to finish
        if self.conn_thread is not None and self.conn_thread.isRunning():
            self.conn_thread.quit()
            self.conn_thread.wait(3000)  # Wait up to 3 seconds
        
        # Disconnect from device
        try:
            async_worker = AsyncWorker()
            async_worker.run_async(self.controller.disconnect())
        except:
            pass
        
        event.accept()


def main():
    """Main entry point"""
    try:
        import bleak
    except ImportError:
        print("ERROR: bleak not installed")
        print("Install with: pip install bleak")
        sys.exit(1)
    
    try:
        import PyQt6
    except ImportError:
        print("ERROR: PyQt6 not installed")
        print("Install with: pip install PyQt6")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    window = LEDControllerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
