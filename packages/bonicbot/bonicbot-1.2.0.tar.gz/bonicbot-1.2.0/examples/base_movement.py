#!/usr/bin/env python3
"""
BonicBot Base Movement Patterns

This example demonstrates various base movement patterns including:
- Basic movements (forward, backward, turning)
- Navigation patterns (square, circle, figure-8)
- Search patterns
- Controlled movements with timing
"""

import time
import math
from bonicbot import BonicBotController

def basic_movements(bot):
    """Demonstrate basic movement commands"""
    print("Demonstrating basic movements...")
    
    movements = [
        ("Forward", lambda: bot.move_forward(100)),
        ("Backward", lambda: bot.move_backward(100)),
        ("Turn Left", lambda: bot.turn_left(80)),
        ("Turn Right", lambda: bot.turn_right(80)),
        ("Stop", lambda: bot.stop())
    ]
    
    for name, movement in movements:
        print(f"  {name}")
        movement()
        time.sleep(1.5)
        bot.stop()
        time.sleep(0.5)

def square_pattern(bot, side_duration=2.0, speed=80):
    """Move in a square pattern"""
    print(f"Moving in square pattern (speed={speed})...")
    
    for i in range(4):
        print(f"  Side {i+1}/4")
        # Move forward
        bot.move_forward(speed)
        time.sleep(side_duration)
        
        # Turn 90 degrees (approximate timing)
        bot.turn_right(speed)
        time.sleep(1.0)  # Adjust this timing based on your robot
        
        bot.stop()
        time.sleep(0.5)

def circle_pattern(bot, radius_time=0.5, speed=70):
    """Move in a circular pattern"""
    print(f"Moving in circular pattern (speed={speed})...")
    
    # Create circular motion by varying left/right motor speeds
    steps = 20
    duration = 0.3
    
    for i in range(steps):
        # Calculate differential speeds for circular motion
        angle = i * 2 * math.pi / steps
        left_speed = int(speed * (1 + 0.3 * math.sin(angle)))
        right_speed = int(speed * (1 - 0.3 * math.sin(angle)))
        
        bot.control_base(left_speed, right_speed)
        time.sleep(duration)
    
    bot.stop()

def figure_eight_pattern(bot, speed=60):
    """Move in a figure-8 pattern"""
    print(f"Moving in figure-8 pattern (speed={speed})...")
    
    # First loop of the 8
    print("  First loop...")
    for i in range(10):
        bot.turn_left(speed)
        time.sleep(0.4)
    
    bot.stop()
    time.sleep(0.5)
    
    # Second loop of the 8  
    print("  Second loop...")
    for i in range(10):
        bot.turn_right(speed)
        time.sleep(0.4)
    
    bot.stop()

def search_pattern(bot, speed=70):
    """Zigzag search pattern"""
    print(f"Performing search pattern (speed={speed})...")
    
    # Zigzag pattern
    for i in range(3):
        print(f"  Zigzag {i+1}/3")
        
        # Move forward
        bot.move_forward(speed)
        time.sleep(1.5)
        
        # Turn left
        bot.turn_left(speed)
        time.sleep(0.8)
        
        # Move forward
        bot.move_forward(speed)
        time.sleep(1.0)
        
        # Turn right
        bot.turn_right(speed)
        time.sleep(1.6)  # Turn more to create zigzag
        
        # Move forward
        bot.move_forward(speed)
        time.sleep(1.0)
        
        # Turn left to prepare for next iteration
        bot.turn_left(speed)
        time.sleep(0.8)
        
        bot.stop()
        time.sleep(0.5)

def spiral_pattern(bot, speed=80, steps=15):
    """Move in an expanding spiral"""
    print(f"Moving in spiral pattern (speed={speed})...")
    
    for i in range(steps):
        # Move forward with increasing duration
        forward_time = 0.3 + (i * 0.1)
        print(f"  Spiral step {i+1}/{steps} (forward time: {forward_time:.1f}s)")
        
        bot.move_forward(speed)
        time.sleep(forward_time)
        
        # Turn (consistent angle)
        bot.turn_right(speed)
        time.sleep(0.5)
        
        bot.stop()
        time.sleep(0.2)

def precise_movements(bot):
    """Demonstrate precise movement control"""
    print("Demonstrating precise movements...")
    
    # Variable speed demonstration
    speeds = [30, 60, 100, 150, 200]
    
    for speed in speeds:
        print(f"  Forward at speed {speed}")
        bot.move_forward(speed)
        time.sleep(1.0)
        bot.stop()
        time.sleep(0.5)
    
    print("  Manual motor control...")
    # Manual differential control
    bot.control_base(100, 50)  # Turn while moving
    time.sleep(1.5)
    
    bot.control_base(50, 100)  # Turn other direction
    time.sleep(1.5)
    
    bot.control_base(-80, -80)  # Reverse
    time.sleep(1.0)
    
    bot.stop()

def obstacle_avoidance_simulation(bot):
    """Simulate obstacle avoidance behavior"""
    print("Simulating obstacle avoidance...")
    
    # Simulate approaching obstacle and avoiding
    scenarios = [
        "Moving forward and encountering obstacle",
        "Backing up",
        "Turning to avoid",
        "Moving around obstacle",
        "Continuing forward"
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"  {i+1}. {scenario}")
        
        if i == 0:  # Forward movement
            bot.move_forward(100)
            time.sleep(1.5)
        elif i == 1:  # Backup
            bot.move_backward(80)
            time.sleep(1.0)
        elif i == 2:  # Turn to avoid
            bot.turn_right(100)
            time.sleep(1.2)
        elif i == 3:  # Move around
            bot.move_forward(100)
            time.sleep(1.0)
            bot.turn_left(100)
            time.sleep(1.2)
            bot.move_forward(100)
            time.sleep(1.0)
        elif i == 4:  # Continue
            bot.move_forward(100)
            time.sleep(1.0)
        
        bot.stop()
        time.sleep(0.5)

def main():
    PORT = '/dev/ttyUSB0'  # Adjust for your system
    
    print("BonicBot Base Movement Patterns")
    print("===============================")
    print("⚠️  Warning: Ensure robot has sufficient space to move safely!")
    print("⚠️  Keep emergency stop ready and supervise all movements.\n")
    
    try:
        with BonicBotController(PORT) as bot:
            print(f"✓ Connected to robot on {PORT}")
            print("\nStarting movement demonstrations...\n")
            
            # Start with basic movements
            basic_movements(bot)
            time.sleep(2)
            
            # Geometric patterns
            square_pattern(bot, side_duration=1.5, speed=70)
            time.sleep(2)
            
            circle_pattern(bot, speed=60)
            time.sleep(2)
            
            figure_eight_pattern(bot, speed=50)
            time.sleep(2)
            
            # Search and navigation patterns
            search_pattern(bot, speed=60)
            time.sleep(2)
            
            spiral_pattern(bot, speed=70, steps=8)
            time.sleep(2)
            
            # Precision and control
            precise_movements(bot)
            time.sleep(2)
            
            # Behavioral simulation
            obstacle_avoidance_simulation(bot)
            
            # Final stop
            print("\nMovement demonstration completed!")
            print("Robot stopped and ready.")
            bot.stop()
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("  Please check your robot connection and try again")

if __name__ == "__main__":
    main()