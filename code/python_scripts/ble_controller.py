#!/usr/bin/env python3
"""
BLE Control Script for Glowing Match LED Display (ESP32-C6)
Uses Bleak for cross-platform BLE communication

Install required packages:
    pip install bleak
"""

import asyncio
import sys
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "GlowingMatch"  # Name of the device to connect to

# BLE UUIDs - must match BLECommandHandler.h
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
COMMAND_CHAR_UUID = "87654321-4321-8765-4321-0fedcba98765"
RESPONSE_CHAR_UUID = "abcdef00-abcd-ef00-abcd-ef0012345678"

class LEDControllerBLE:
    def __init__(self, device_name=DEVICE_NAME):
        self.device_name = device_name
        self.client = None
        self.device = None
        # Device information storage
        self.word_mode = None
        self.effects_list = {}
        self.device_info_loaded = False
        self.brightness = 100  # Default brightness
        
    async def read_response(self):
        """Read response from device"""
        try:
            response = await self.client.read_gatt_char(RESPONSE_CHAR_UUID)
            return response.decode('utf-8', errors='ignore').strip()
        except:
            return None
    
    async def send_command_silent(self, command):
        """Send a command and return raw response without printing"""
        if not await self.is_connected():
            return None
        
        try:
            cmd = command.strip() + "\n"
            await self.client.write_gatt_char(COMMAND_CHAR_UUID, cmd.encode())
            await asyncio.sleep(0.2)
            response = await self.read_response()
            return response
        except Exception as e:
            return None
    
    async def load_device_info(self):
        """Load critical device information (word mode and effects)"""
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
    
    def get_effect_name(self, effect_num):
        """Get effect name by number"""
        return self.effects_list.get(effect_num, f"Unknown Effect {effect_num}")
    
    async def scan_devices(self):
        """Scan for BLE devices"""
        print("\nScanning for BLE devices...")
        devices = await BleakScanner.discover()
        
        if not devices:
            print("No devices found!")
            return []
        
        print(f"\nFound {len(devices)} device(s):")
        target_device = None
        for i, device in enumerate(devices):
            print(f"  {i}: {device.name or 'Unknown'} ({device.address})")
            if device.name and self.device_name in device.name:
                print(f"     ^ {self.device_name} (TARGET DEVICE - Will auto-connect!)")
                target_device = device
        
        return devices, target_device
    
    async def connect(self, device):
        """Connect to BLE device"""
        try:
            print(f"\nConnecting to {device.name or device.address}...")
            self.client = BleakClient(device)
            await self.client.connect()
            self.device = device
            print("✓ Connected successfully!")
            
            # Try to read from the service to confirm connection
            try:
                response = await self.read_response()
                if response:
                    print(f"Device response: {response}")
            except Exception as e:
                print(f"Note: Could not read initial response: {e}")
            
            # Load device information
            await self.load_device_info()
            
            return True
            
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def is_connected(self):
        """Check if device is still connected"""
        if not self.client:
            return False
        return self.client.is_connected
    
    async def check_connection(self):
        """Verify connection by reading a characteristic"""
        if not self.client or not self.client.is_connected:
            return False
        
        try:
            # Try to read response characteristic to verify connection
            await self.client.read_gatt_char(RESPONSE_CHAR_UUID)
            return True
        except Exception:
            return False
    
    async def reconnect(self, max_retries=3):
        """Attempt to reconnect to the device"""
        if not self.device:
            print("ERROR: No device information stored for reconnection")
            return False
        
        for attempt in range(max_retries):
            print(f"\n[Reconnect] Attempt {attempt + 1}/{max_retries}...")
            try:
                # Disconnect old connection if it exists
                if self.client:
                    try:
                        await self.client.disconnect()
                    except:
                        pass
                
                # Try to reconnect
                self.client = BleakClient(self.device)
                await self.client.connect()
                print("✓ Reconnected successfully!")
                return True
                
            except Exception as e:
                print(f"✗ Reconnection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # Wait before retrying
        
        return False
    
    async def send_command(self, command):
        """Send a command to the LED controller"""
        # Check connection and auto-reconnect if needed
        if not await self.is_connected():
            print("⚠ Connection lost, attempting to reconnect...")
            if not await self.reconnect():
                print("✗ ERROR: Failed to reconnect to device")
                return False
            print("✓ Reconnection successful, resuming operation...")
        
        try:
            cmd = command.strip() + "\n"
            await self.client.write_gatt_char(COMMAND_CHAR_UUID, cmd.encode())
            print(f"→ Sent: {command}")
            
            # Wait for response
            await asyncio.sleep(0.2)
            try:
                response = await self.client.read_gatt_char(RESPONSE_CHAR_UUID)
                response_text = response.decode('utf-8', errors='ignore').strip()
                if response_text:
                    print(f"← {response_text}")
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"ERROR sending command: {e}")
            # Mark as disconnected on error
            return False
    
    async def disconnect(self):
        """Disconnect from device"""
        if self.client:
            try:
                await self.client.disconnect()
                print("Disconnected")
            except:
                pass
    
    async def interactive_mode(self):
        """Interactive command mode"""
        print("\n" + "="*60)
        print("  INTERACTIVE BLE LED CONTROL MODE")
        print("="*60)
        print("Type 'help' for command list, 'quit' to exit")
        print("Type 'info' to display device information")
        print("Connection monitoring: ENABLED (auto-reconnect on disconnect)\n")
        
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
        connection_check_counter = 0
        
        while True:
            try:
                # Periodically check connection (every 10 commands)
                connection_check_counter += 1
                if connection_check_counter >= 10:
                    is_still_connected = await self.check_connection()
                    if not is_still_connected:
                        print("\n⚠ Connection lost! Attempting to reconnect...")
                        if await self.reconnect():
                            print("✓ Reconnected!\n")
                            # Reload device info after reconnect
                            self.device_info_loaded = False
                            await self.load_device_info()
                        else:
                            print("✗ Failed to reconnect. Exiting...")
                            break
                    connection_check_counter = 0
                
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
    print("║          BLE Control Script (Python)   ║")
    print("╚════════════════════════════════════════╝\n")
    
    controller = LEDControllerBLE()
    
    # Scan for devices
    devices, target_device = await controller.scan_devices()
    
    if not devices:
        print("\nNo BLE devices found. Make sure:")
        print("  1. Your ESP32-C6 is powered on")
        print("  2. It's running the LED control sketch")
        print("  3. BLE is enabled on your device")
        sys.exit(1)
    
    # Auto-connect to target device if found
    if target_device:
        print(f"\n✓ Found target device '{DEVICE_NAME}', attempting auto-connect...")
        if not await controller.connect(target_device):
            sys.exit(1)
    else:
        print(f"\n✗ Target device '{DEVICE_NAME}' not found!")
        print("Available devices listed above. Make sure your ESP32 is powered on and running the sketch.")
        sys.exit(1)
    
    # Interactive mode
    try:
        await controller.interactive_mode()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await controller.disconnect()


if __name__ == "__main__":
    # Check if bleak is installed
    try:
        import bleak
    except ImportError:
        print("ERROR: bleak not installed")
        print("Install it with: pip install bleak")
        sys.exit(1)
    
    # Run async main
    asyncio.run(main())
