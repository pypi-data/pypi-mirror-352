#!/usr/bin/env python3
"""
Unit tests for BonicBot Controller

These tests verify the basic functionality of the BonicBot controller
without requiring actual hardware connection.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from bonicbot.controller import BonicBotController, ServoID


class TestBonicBotController(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_serial_patcher = patch('bonicbot.controller.serial.Serial')
        self.mock_serial = self.mock_serial_patcher.start()
        
        # Configure mock serial instance
        self.mock_serial_instance = Mock()
        self.mock_serial_instance.is_open = True
        self.mock_serial_instance.write = Mock()
        self.mock_serial_instance.flush = Mock()
        self.mock_serial_instance.close = Mock()
        self.mock_serial.return_value = self.mock_serial_instance
        
        # Create controller instance
        self.controller = BonicBotController('/dev/ttyUSB0')
    
    def tearDown(self):
        """Clean up after each test method."""
        self.mock_serial_patcher.stop()
    
    def test_controller_initialization(self):
        """Test controller initialization."""
        self.assertEqual(self.controller.port, '/dev/ttyUSB0')
        self.assertEqual(self.controller.baudrate, 115200)
        self.assertEqual(self.controller.timeout, 1.0)
        self.mock_serial.assert_called_once_with(
            port='/dev/ttyUSB0',
            baudrate=115200,
            timeout=1.0
        )
    
    def test_servo_control_with_string_id(self):
        """Test individual servo control with string ID."""
        self.controller.control_servo('headPan', 45.0, 200, 20)
        
        # Verify the correct command was sent
        expected_command = {
            "commandType": "command",
            "dataType": "servo",
            "payload": {
                "angle": 45.0,
                "speed": 200,
                "acc": 20,
                "id": "headPan"
            },
            "interval": 0
        }
        
        self.mock_serial_instance.write.assert_called_once()
        written_data = self.mock_serial_instance.write.call_args[0][0]
        actual_command = json.loads(written_data.decode('utf-8'))
        self.assertEqual(actual_command, expected_command)
    
    def test_servo_control_with_enum_id(self):
        """Test individual servo control with ServoID enum."""
        self.controller.control_servo(ServoID.HEAD_TILT, -10.0, 150, 30)
        
        expected_command = {
            "commandType": "command",
            "dataType": "servo",
            "payload": {
                "angle": -10.0,
                "speed": 150,
                "acc": 30,
                "id": "headTilt"
            },
            "interval": 0
        }
        
        written_data = self.mock_serial_instance.write.call_args[0][0]
        actual_command = json.loads(written_data.decode('utf-8'))
        self.assertEqual(actual_command, expected_command)
    
    def test_invalid_servo_id(self):
        """Test error handling for invalid servo ID."""
        with self.assertRaises(ValueError):
            self.controller.control_servo('invalidServo', 45.0)
    
    def test_head_control(self):
        """Test head control method."""
        self.controller.control_head(pan_angle=30.0, tilt_angle=-15.0)
        
        expected_command = {
            "commandType": "command",
            "dataType": "head",
            "payload": {
                "mode": "None",
                "headPan": {
                    "angle": 30.0,
                    "speed": 200,
                    "acc": 20
                },
                "headTilt": {
                    "angle": -15.0,
                    "speed": 200,
                    "acc": 50
                }
            },
            "interval": 0
        }
        
        written_data = self.mock_serial_instance.write.call_args[0][0]
        actual_command = json.loads(written_data.decode('utf-8'))
        self.assertEqual(actual_command, expected_command)
    
    def test_left_hand_control(self):
        """Test left hand control method."""
        self.controller.control_left_hand(
            gripper_angle=90.0,
            elbow_angle=-45.0,
            shoulder_pitch=60.0
        )
        
        # Verify command type and structure
        written_data = self.mock_serial_instance.write.call_args[0][0]
        actual_command = json.loads(written_data.decode('utf-8'))
        
        self.assertEqual(actual_command["commandType"], "command")
        self.assertEqual(actual_command["dataType"], "leftHand")
        self.assertEqual(actual_command["payload"]["leftGripper"]["angle"], 90.0)
        self.assertEqual(actual_command["payload"]["leftElbow"]["angle"], -45.0)
        self.assertEqual(actual_command["payload"]["leftSholderPitch"]["angle"], 60.0)
    
    def test_right_hand_control(self):
        """Test right hand control method."""
        self.controller.control_right_hand(gripper_angle=-30.0)
        
        written_data = self.mock_serial_instance.write.call_args[0][0]
        actual_command = json.loads(written_data.decode('utf-8'))
        
        self.assertEqual(actual_command["dataType"], "rightHand")
        self.assertEqual(actual_command["payload"]["rightGripper"]["angle"], -30.0)
    
    def test_base_control(self):
        """Test base motor control."""
        self.controller.control_base(100, -50)
        
        expected_command = {
            "commandType": "command",
            "dataType": "base",
            "payload": {
                "leftMotor": {"speed": 100},
                "rightMotor": {"speed": -50}
            },
            "interval": 0
        }
        
        written_data = self.mock_serial_instance.write.call_args[0][0]
        actual_command = json.loads(written_data.decode('utf-8'))
        self.assertEqual(actual_command, expected_command)
    
    def test_movement_methods(self):
        """Test convenience movement methods."""
        # Test forward movement
        self.controller.move_forward(150)
        written_data = self.mock_serial_instance.write.call_args[0][0]
        command = json.loads(written_data.decode('utf-8'))
        self.assertEqual(command["payload"]["leftMotor"]["speed"], 150)
        self.assertEqual(command["payload"]["rightMotor"]["speed"], 150)
        
        # Reset mock for next test
        self.mock_serial_instance.write.reset_mock()
        
        # Test turn left
        self.controller.turn_left(100)
        written_data = self.mock_serial_instance.write.call_args[0][0]
        command = json.loads(written_data.decode('utf-8'))
        self.assertEqual(command["payload"]["leftMotor"]["speed"], -100)
        self.assertEqual(command["payload"]["rightMotor"]["speed"], 100)
    
    def test_context_manager(self):
        """Test context manager protocol."""
        with patch('bonicbot.controller.serial.Serial') as mock_serial:
            mock_instance = Mock()
            mock_instance.is_open = True
            mock_serial.return_value = mock_instance
            
            with BonicBotController('/dev/ttyUSB0') as bot:
                self.assertIsNotNone(bot)
            
            # Verify close was called
            mock_instance.close.assert_called_once()
    
    def test_connection_error_handling(self):
        """Test connection error handling."""
        with patch('bonicbot.controller.serial.Serial') as mock_serial:
            mock_serial.side_effect = Exception("Connection failed")
            
            with self.assertRaises(ConnectionError):
                BonicBotController('/dev/ttyUSB0')
    
    def test_serial_not_connected_error(self):
        """Test error when sending command without connection."""
        # Simulate disconnected state
        self.controller._serial = None
        
        with self.assertRaises(ConnectionError):
            self.controller.control_servo('headPan', 45.0)


class TestServoID(unittest.TestCase):
    """Test ServoID enumeration."""
    
    def test_servo_id_values(self):
        """Test that all servo IDs have correct string values."""
        expected_values = {
            ServoID.HEAD_PAN: "headPan",
            ServoID.HEAD_TILT: "headTilt",
            ServoID.LEFT_GRIPPER: "leftGripper",
            ServoID.LEFT_WRIST: "leftWrist",
            ServoID.LEFT_ELBOW: "leftElbow",
            ServoID.RIGHT_GRIPPER: "rightGripper",
            ServoID.RIGHT_WRIST: "rightWrist",
            ServoID.RIGHT_ELBOW: "rightElbow",
        }
        
        for servo_id, expected_value in expected_values.items():
            self.assertEqual(servo_id.value, expected_value)
    
    def test_all_servos_present(self):
        """Test that all expected servo IDs are present."""
        servo_values = [servo.value for servo in ServoID]
        
        expected_servos = [
            "headPan", "headTilt",
            "leftGripper", "leftWrist", "leftElbow",
            "leftSholderPitch", "leftSholderYaw", "leftSholderRoll",
            "rightGripper", "rightWrist", "rightElbow", 
            "rightSholderPitch", "rightSholderYaw", "rightSholderRoll"
        ]
        
        for expected_servo in expected_servos:
            self.assertIn(expected_servo, servo_values)


if __name__ == '__main__':
    unittest.main()