#!/usr/bin/env python3
"""
BonicBot Hand Gestures and Manipulation

This example demonstrates various hand gestures and manipulation tasks:
- Greeting gestures
- Expressive hand movements
- Basic manipulation patterns
- Coordinated arm movements
"""

import time
from bonicbot import BonicBotController

def wave_hello(bot, hand='right', waves=3):
    """Wave hello gesture"""
    print(f"Waving hello with {hand} hand...")
    
    if hand == 'right':
        # Raise right arm
        bot.control_right_hand(
            shoulder_pitch=-60,
            elbow_angle=60,
            wrist_angle=0
        )
        time.sleep(1.5)
        
        # Wave motion
        for i in range(waves):
            bot.control_right_hand(
                shoulder_pitch=-60,
                elbow_angle=60,
                wrist_angle=45
            )
            time.sleep(0.5)
            bot.control_right_hand(
                shoulder_pitch=-60,
                elbow_angle=60,
                wrist_angle=-45
            )
            time.sleep(0.5)
        
        # Return to neutral
        bot.control_right_hand()
        
    else:  # left hand
        # Raise left arm
        bot.control_left_hand(
            shoulder_pitch=60,
            elbow_angle=-60,
            wrist_angle=0
        )
        time.sleep(1.5)
        
        # Wave motion
        for i in range(waves):
            bot.control_left_hand(
                shoulder_pitch=60,
                elbow_angle=-60,
                wrist_angle=45
            )
            time.sleep(0.5)
            bot.control_left_hand(
                shoulder_pitch=60,
                elbow_angle=-60,
                wrist_angle=-45
            )
            time.sleep(0.5)
        
        # Return to neutral
        bot.control_left_hand()

def pointing_gesture(bot, direction='forward'):
    """Point in different directions"""
    print(f"Pointing {direction}...")
    
    if direction == 'forward':
        bot.control_right_hand(
            shoulder_pitch=-45,
            elbow_angle=45,
            wrist_angle=0,
            gripper_angle=0
        )
    elif direction == 'left':
        bot.control_right_hand(
            shoulder_pitch=-30,
            shoulder_yaw=60,
            elbow_angle=30,
            gripper_angle=0
        )
    elif direction == 'right':
        bot.control_right_hand(
            shoulder_pitch=-30,
            shoulder_yaw=-60,
            elbow_angle=30,
            gripper_angle=0
        )
    elif direction == 'up':
        bot.control_right_hand(
            shoulder_pitch=-120,
            elbow_angle=0,
            gripper_angle=0
        )
    
    time.sleep(2)
    bot.control_right_hand()  # Return to neutral

def applause(bot, claps=5):
    """Clapping motion"""
    print(f"Applauding with {claps} claps...")
    
    for i in range(claps):
        # Hands together
        bot.control_left_hand(
            shoulder_pitch=30,
            shoulder_yaw=-30,
            elbow_angle=-45
        )
        bot.control_right_hand(
            shoulder_pitch=-30,
            shoulder_yaw=30,
            elbow_angle=45
        )
        time.sleep(0.3)
        
        # Hands apart
        bot.control_left_hand(
            shoulder_pitch=30,
            shoulder_yaw=0,
            elbow_angle=-30
        )
        bot.control_right_hand(
            shoulder_pitch=-30,
            shoulder_yaw=0,
            elbow_angle=30
        )
        time.sleep(0.3)
    
    # Return to neutral
    bot.control_left_hand()
    bot.control_right_hand()

def thinking_pose(bot):
    """Classic thinking pose"""
    print("Striking a thinking pose...")
    
    # Hand to chin pose
    bot.control_right_hand(
        shoulder_pitch=-90,
        elbow_angle=90,
        wrist_angle=-30,
        gripper_angle=20
    )
    
    # Tilt head slightly
    bot.control_head(pan_angle=10, tilt_angle=5)
    
    time.sleep(3)
    
    # Return to neutral
    bot.control_right_hand()
    bot.control_head()

def victory_pose(bot):
    """Victory pose with both arms up"""
    print("Victory pose!")
    
    # Both arms up in V shape
    bot.control_left_hand(
        shoulder_pitch=120,
        shoulder_yaw=-20,
        elbow_angle=-30,
        gripper_angle=45
    )
    bot.control_right_hand(
        shoulder_pitch=-120,
        shoulder_yaw=-20,
        elbow_angle=30,
        gripper_angle=45
    )
    
    time.sleep(3)
    
    # Return to neutral
    bot.control_left_hand()
    bot.control_right_hand()

