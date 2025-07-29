#!/usr/bin/env python3
"""
BonicBot WebSocket Control Example

This example demonstrates WebSocket communication with BonicBot robots including:
- Network discovery and connection
- Remote robot control
- Connection monitoring
- Error handling for network issues

WebSocket Features:
- Remote control over WiFi/Ethernet
- Real-time bidirectional communication  
- Multiple client support (if robot supports it)
- Network resilience with reconnection

Setup Requirements:
1. Robot must be connected to same network
2. Robot must be running WebSocket server
3. Adjust ROBOT_IP and PORT as needed
"""

import time
import threading
from bonicbot import create_websocket_controller, BonicBotController, CommunicationType

# Configuration - Adjust these for your robot
ROBOT_IP = "192.168.1.100"
ROBOT_PORT = 8080
WEBSOCKET_PATH = "/control"
WEBSOCKET_URI = f"ws://{ROBOT_IP}:{ROBOT_PORT}{WEBSOCKET_PATH}"

def test_connection_stability(bot, duration=30):
    """Test WebSocket connection stability over time."""
    print(f"\n🔄 Testing connection stability for {duration} seconds...")
    
    start_time = time.time()
    successful_commands = 0
    failed_commands = 0
    
    while time.time() - start_time < duration:
        try:
            if bot.is_connected():
                # Send a simple command
                angle = 20 * (1 if (time.time() % 4) < 2 else -1)  # Oscillate
                bot.control_servo('headPan', angle=angle, speed=100)
                successful_commands += 1
                print(f"✅ Command {successful_commands}: Head pan to {angle}°")
            else:
                print("❌ Connection lost!")
                failed_commands += 1
                
        except Exception as e:
            print(f"❌ Command failed: {e}")
            failed_commands += 1
        
        time.sleep(2)
    
    print(f"\n📊 Connection Stability Results:")
    print(f"   Successful commands: {successful_commands}")
    print(f"   Failed commands: {failed_commands}")
    print(f"   Success rate: {successful_commands/(successful_commands+failed_commands)*100:.1f}%")

def demonstrate_remote_gestures(bot):
    """Demonstrate complex gestures over WebSocket."""
    print("\n🎭 Demonstrating Remote Gesture Control")
    
    gestures = [
        {
            "name": "Wave Hello",
            "actions": [
                lambda: bot.control_right_hand(shoulder_pitch=-60, elbow_angle=60),
                lambda: time.sleep(1),
                lambda: [bot.control_right_hand(shoulder_pitch=-60, elbow_angle=60, wrist_angle=45), time.sleep(0.5)],
                lambda: [bot.control_right_hand(shoulder_pitch=-60, elbow_angle=60, wrist_angle=-45), time.sleep(0.5)],
                lambda: [bot.control_right_hand(shoulder_pitch=-60, elbow_angle=60, wrist_angle=45), time.sleep(0.5)],
                lambda: [bot.control_right_hand(shoulder_pitch=-60, elbow_angle=60, wrist_angle=-45), time.sleep(0.5)],
                lambda: bot.control_right_hand()  # Return to neutral
            ]
        },
        {
            "name": "Look Around",
            "actions": [
                lambda: bot.control_head(pan_angle=-60, tilt_angle=10),
                lambda: time.sleep(1.5),
                lambda: bot.control_head(pan_angle=60, tilt_angle=10),
                lambda: time.sleep(1.5),
                lambda: bot.control_head(pan_angle=0, tilt_angle=-20),
                lambda: time.sleep(1.5),
                lambda: bot.control_head(pan_angle=0, tilt_angle=0)  # Center
            ]
        },
        {
            "name": "Dance Move",
            "actions": [
                lambda: bot.control_left_hand(shoulder_pitch=90, shoulder_roll=30),
                lambda: bot.control_right_hand(shoulder_pitch=-90, shoulder_roll=-30),
                lambda: time.sleep(1),
                lambda: bot.control_left_hand(shoulder_pitch=30, shoulder_roll=-30),
                lambda: bot.control_right_hand(shoulder_pitch=-30, shoulder_roll=30),
                lambda: time.sleep(1),
                lambda: bot.control_left_hand(),  # Return to neutral
                lambda: bot.control_right_hand()
            ]
        }
    ]
    
    for gesture in gestures:
        print(f"\n🎪 Performing: {gesture['name']}")
        try:
            for action in gesture['actions']:
                if callable(action):
                    result = action()
                    if isinstance(result, list):  # Handle multiple actions
                        for sub_action in result:
                            if callable(sub_action):
                                sub_action()
            print(f"✅ {gesture['name']} completed successfully")
        except Exception as e:
            print(f"❌ {gesture['name']} failed: {e}")
        
        time.sleep(0.5)  # Brief pause between gestures

