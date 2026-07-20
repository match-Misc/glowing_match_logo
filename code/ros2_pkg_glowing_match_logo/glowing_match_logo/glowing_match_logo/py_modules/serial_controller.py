#!/usr/bin/env python3
"""
Serial Control Script for Glowing Match LED Display (ESP32-C6)
Uses pyserial for serial communication via COM port

Install required packages:
    pip install pyserial
"""

import asyncio
import sys
import serial
from typing import Tuple, Optional
from serial.tools import list_ports

class LEDControllerSerial:
    def __init__(self, port: str = None, baudrate: int = 115200):
        """
        Initialize serial controller
        
        Args:
            port: COM port (e.g., 'COM3', '/dev/ttyUSB0'). If None, will auto-detect.
            baudrate: Serial baudrate (default: 115200)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
        # Device information storage
        self.word_mode = None
        self.effects_list = {}
        self.device_info_loaded = False
        self.brightness = 100  # Default brightness
    
    @staticmethod
    def list_available_ports() -> list:
        """List all available COM ports"""
        ports = []
        for port in list_ports.comports():
            ports.append({
                'port': port.device,
                'description': port.description,
                'manufacturer': port.manufacturer
            })
        return ports
    
    def is_connected(self) -> bool:
        """Check if serial port is connected"""
        return self.serial is not None and self.serial.is_open
    
    async def connect(self, port: str = None) -> bool:
        """Connect to device via serial port"""
        try:
            connect_port = port or self.port
            
            if not connect_port:
                print("ERROR: No COM port specified")
                return False
            
            print(f"\nConnecting to {connect_port}...")
            self.serial = serial.Serial(connect_port, self.baudrate, timeout=0.1)
            self.port = connect_port
            print("✓ Connected successfully!")
            
            # Load device information
            await self.load_device_info()
            
            return True
            
        except serial.SerialException as e:
            print(f"✗ Connection failed: {e}")
            raise  # Re-raise to let caller handle
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            raise  # Re-raise to let caller handle
    
    async def send_command_silent(self, command: str) -> Optional[str]:
        """Send a command and return raw response without printing"""
        if not self.is_connected():
            return None
        
        try:
            # Clear any pending data
            self.serial.reset_input_buffer()
            
            # Send command
            cmd = command.strip() + "\n"
            self.serial.write(cmd.encode())
            self.serial.flush()
            
            # Read response - collect lines until we get an empty line or timeout
            await asyncio.sleep(0.1)
            
            response_lines = []
            empty_line_count = 0
            
            while empty_line_count < 2:  # Stop after 2 consecutive empty lines
                try:
                    # Set a shorter timeout per line
                    self.serial.timeout = 0.1
                    line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    
                    if not line:
                        empty_line_count += 1
                    else:
                        empty_line_count = 0
                        response_lines.append(line)
                    
                    # Safety limit
                    if len(response_lines) > 20:
                        break
                except:
                    break
            
            response = "\n".join(response_lines) if response_lines else None
            return response if response else None
        except Exception as e:
            return None
    
    async def load_device_info(self) -> bool:
        """Load critical device information (word mode, effects, brightness)"""
        if self.device_info_loaded:
            return True
        
        print("\n📋 Loading device information...")
        
        try:
            # Get word mode
            response = await self.send_command_silent("word")
            if response:
                self.word_mode = response
                print(f"  Word Mode: {response}")
            
            # Get effects list
            response = await self.send_command_silent("effects")
            if response:
                # Parse effects from response
                lines = response.split('\n')
                for line in lines:
                    if ' - ' in line:
                        parts = line.strip().split(' - ', 1)
                        if len(parts) == 2 and parts[0].isdigit():
                            effect_num = int(parts[0])
                            effect_name = parts[1]
                            self.effects_list[effect_num] = effect_name
                
                if self.effects_list:
                    print(f"  Effects: Loaded {len(self.effects_list)} effects")
            
            # Get current brightness
            response = await self.send_command_silent("brightness")
            if response:
                # Parse brightness from response like "Current brightness: 28% (56/255)"
                try:
                    if "Current brightness:" in response:
                        # Extract percentage value
                        parts = response.split("Current brightness:")[1].strip()
                        percent_str = parts.split("%")[0].strip()
                        self.brightness = int(percent_str)
                        print(f"  Brightness: {percent_str}%")
                except (ValueError, IndexError):
                    print(f"  Could not parse brightness: {response}")
            
            self.device_info_loaded = True
            return True
            
        except Exception as e:
            print(f"  ⚠ Error loading device info: {e}")
            return False
    
    def display_device_info(self):
        """Display stored device information"""
        if not self.device_info_loaded:
            print("Device info not loaded yet")
            return
        
        print("\n" + "="*60)
        print("  DEVICE INFORMATION")
        print("="*60)
        if self.word_mode:
            print(f"Word Mode: {self.word_mode}")
        
        if self.effects_list:
            print(f"\nAvailable Effects ({len(self.effects_list)}):")
            for effect_num in sorted(self.effects_list.keys()):
                print(f"  {effect_num:2d} - {self.effects_list[effect_num]}")
        print("="*60 + "\n")
    
    def get_effect_name(self, effect_num: int) -> str:
        """Get effect name by number"""
        return self.effects_list.get(effect_num, f"Unknown Effect {effect_num}")
    
    async def send_command(self, command: str) -> bool:
        """Send a command to the LED controller"""
        if not self.is_connected():
            print("ERROR: Not connected to device")
            return False
        
        try:
            # Clear any pending data
            self.serial.reset_input_buffer()
            
            cmd = command.strip() + "\n"
            self.serial.write(cmd.encode())
            self.serial.flush()
            print(f"→ Sent: {command}")
            
            # Wait for response - handle multi-line responses
            await asyncio.sleep(0.1)
            
            response_lines = []
            empty_line_count = 0
            
            while empty_line_count < 2:  # Stop after 2 consecutive empty lines
                try:
                    # Set a shorter timeout per line
                    self.serial.timeout = 0.1
                    line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    
                    if not line:
                        empty_line_count += 1
                    else:
                        empty_line_count = 0
                        response_lines.append(line)
                    
                    # Safety limit for number of lines
                    if len(response_lines) > 20:
                        break
                except:
                    break
            
            # Print all response lines
            for line in response_lines:
                if line:
                    print(f"← {line}")
            
            return True
            
        except Exception as e:
            print(f"ERROR sending command: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from device"""
        if self.serial:
            try:
                self.serial.close()
                print("Disconnected")
            except:
                pass
    
    async def interactive_mode(self):
        """Interactive command mode"""
        print("\n" + "="*60)
        print("  INTERACTIVE SERIAL LED CONTROL MODE")
        print("="*60)
        print("Type 'help' for command list, 'quit' to exit")
        print("Type 'info' to display device information")
        print("Type 'list' to list available COM ports\n")
        
        print("QUICK REFERENCE:")
        print("  Turn off all: off")
        print("  Turn on: on")
        print("  Set letter (M,A,T,C,H) to effect: m.5 a.3 t.1")
        print("  Word mode: word.1 (effect 0-13)")
        print("  Brightness: brightness.50 (0-100)")
        print("")
        
        # Display device info on startup
        self.display_device_info()
        
        loop = asyncio.get_event_loop()
        
        while True:
            try:
                # Use run_in_executor to avoid blocking on input
                cmd = await loop.run_in_executor(None, input, "> ")
                cmd = cmd.strip()
                
                if not cmd:
                    continue
                
                if cmd.lower() == 'quit':
                    break
                
                if cmd.lower() == 'info':
                    self.display_device_info()
                    continue
                
                if cmd.lower() == 'list':
                    ports = self.list_available_ports()
                    if ports:
                        print("\nAvailable COM ports:")
                        for p in ports:
                            print(f"  {p['port']}: {p['description']}")
                    else:
                        print("No COM ports available")
                    continue
                
                await self.send_command(cmd)
                
            except KeyboardInterrupt:
                print("\nInterrupted")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")