def pick_and_place_simulation(bot):
    """Simulate picking up and placing an object"""
    print("Simulating pick and place operation...")
    
    # Reach down to pick up object
    print("  Reaching for object...")
    bot.control_right_hand(
        shoulder_pitch=0,
        elbow_angle=60,
        wrist_angle=-30,
        gripper_angle=60  # Open gripper
    )
    time.sleep(2)
    
    # Close gripper to "grasp" object
    print("  Grasping object...")
    bot.control_right_hand(
        shoulder_pitch=0,
        elbow_angle=60,
        wrist_angle=-30,
        gripper_angle=-30  # Close gripper
    )
    time.sleep(1)
    
    # Lift object
    print("  Lifting object...")
    bot.control_right_hand(
        shoulder_pitch=-45,
        elbow_angle=30,
        wrist_angle=0,
        gripper_angle=-30  # Keep gripper closed
    )
    time.sleep(2)
    
    # Move to placement position
    print("  Moving to placement position...")
    bot.control_right_hand(
        shoulder_pitch=-30,
        shoulder_yaw=-45,
        elbow_angle=45,
        wrist_angle=0,
        gripper_angle=-30
    )
    time.sleep(2)
    
    # Place object (open gripper)
    print("  Placing object...")
    bot.control_right_hand(
        shoulder_pitch=-30,
        shoulder_yaw=-45,
        elbow_angle=45,
        wrist_angle=0,
        gripper_angle=60  # Open gripper
    )
    time.sleep(1)
    
    # Return to neutral
    bot.control_right_hand()

def expressive_gestures(bot):
    """Various expressive gestures"""
    print("Performing expressive gestures...")
    
    gestures = [
        ("Shrug", lambda: [
            bot.control_left_hand(shoulder_pitch=60, shoulder_roll=30),
            bot.control_right_hand(shoulder_pitch=-60, shoulder_roll=-30),
            bot.control_head(tilt_angle=10)
        ]),
        
        ("Stop/Halt", lambda: [
            bot.control_right_hand(shoulder_pitch=-90, elbow_angle=0, gripper_angle=60)
        ]),
        
        ("Come here", lambda: [
            bot.control_right_hand(shoulder_pitch=-45, elbow_angle=60, wrist_angle=30)
        ]),
        
        ("Thumbs up", lambda: [
            bot.control_right_hand(shoulder_pitch=-30, elbow_angle=45, gripper_angle=-60)
        ])
    ]
    
    for name, gesture_func in gestures:
        print(f"  {name}")
        gesture_func()
        time.sleep(2.5)
        
        # Return to neutral between gestures
        bot.control_left_hand()
        bot.control_right_hand()
        bot.control_head()
        time.sleep(1)

def main():
    PORT = '/dev/ttyUSB0'  # Adjust for your system
    
    print("BonicBot Hand Gestures and Manipulation")
    print("======================================")
    
    try:
        with BonicBotController(PORT) as bot:
            print(f"✓ Connected to robot on {PORT}")
            print("\nStarting gesture demonstrations...\n")
            
            # Reset to neutral position
            bot.control_head()
            bot.control_left_hand()
            bot.control_right_hand()
            time.sleep(1)
            
            # Demonstrate various gestures
            wave_hello(bot, 'right', waves=3)
            time.sleep(2)
            
            pointing_gesture(bot, 'forward')
            time.sleep(1)
            pointing_gesture(bot, 'left')
            time.sleep(1)
            pointing_gesture(bot, 'right')
            time.sleep(1)
            
            applause(bot, claps=4)
            time.sleep(2)
            
            thinking_pose(bot)
            time.sleep(2)
            
            victory_pose(bot)
            time.sleep(2)
            
            pick_and_place_simulation(bot)
            time.sleep(2)
            
            expressive_gestures(bot)
            
            # Final neutral position
            print("Returning to neutral position...")
            bot.control_head()
            bot.control_left_hand()
            bot.control_right_hand()
            
            print("\n✓ Gesture demonstration completed!")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("  Please check your robot connection and try again")

if __name__ == "__main__":
    main()