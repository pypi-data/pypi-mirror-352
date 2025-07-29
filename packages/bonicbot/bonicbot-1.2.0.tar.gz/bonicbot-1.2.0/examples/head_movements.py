#!/usr/bin/env python3
"""
BonicBot Head Movement Patterns

This example demonstrates various head movement patterns including:
- Scanning patterns
- Tracking simulation
- Expressive movements
- Attention behaviors
"""

import time
import math
from bonicbot import BonicBotController

def scanning_pattern(bot, cycles=2):
    """Perform a scanning pattern - left to right sweep"""
    print("Performing scanning pattern...")
    
    for cycle in range(cycles):
        print(f"  Scan cycle {cycle + 1}/{cycles}")
        
        # Sweep from left to right
        positions = [-60, -30, 0, 30, 60, 30, 0, -30]
        for pan_angle in positions:
            bot.control_head(pan_angle=pan_angle, tilt_angle=5)
            time.sleep(0.8)

def tracking_simulation(bot):
    """Simulate tracking a moving object"""
    print("Simulating object tracking...")
    
    # Simulate tracking an object moving in a figure-8 pattern
    steps = 20
    for i in range(steps * 2):  # Two complete cycles
        t = i * 2 * math.pi / steps
        
        # Figure-8 pattern
        pan = 30 * math.sin(t)
        tilt = 15 * math.sin(2 * t)
        
        bot.control_head(pan_angle=pan, tilt_angle=tilt, pan_speed=150, tilt_speed=150)
        time.sleep(0.2)

def expressive_movements(bot):
    """Demonstrate expressive head movements"""
    print("Performing expressive movements...")
    
    movements = [
        ("Nodding 'yes'", [(0, 20), (0, -10), (0, 20), (0, 0)]),
        ("Shaking 'no'", [(30, 0), (-30, 0), (30, 0), (0, 0)]),
        ("Confused", [(20, 10), (-20, 10), (0, 0)]),
        ("Looking up in wonder", [(0, 35), (0, 0)]),
        ("Shame/looking down", [(0, -25), (0, 0)])
    ]
    
    for description, positions in movements:
        print(f"  {description}")
        for pan, tilt in positions:
            bot.control_head(pan_angle=pan, tilt_angle=tilt)
            time.sleep(1.2)
        time.sleep(0.5)

def attention_behaviors(bot):
    """Demonstrate attention and alertness behaviors"""
    print("Performing attention behaviors...")
    
    behaviors = [
        ("Alert scan", [(-45, 15), (45, 15), (0, 0)]),
        ("Quick look around", [(-30, 0), (30, 0), (0, 20), (0, 0)]),
        ("Cautious peek", [(60, -10), (0, 0)]),
        ("Double-take", [(0, 0), (45, 5), (0, 0), (45, 5), (0, 0)])
    ]
    
    for description, positions in behaviors:
        print(f"  {description}")
        for pan, tilt in positions:
            bot.control_head(pan_angle=pan, tilt_angle=tilt, pan_speed=300, tilt_speed=300)
            time.sleep(0.8)
        time.sleep(1)

def smooth_circle(bot, radius=30, speed=100):
    """Move head in a smooth circular pattern"""
    print(f"Performing smooth circular movement (radius={radius}°)...")
    
    steps = 16
    for i in range(steps + 1):  # +1 to complete the circle
        angle = i * 2 * math.pi / steps
        pan = radius * math.cos(angle)
        tilt = radius * 0.5 * math.sin(angle)  # Smaller vertical movement
        
        bot.control_head(pan_angle=pan, tilt_angle=tilt, pan_speed=speed, tilt_speed=speed)
        time.sleep(0.3)

def main():
    PORT = '/dev/ttyUSB0'  # Adjust for your system
    
    print("BonicBot Head Movement Patterns")
    print("===============================")
    
    try:
        with BonicBotController(PORT) as bot:
            print(f"✓ Connected to robot on {PORT}")
            print("\nStarting head movement demonstrations...\n")
            
            # Center head first
            bot.control_head(pan_angle=0, tilt_angle=0)
            time.sleep(1)
            
            # Demonstrate different movement patterns
            scanning_pattern(bot, cycles=2)
            time.sleep(2)
            
            tracking_simulation(bot)
            time.sleep(2)
            
            expressive_movements(bot)
            time.sleep(2)
            
            attention_behaviors(bot)
            time.sleep(2)
            
            smooth_circle(bot, radius=40, speed=150)
            time.sleep(2)
            
            # Return to center
            print("Returning to center position...")
            bot.control_head(pan_angle=0, tilt_angle=0)
            
            print("\n✓ Head movement demonstration completed!")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("  Please check your robot connection and try again")

if __name__ == "__main__":
    main()