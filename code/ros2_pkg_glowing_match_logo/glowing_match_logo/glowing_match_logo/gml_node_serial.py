#!/usr/bin/env python3
"""
Serial Control Node for Glowing Match Logo
Communicates with ESP32-C6 via serial connection
"""

import rclpy
from typing import Optional, List
from glowing_match_logo.py_modules.GmlBaseNode import GmlBaseNode
from glowing_match_logo.py_modules.serial_controller import LEDControllerSerial


class SerialControlNode(GmlBaseNode):
    """
    ROS2 Node for serial-based control of Glowing Match Logo devices.
    
    This node inherits service handling from GmlBaseNode and uses
    LEDControllerSerial for device communication over a serial port.
    
    Parameters:
        port: Serial port name (e.g., '/dev/ttyUSB0', 'COM3'). If not specified, auto-detects.
        baudrate: Serial communication baudrate (default: 115200)
    """
    
    def __init__(self) -> None:
        # Initialize attributes BEFORE calling super().__init__()
        # This is critical because parent's __init__ calls device_connect()
        self.port: Optional[str] = None
        self.baudrate: int = 115200
        
        # Initialize base node (this will call device_connect())
        super().__init__('glowing_match_logo_node')
        
        # Declare parameters
        self.declare_parameter('port', '')
        self.declare_parameter('baudrate', 115200)
        
        # Get parameter values and update attributes
        port_param = self.get_parameter('port').value
        self.port = port_param if port_param else None
        self.baudrate = self.get_parameter('baudrate').value
    
    def device_connect(self) -> Optional[LEDControllerSerial]:
        """
        Initialize and connect to the device via serial port.
        
        Returns:
            LEDControllerSerial instance if successful, None otherwise
        """
        try:
            self.get_logger().info("Initializing serial connection...")
            
            # Create serial controller
            controller = LEDControllerSerial(port=self.port, baudrate=self.baudrate)
            
            # If a specific port was provided, try to connect to it
            if self.port:
                try:
                    self.get_logger().info(f"Attempting to connect to specified port: {self.port}...")
                    # Actually connect using the async method
                    success = self._run_async(controller.connect(self.port))
                    if success:
                        self.get_logger().info(f"Successfully connected to {self.port}")
                        return controller
                    else:
                        self.get_logger().error(f"Failed to connect to specified port {self.port}")
                        return None
                except Exception as e:
                    self.get_logger().error(f"Error connecting to specified port {self.port}: {e}")
                    return None
            
            # Auto-detect if no port specified
            self.get_logger().info("No port specified, auto-detecting...")
            available_ports = controller.list_available_ports()
            if not available_ports:
                self.get_logger().error("No COM ports available")
                return None
            
            # Filter out generic ports (description = 'n/a') and prioritize USB devices
            active_ports = [p for p in available_ports if p['description'] and p['description'].lower() != 'n/a']
            ports_to_try = active_ports if active_ports else available_ports
            
            self.get_logger().info(f"Trying {len(ports_to_try)} active port(s)...")
            
            # Try to connect to each available port
            for port_info in ports_to_try:
                try:
                    port = port_info['port']
                    description = port_info.get('description', 'Unknown')
                    self.get_logger().info(f"Attempting to connect to {port} ({description})...")
                    
                    # Actually connect using the async method
                    success = self._run_async(controller.connect(port))
                    if success:
                        self.get_logger().info(f"Successfully connected to {port}")
                        return controller
                        
                except Exception as e:
                    self.get_logger().debug(f"Failed to connect to {port}: {e}")
                    continue
            
            self.get_logger().error("Could not connect to any available port")
            return None
            
        except Exception as e:
            self.get_logger().error(f"Error during device connection: {e}")
            return None


def main(args: Optional[List[str]] = None) -> None:
    """Main entry point for serial control node"""
    rclpy.init(args=args)
    node = SerialControlNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
