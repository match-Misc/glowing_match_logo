#!/usr/bin/env python3
"""
BLE Control Node for Glowing Match Logo
Communicates with ESP32-C6 via Bluetooth Low Energy (BLE)
"""

import rclpy
import asyncio
from typing import Optional, List
from glowing_match_logo.py_modules.GmlBaseNode import GmlBaseNode
from glowing_match_logo.py_modules.ble_controller import LEDControllerBLE


class BleControlNode(GmlBaseNode):
    """
    ROS2 Node for BLE-based control of Glowing Match Logo devices.
    
    This node inherits service handling from GmlBaseNode and uses
    LEDControllerBLE for device communication via Bluetooth Low Energy.
    
    Parameters:
        device_name: BLE device name to search for (default: 'GlowingMatch')
    """
    
    def __init__(self) -> None:
        # Initialize base node
        super().__init__('glowing_match_logo_node')
        
        # Declare parameters
        self.declare_parameter('device_name', 'GlowingMatch')
        
        # Get parameter values
        self.device_name: str = self.get_parameter('device_name').get_parameter_value().string_value
    
    def device_connect(self) -> Optional[LEDControllerBLE]:
        """
        Initialize and connect to the device via BLE.
        
        Returns:
            LEDControllerBLE instance if successful, None otherwise
        """
        try:
            self.get_logger().info(f"Initializing BLE connection (looking for '{self.device_name}')...")
            
            # Create BLE controller
            controller = LEDControllerBLE(device_name=self.device_name)
            
            # For BLE, we need async operations, so we'll set up async scanning
            # and connecting in a separate thread or use a non-blocking approach
            try:
                # Try to scan and connect asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Scan for devices
                self.get_logger().info("Scanning for BLE devices...")
                devices, target_device = loop.run_until_complete(controller.scan_devices())
                
                if target_device:
                    self.get_logger().info(f"Found target device: {target_device.name}")
                    
                    # Connect to device
                    success = loop.run_until_complete(controller.connect(target_device))
                    
                    if success:
                        self.get_logger().info("Successfully connected to BLE device")
                        return controller
                    else:
                        self.get_logger().error("Failed to connect to BLE device")
                        return None
                else:
                    self.get_logger().error(f"Target device '{self.device_name}' not found in scan")
                    return None
                    
            except Exception as e:
                self.get_logger().error(f"Error during BLE connection: {e}")
                return None
            
        except Exception as e:
            self.get_logger().error(f"Error initializing BLE controller: {e}")
            return None


def main(args: Optional[List[str]] = None) -> None:
    """Main entry point for BLE control node"""
    rclpy.init(args=args)
    node = BleControlNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
