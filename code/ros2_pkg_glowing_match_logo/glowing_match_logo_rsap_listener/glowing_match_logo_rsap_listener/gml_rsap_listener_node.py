#!/usr/bin/env python3
"""
RSAP Listener Node for Glowing Match Logo
Listens to RSAP tick events and controls word mode based on start/stop signals
"""

import rclpy
from rclpy.node import Node
from rsap_interfaces.msg import RsapTick
from glowing_match_logo_interfaces.srv import SetWord


class GmlRsapListenerNode(Node):
    """
    ROS2 Node that listens to RSAP tick events and controls the Glowing Match Logo
    word mode based on start/stop signals and success flags.
    """
    
    def __init__(self):
        super().__init__('gml_rsap_listener_node')
        
        # Configuration for word modes
        self.start_mode = 13           # Word mode when START signal received
        self.stop_success_mode = 9    # Word mode when STOP with success=true
        self.stop_failure_mode = 5    # Word mode when STOP with success=false
        
        # Target device node name (can be specified as parameter)
        self.declare_parameter('target_node', 'glowing_match_logo_node')
        self.target_node = self.get_parameter('target_node').value
        
        # Create subscriber to RSAP tick topic
        self.subscription = self.create_subscription(
            RsapTick,
            '/RSAP_App/rsap_tick',
            self._rsap_tick_callback,
            10
        )
        
        # Create client for set_word_mode service
        self.set_word_client = self.create_client(
            SetWord,
            f'/{self.target_node}/set_word_mode'
        )
        
        self.get_logger().info(f"RSAP Listener Node initialized")
        self.get_logger().info(f"TARGET: {self.target_node}")
        self.get_logger().info(f"START mode: {self.start_mode}")
        self.get_logger().info(f"STOP SUCCESS mode: {self.stop_success_mode}")
        self.get_logger().info(f"STOP FAILURE mode: {self.stop_failure_mode}")
    
    def _rsap_tick_callback(self, msg: RsapTick) -> None:
        """
        Callback for RSAP tick messages.
        
        Args:
            msg: RsapTick message containing:
                - is_start_not_stop_sig: True for start, False for stop
                - success: True if action succeeded, False otherwise
                - action_name: Name of the action
                - description: Action description
        """
        try:
            self.get_logger().info(
                f"RSAP Tick: {'START' if msg.is_start_not_stop_sig else 'STOP'} | "
                f"Action: {msg.action_name} | Success: {msg.success}"
            )
            
            # Determine word mode based on signal
            if msg.is_start_not_stop_sig:
                # START signal - use start mode
                word_mode = self.start_mode
                signal_type = "START"
            else:
                # STOP signal - check success flag
                if msg.success:
                    word_mode = self.stop_success_mode
                    signal_type = "STOP (success)"
                else:
                    word_mode = self.stop_failure_mode
                    signal_type = "STOP (failure)"
            
            # Send word mode change request
            self._set_word_mode(word_mode, signal_type, msg.action_name)
            
        except Exception as e:
            self.get_logger().error(f"Error processing RSAP tick: {e}")
    
    def _set_word_mode(self, mode: int, signal_type: str, action_name: str) -> None:
        """
        Send a request to set the word mode.
        
        Args:
            mode: Word mode to set (0-13 typically)
            signal_type: Description of signal type (for logging)
            action_name: Name of the action triggering this change
        """
        if not self.set_word_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error(f"SetWord service not available for {self.target_node}")
            return
        
        request = SetWord.Request()
        request.word_mode = mode
        
        future = self.set_word_client.call_async(request)
        future.add_done_callback(
            lambda f: self._word_mode_response_callback(f, signal_type, mode, action_name)
        )
    
    def _word_mode_response_callback(self, future, signal_type: str, mode: int, action_name: str) -> None:
        """Handle response from SetWord service."""
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(
                    f"✓ [{signal_type}] Set word mode to {mode} (Action: {action_name})"
                )
            else:
                self.get_logger().warn(
                    f"✗ [{signal_type}] Failed to set word mode to {mode}: {response.message}"
                )
        except Exception as e:
            self.get_logger().error(
                f"✗ [{signal_type}] Error setting word mode to {mode}: {e}"
            )


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    node = GmlRsapListenerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
