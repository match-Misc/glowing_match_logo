import rclpy
from rclpy.node import Node
from abc import ABC, abstractmethod
import asyncio
import inspect
import threading
from typing import Optional, Any, Callable, Coroutine

from glowing_match_logo_interfaces.srv import (
    ChangeBrightness,
    SetLetter,
    SetState,
    SetWord,
    EmpthyWithSuccess
)


class GmlBaseNode(Node, ABC):
    """
    Base class for Glowing Match Logo control nodes.
    
    This class handles all ROS2 service implementations and device communication.
    Child classes must implement the abstract device_connect() method to specify
    how to initialize their particular device controller (Serial or BLE).
    """

    def __init__(self, node_name: str):
        super().__init__(node_name)
        self.device_controller = None
        self.device_connected = False
        
        # Create event loop for async operations
        self.loop = None
        self.loop_thread = None
        self._start_async_loop()
        
        # Initialize service servers
        self._init_services()
        
        # Connect to device
        self._setup_device()
    
    def _start_async_loop(self) -> None:
        """Start an event loop in a separate thread for async operations"""
        self.loop = asyncio.new_event_loop()
        
        def run_loop() -> None:
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()
    
    def _run_async(self, coro: Coroutine[Any, Any, Any]) -> Optional[Any]:
        """Run an async coroutine in the event loop and wait for result"""
        if not self.loop or not self.loop.is_running():
            self.get_logger().warning("Event loop not running, attempting synchronous fallback")
            return None
        
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        try:
            return future.result(timeout=5.0)  # Wait up to 5 seconds
        except TimeoutError:
            self.get_logger().error("Command timed out")
            return None
        except Exception as e:
            self.get_logger().error(f"Error executing async command: {e}")
            return None
    
    def _init_services(self) -> None:
        """Initialize all ROS2 service servers"""
        self.create_service(
            ChangeBrightness,
            f'/{self.get_name()}/change_brightness',
            self._handle_change_brightness
        )
        
        self.create_service(
            SetLetter,
            f'/{self.get_name()}/set_letter_mode',
            self._handle_set_letter
        )
        
        self.create_service(
            SetState,
            f'/{self.get_name()}/set_activation',
            self._handle_set_state
        )
        
        self.create_service(
            SetWord,
            f'/{self.get_name()}/set_word_mode',
            self._handle_set_word
        )
        
        self.create_service(
            EmpthyWithSuccess,
            f'/{self.get_name()}/toggle_activation',
            self._handle_toggle_state
        )
        
        self.create_service(
            EmpthyWithSuccess,
            f'/{self.get_name()}/get_device_info',
            self._handle_get_device_info
        )
        
        self.get_logger().info("All services registered")
    
    def _setup_device(self) -> None:
        """Setup and connect to device"""
        try:
            self.device_controller = self.device_connect()
            if self.device_controller:
                self.device_connected = True
                self.get_logger().info("Device connected successfully")
            else:
                self.get_logger().error("Failed to connect to device")
        except Exception as e:
            self.get_logger().error(f"Error during device setup: {e}")
    
    @abstractmethod
    def device_connect(self) -> Optional[Any]:
        """
        Abstract method that must be implemented by child classes.
        Should initialize and return the device controller (Serial or BLE).
        
        Returns:
            Device controller instance or None if connection failed
        """
        pass
    
    def _execute_command(self, command: str) -> bool:
        """
        Execute a command on the device controller.
        Handles both sync and async methods.
        
        Args:
            command: The command string to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.device_connected or not self.device_controller:
            return False
        
        try:
            # Check if send_command is async or sync
            if inspect.iscoroutinefunction(self.device_controller.send_command):
                # Async method - run it in the event loop
                return self._run_async(self.device_controller.send_command(command))
            else:
                # Sync method - call directly
                return self.device_controller.send_command(command)
        except Exception as e:
            self.get_logger().error(f"Error executing command '{command}': {e}")
            return False
    
    # Service callback handlers
    
    def _handle_change_brightness(self, request: ChangeBrightness.Request, response: ChangeBrightness.Response) -> ChangeBrightness.Response:
        """Handle ChangeBrightness service request"""
        try:
            if not self.device_connected or not self.device_controller:
                response.success = False
                response.message = "Device not connected"
                return response
            
            brightness = int(request.brightness_pct)
            brightness = max(0, min(100, brightness))  # Clamp to 0-100
            command = f"brightness.{brightness}"
            
            result = self._execute_command(command)
            response.success = result
            response.message = f"Brightness set to {brightness}%" if result else "Failed to set brightness"
            
            self.get_logger().info(f"Brightness set to {brightness}%: {response.success}")
            
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"ChangeBrightness error: {e}")
        
        return response
    
    def _handle_set_letter(self, request: SetLetter.Request, response: SetLetter.Response) -> SetLetter.Response:
        """Handle SetLetter service request"""
        try:
            if not self.device_connected or not self.device_controller:
                response.success = False
                response.message = "Device not connected"
                return response
            
            letter = request.letter.upper()
            letter_mode = request.letter_mode
            command = f"{letter.lower()}.{letter_mode}"
            
            result = self._execute_command(command)
            response.success = result
            response.message = f"Letter set to {letter} (mode {letter_mode})" if result else "Failed to set letter"
            
            self.get_logger().info(f"Letter set to {letter}: {response.success}")
            
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"SetLetter error: {e}")
        
        return response
    
    def _handle_set_state(self, request: SetState.Request, response: SetState.Response) -> SetState.Response:
        """Handle SetState service request"""
        try:
            if not self.device_connected or not self.device_controller:
                response.success = False
                response.message = "Device not connected"
                return response
            
            state = "on" if request.state else "off"
            command = state
            
            result = self._execute_command(command)
            response.success = result
            response.message = f"State set to {state}" if result else "Failed to set state"
            
            self.get_logger().info(f"State set to {state}: {response.success}")
            
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"SetState error: {e}")
        
        return response
    
    def _handle_set_word(self, request: SetWord.Request, response: SetWord.Response) -> SetWord.Response:
        """Handle SetWord service request"""
        try:
            if not self.device_connected or not self.device_controller:
                response.success = False
                response.message = "Device not connected"
                return response
            
            word_mode = request.word_mode
            command = f"word.{word_mode}"
            
            result = self._execute_command(command)
            response.success = result
            response.message = f"Word mode set to {word_mode}" if result else "Failed to set word mode"
            
            self.get_logger().info(f"Word mode set to {word_mode}: {response.success}")
            
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"SetWord error: {e}")
        
        return response
    
    def _handle_toggle_state(self, request: EmpthyWithSuccess.Request, response: EmpthyWithSuccess.Response) -> EmpthyWithSuccess.Response:
        """Handle EmpthyWithSuccess service request"""
        try:
            if not self.device_connected or not self.device_controller:
                response.success = False
                response.message = "Device not connected"
                return response
            
            command = "toggle"
            
            result = self._execute_command(command)
            response.success = result
            response.message = "State toggled" if result else "Failed to toggle state"
            
            self.get_logger().info(f"Toggle state: {response.success}")
            
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"EmpthyWithSuccess error: {e}")
        
        return response
    
    def _handle_get_device_info(self, request: EmpthyWithSuccess.Request, response: EmpthyWithSuccess.Response) -> EmpthyWithSuccess.Response:
        """Handle GetDeviceInfo service request - returns all device information"""
        try:
            if not self.device_connected or not self.device_controller:
                response.success = False
                response.message = "Device not connected"
                return response
            
            # Try to load device info first
            if hasattr(self.device_controller, 'load_device_info'):
                self._run_async(self.device_controller.load_device_info())
            
            # Gather device information
            info_lines = []
            info_lines.append("=== DEVICE INFORMATION ===")
            
            # Word mode
            if hasattr(self.device_controller, 'word_mode'):
                word_mode = self.device_controller.word_mode or "Not loaded"
                info_lines.append(f"Word Mode: {word_mode}")
            
            # Brightness
            if hasattr(self.device_controller, 'brightness'):
                brightness = self.device_controller.brightness
                info_lines.append(f"Brightness: {brightness}%")
            
            # Effects list
            if hasattr(self.device_controller, 'effects_list'):
                effects = self.device_controller.effects_list
                if effects:
                    info_lines.append(f"Available Effects ({len(effects)}):")
                    for effect_num in sorted(effects.keys()):
                        info_lines.append(f"  {effect_num}: {effects[effect_num]}")
                else:
                    info_lines.append("Available Effects: None loaded")
            
            # Device connection info
            if hasattr(self.device_controller, 'port'):
                info_lines.append(f"Connected Port: {self.device_controller.port}")
            
            if hasattr(self.device_controller, 'baudrate'):
                info_lines.append(f"Baudrate: {self.device_controller.baudrate}")
            
            info_lines.append("========================")
            
            response.success = True
            response.message = "\n".join(info_lines)
            self.get_logger().info(f"Device info retrieved: {response.success}")
            
        except Exception as e:
            response.success = False
            response.message = f"Error retrieving device info: {str(e)}"
            self.get_logger().error(f"GetDeviceInfo error: {e}")
        
        return response
    
    def destroy_node(self) -> None:
        """Cleanup on node destruction"""
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        super().destroy_node()