def monitor_connection_in_background(bot, stop_event):
    """Monitor connection status in background thread."""
    print("\n📡 Starting connection monitor...")
    
    last_status = None
    while not stop_event.is_set():
        current_status = bot.is_connected()
        
        if current_status != last_status:
            status_text = "CONNECTED" if current_status else "DISCONNECTED"
            emoji = "✅" if current_status else "❌"
            print(f"{emoji} Connection status changed: {status_text}")
            last_status = current_status
        
        time.sleep(1)

def test_multiple_connection_methods():
    """Test different ways to create WebSocket connections."""
    print("\n🔧 Testing Multiple Connection Methods")
    
    methods = [
        {
            "name": "Convenience Function",
            "create": lambda: create_websocket_controller(WEBSOCKET_URI)
        },
        {
            "name": "Direct with String",
            "create": lambda: BonicBotController('websocket', websocket_uri=WEBSOCKET_URI)
        },
        {
            "name": "Direct with Enum",
            "create": lambda: BonicBotController(CommunicationType.WEBSOCKET, websocket_uri=WEBSOCKET_URI)
        }
    ]
    
    for method in methods:
        print(f"\n🧪 Testing: {method['name']}")
        try:
            with method['create']() as bot:
                if bot.is_connected():
                    print(f"✅ {method['name']}: Connection successful")
                    # Quick test
                    bot.control_servo('headPan', angle=10, speed=200)
                    time.sleep(0.5)
                    bot.control_servo('headPan', angle=0, speed=200)
                else:
                    print(f"❌ {method['name']}: Connection failed")
        except Exception as e:
            print(f"❌ {method['name']}: Error - {e}")

def main():
    print("BonicBot WebSocket Control Example")
    print("==================================")
    print(f"Target: {WEBSOCKET_URI}")
    print(f"Robot IP: {ROBOT_IP}")
    
    # Test different connection methods first
    test_multiple_connection_methods()
    
    print(f"\n🌐 Connecting to robot via WebSocket...")
    
    try:
        with create_websocket_controller(WEBSOCKET_URI) as bot:
            if not bot.is_connected():
                print("❌ Failed to connect to robot")
                return
            
            print("✅ WebSocket connection established!")
            
            # Start background connection monitoring
            stop_monitor = threading.Event()
            monitor_thread = threading.Thread(
                target=monitor_connection_in_background,
                args=(bot, stop_monitor),
                daemon=True
            )
            monitor_thread.start()
            
            # Demonstrate remote control capabilities
            demonstrate_remote_gestures(bot)
            
            # Test connection stability
            test_connection_stability(bot, duration=15)
            
            # Stop monitoring
            stop_monitor.set()
            
            print("\n🏠 Returning robot to home position...")
            bot.control_head(pan_angle=0, tilt_angle=0)
            bot.control_left_hand()
            bot.control_right_hand()
            bot.stop()  # Stop base motors
            
            print("✅ WebSocket control demo completed!")
            
    except ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print(f"💡 Troubleshooting tips:")
        print(f"   1. Check robot IP address: {ROBOT_IP}")
        print(f"   2. Verify robot is on same network")
        print(f"   3. Ensure WebSocket server is running on robot")
        print(f"   4. Check firewall settings")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()