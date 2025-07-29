#!/usr/bin/env python3
"""
Basic BonicBot Control Example

This example demonstrates basic control of the BonicBot robot including:
- Connecting via Serial and WebSocket
- Individual servo control
- Group control methods
- Basic movements

Communication options:
- Serial: '/dev/ttyUSB0' (Linux/Mac) or 'COM3' (Windows)
- WebSocket: 'ws://192.168.1.100:8080/control' (adjust IP as needed)
"""

import time
from bonicbot import (
    BonicBotController, 
    ServoID, 
    CommunicationType,
    create_serial_controller,
    create_websocket_controller
)

def demonstrate_robot_control(bot, connection_type):
    """Demonstrate robot control with any communication method."""
    print(f"\n🤖 {connection_type} Control Demo")
    print("=" * 40)
    
    if not bot.is_connected():
        print("❌ Robot not connected!")
        return
    
    print("✅ Robot connected successfully!")
    
    # Individual servo control examples
    print("\n1. Individual Servo Control")
    print("Moving head pan to 45 degrees...")
    bot.control_servo(ServoID.HEAD_PAN, angle=45.0, speed=200)
    time.sleep(2)
    
    print("Moving head tilt to 20 degrees...")
    bot.control_servo('headTilt', angle=20.0, speed=150)
    time.sleep(2)
    
    # Group control examples
    print("\n2. Group Control - Head")
    print("Moving head to look around...")
    positions = [
        (45, 10),   # Look right and up
        (-45, 10),  # Look left and up
        (0, -20),   # Look forward and down
        (0, 0)      # Center position
    ]
    
    for pan, tilt in positions:
        print(f"Head position: pan={pan}°, tilt={tilt}°")
        bot.control_head(pan_angle=pan, tilt_angle=tilt)
        time.sleep(1.5)
    
    print("\n3. Hand Control")
    print("Moving left hand...")
    bot.control_left_hand(
        gripper_angle=45.0,
        elbow_angle=-30.0,
        shoulder_pitch=45.0
    )
    time.sleep(2)
    
    print("Moving right hand...")
    bot.control_right_hand(
        gripper_angle=-45.0,
        elbow_angle=30.0,
        shoulder_pitch=-45.0
    )
    time.sleep(2)
    
    print("\n4. Base Movement")
    print("Moving forward...")
    bot.move_forward(speed=80)
    time.sleep(1)
    
    print("Turning left...")
    bot.turn_left(speed=60)
    time.sleep(1)
    
    print("Turning right...")
    bot.turn_right(speed=60)
    time.sleep(1)
    
    print("Moving backward...")
    bot.move_backward(speed=80)
    time.sleep(1)
    
    print("Stopping...")
    bot.stop()
    
    print("\n5. Return to Home Position")
    # Return all servos to neutral position
    bot.control_head(pan_angle=0.0, tilt_angle=0.0)
    bot.control_left_hand()  # All parameters default to 0
    bot.control_right_hand()
    
    print("✅ Returned to home position")

def test_serial_connection():
    """Test serial communication."""
    PORT = '/dev/ttyUSB0'  # Change this to your robot's port
    print(f"\n📡 Testing Serial Connection: {PORT}")
    
    try:
        # Method 1: Using convenience function
        with create_serial_controller(PORT) as bot:
            demonstrate_robot_control(bot, "Serial")
            
    except FileNotFoundError:
        print(f"❌ Could not find serial port {PORT}")
        print("  Please check your connection and adjust the PORT variable")
    except PermissionError:
        print(f"❌ Permission denied for port {PORT}")
        print("  Try running with sudo or check port permissions")
    except Exception as e:
        print(f"❌ Serial connection error: {str(e)}")

def test_websocket_connection():
    """Test WebSocket communication."""
    WEBSOCKET_URI = 'ws://192.168.1.100:8080/control'  # Change this to your robot's WebSocket URI
    print(f"\n🌐 Testing WebSocket Connection: {WEBSOCKET_URI}")
    
    try:
        # Method 1: Using convenience function
        with create_websocket_controller(WEBSOCKET_URI) as bot:
            demonstrate_robot_control(bot, "WebSocket")
            
    except Exception as e:
        print(f"❌ WebSocket connection error: {str(e)}")
        print(f"  Please check that the robot is accessible at {WEBSOCKET_URI}")

def test_direct_initialization():
    """Test direct controller initialization methods."""
    print("\n⚙️ Testing Direct Initialization Methods")
    
    # Test serial initialization
    try:
        bot = BonicBotController('serial', port='/dev/ttyUSB0')
        if bot.is_connected():
            print("✅ Direct serial initialization successful")
            bot.close()
        else:
            print("❌ Direct serial initialization failed")
    except Exception as e:
        print(f"❌ Direct serial init error: {e}")
    
    # Test WebSocket initialization  
    try:
        bot = BonicBotController(
            CommunicationType.WEBSOCKET, 
            websocket_uri='ws://192.168.1.100:8080/control'
        )
        if bot.is_connected():
            print("✅ Direct WebSocket initialization successful")
            bot.close()
        else:
            print("❌ Direct WebSocket initialization failed")
    except Exception as e:
        print(f"❌ Direct WebSocket init error: {e}")

def main():
    print("BonicBot Basic Control Example")
    print("==============================")
    print("This example demonstrates both Serial and WebSocket communication")
    
    # Test both communication methods
    test_serial_connection()
    test_websocket_connection()
    test_direct_initialization()
    
    print("\n🎉 Example completed!")
    print("\n💡 Tips:")
    print("   - Adjust PORT and WEBSOCKET_URI variables for your setup")
    print("   - Serial: Ensure correct permissions and port name")
    print("   - WebSocket: Ensure robot is network-accessible")

if __name__ == "__main__":
    main()