async def main():
    """Main async function"""
    print("╔════════════════════════════════════════╗")
    print("║  Glowing Match LED Display Controller  ║")
    print("║       Serial Control Script (Python)   ║")
    print("╚════════════════════════════════════════╝\n")
    
    # List available ports
    all_ports = LEDControllerSerial.list_available_ports()
    
    if not all_ports:
        print("ERROR: No COM ports found!")
        print("Make sure your ESP32 is connected via USB")
        sys.exit(1)
    
    # Filter out generic serial ports with "n/a" description
    # Prioritize ports with actual hardware descriptions
    active_ports = [p for p in all_ports if p['description'] and p['description'].lower() != 'n/a']
    
    # If no active ports found, use all ports (for debugging)
    ports_to_use = active_ports if active_ports else all_ports
    
    print(f"Available COM ports: (showing {len(ports_to_use)} of {len(all_ports)})")
    for i, port in enumerate(ports_to_use):
        marker = "← LIKELY DEVICE" if port['port'].startswith('/dev/ttyACM') or 'USB' in port['description'] else ""
        print(f"  {i}: {port['port']} - {port['description']} {marker}")
    
    # Auto-detect or prompt for port
    if len(ports_to_use) == 1:
        selected_port = ports_to_use[0]['port']
        print(f"\n✓ Auto-selecting: {selected_port}")
    else:
        port_idx = input("\nSelect port number: ").strip()
        try:
            selected_port = ports_to_use[int(port_idx)]['port']
        except (ValueError, IndexError):
            print("Invalid selection")
            sys.exit(1)
    
    # Connect
    controller = LEDControllerSerial(port=selected_port)
    if not await controller.connect():
        sys.exit(1)
    
    # Interactive mode
    try:
        await controller.interactive_mode()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await controller.disconnect()


if __name__ == "__main__":
    # Check if pyserial is installed
    try:
        import serial
    except ImportError:
        print("ERROR: pyserial not installed")
        print("Install it with: pip install pyserial")
        sys.exit(1)
    
    # Run async main
    asyncio.run(main())
