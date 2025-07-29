# BonicBot API Documentation

## Overview

The BonicBot library provides a comprehensive Python interface for controlling BonicBot humanoid robots via **serial communication** or **WebSocket**. The main components are:

- `BonicBotController`: Core controller class supporting both communication protocols
- `CommunicationType`: Enumeration for communication method selection
- `ServoID`: Enumeration of available servos
- `BonicBotGUI`: Graphical user interface
- `create_serial_controller`: Convenience function for serial connections
- `create_websocket_controller`: Convenience function for WebSocket connections

## BonicBotController Class

### Constructor

```python
BonicBotController(
    comm_type: Union[str, CommunicationType],
    port: Optional[str] = None,
    baudrate: int = 115200,
    timeout: float = 1.0,
    websocket_uri: Optional[str] = None
)
```

**Parameters:**
- `comm_type` (str or CommunicationType): 'serial' or 'websocket'
- `port` (str): Serial port name (required for serial) 
- `baudrate` (int): Serial baud rate (default: 115200)
- `timeout` (float): Communication timeout (default: 1.0)
- `websocket_uri` (str): WebSocket URI (required for WebSocket)

**Examples:**
```python
# Serial communication
bot = BonicBotController('serial', port='/dev/ttyUSB0', baudrate=115200)
bot = BonicBotController(CommunicationType.SERIAL, port='COM3')

# WebSocket communication  
bot = BonicBotController('websocket', websocket_uri='ws://192.168.1.100:8080/control')
bot = BonicBotController(CommunicationType.WEBSOCKET, websocket_uri='ws://robot.local:8080/control')
```

**Raises:**
- `ValueError`: Invalid communication type or missing required parameters
- `ConnectionError`: Unable to establish connection

## Convenience Functions

### create_serial_controller()

```python
create_serial_controller(port: str, baudrate: int = 115200) -> BonicBotController
```

Create a BonicBot controller for serial communication.

**Parameters:**
- `port` (str): Serial port name
- `baudrate` (int): Serial baud rate

**Returns:**
- `BonicBotController`: Controller instance configured for serial

**Example:**
```python
bot = create_serial_controller('/dev/ttyUSB0')
```

### create_websocket_controller()

```python
create_websocket_controller(websocket_uri: str, timeout: float = 1.0) -> BonicBotController
```

Create a BonicBot controller for WebSocket communication.

**Parameters:**
- `websocket_uri` (str): WebSocket URI
- `timeout` (float): Connection timeout

**Returns:**
- `BonicBotController`: Controller instance configured for WebSocket

**Example:**
```python
bot = create_websocket_controller('ws://192.168.1.100:8080/control')
```

## CommunicationType Enumeration

```python
class CommunicationType(Enum):
    SERIAL = "serial"
    WEBSOCKET = "websocket"
```

Used to specify the communication protocol.

### Individual Servo Control

#### control_servo()

```python
control_servo(servo_id: Union[str, ServoID], angle: float, speed: int = 200, acc: int = 20)
```

Controls an individual servo motor.

**Parameters:**
- `servo_id`: Servo identifier (string or ServoID enum)
- `angle`: Target angle in degrees
- `speed`: Movement speed (1-1000)
- `acc`: Acceleration value (1-100)

**Raises:**
- `ValueError`: If servo_id is invalid
- `ConnectionError`: If not connected to robot

**Example:**
```python
bot.control_servo('headPan', angle=45.0, speed=200, acc=20)
bot.control_servo(ServoID.HEAD_TILT, angle=-10.0, speed=150)
```

### Group Control Methods

#### control_head()

```python
control_head(pan_angle: float = 0.0, tilt_angle: float = 0.0,
            pan_speed: int = 200, pan_acc: int = 20,
            tilt_speed: int = 200, tilt_acc: int = 50,
            mode: str = "None")
```

Controls head movement (pan and tilt).

**Parameters:**
- `pan_angle`: Head pan angle (-90° to 90°)
- `tilt_angle`: Head tilt angle (-38° to 45°)
- `pan_speed`: Pan movement speed
- `pan_acc`: Pan acceleration
- `tilt_speed`: Tilt movement speed
- `tilt_acc`: Tilt acceleration
- `mode`: Head control mode

#### control_left_hand()

```python
control_left_hand(gripper_angle: float = 0.0, wrist_angle: float = 0.0,
                 elbow_angle: float = 0.0, shoulder_pitch: float = 0.0,
                 shoulder_yaw: float = 0.0, shoulder_roll: float = 0.0,
                 gripper_speed: int = 200, wrist_speed: int = 800,
                 elbow_speed: int = 200, shoulder_pitch_speed: int = 200,
                 shoulder_yaw_speed: int = 750, shoulder_roll_speed: int = 200,
                 gripper_acc: int = 20, wrist_acc: int = 20,
                 elbow_acc: int = 20, shoulder_pitch_acc: int = 20,
                 shoulder_yaw_acc: int = 80, shoulder_roll_acc: int = 20)
```

Controls all left arm servos simultaneously.

**Angle Ranges:**
- `gripper_angle`: -90° to 90°
- `wrist_angle`: -90° to 90°
- `elbow_angle`: -90° to 0°
- `shoulder_pitch`: -45° to 180°
- `shoulder_yaw`: -90° to 90°
- `shoulder_roll`: -3° to 144°

#### control_right_hand()

```python
control_right_hand(gripper_angle: float = 0.0, wrist_angle: float = 0.0,
                  elbow_angle: float = 0.0, shoulder_pitch: float = 0.0,
                  shoulder_yaw: float = 0.0, shoulder_roll: float = 0.0,
                  gripper_speed: int = 200, wrist_speed: int = 750,
                  elbow_speed: int = 200, shoulder_pitch_speed: int = 200,
                  shoulder_yaw_speed: int = 200, shoulder_roll_speed: int = 200,
                  gripper_acc: int = 20, wrist_acc: int = 20,
                  elbow_acc: int = 20, shoulder_pitch_acc: int = 20,
                  shoulder_yaw_acc: int = 20, shoulder_roll_acc: int = 20)
```

Controls all right arm servos simultaneously.

**Angle Ranges:**
- `gripper_angle`: -90° to 90°
- `wrist_angle`: -90° to 90°
- `elbow_angle`: -90° to 0°
- `shoulder_pitch`: -45° to 180°
- `shoulder_yaw`: -90° to 90°
- `shoulder_roll`: -3° to 144°

### Base Motor Control

#### control_base()

```python
control_base(left_motor_speed: int = 0, right_motor_speed: int = 0)
```

Controls base motors directly.

**Parameters:**
- `left_motor_speed`: Left motor speed (-255 to 255)
- `right_motor_speed`: Right motor speed (-255 to 255)

#### Movement Methods

```python
move_forward(speed: int = 100)
move_backward(speed: int = 100)
turn_left(speed: int = 100)
turn_right(speed: int = 100)
stop()
```

Convenience methods for common movements.

**Parameters:**
- `speed`: Movement speed (0-255)

### Connection Management

#### close()

```python
close()
```

Closes the serial connection.

#### Context Manager Support

The controller supports context manager protocol:

```python
with BonicBotController('/dev/ttyUSB0') as bot:
    bot.control_head(pan_angle=45)
    # Connection automatically closed
```

## ServoID Enumeration

Available servo identifiers:

### Head Servos
- `ServoID.HEAD_PAN` / "headPan"
- `ServoID.HEAD_TILT` / "headTilt"

### Left Arm Servos
- `ServoID.LEFT_GRIPPER` / "leftGripper"
- `ServoID.LEFT_WRIST` / "leftWrist"
- `ServoID.LEFT_ELBOW` / "leftElbow"
- `ServoID.LEFT_SHOULDER_PITCH` / "leftSholderPitch"
- `ServoID.LEFT_SHOULDER_YAW` / "leftSholderYaw"
- `ServoID.LEFT_SHOULDER_ROLL` / "leftSholderRoll"

### Right Arm Servos
- `ServoID.RIGHT_GRIPPER` / "rightGripper"
- `ServoID.RIGHT_WRIST` / "rightWrist"
- `ServoID.RIGHT_ELBOW` / "rightElbow"
- `ServoID.RIGHT_SHOULDER_PITCH` / "rightSholderPitch"
- `ServoID.RIGHT_SHOULDER_YAW` / "rightSholderYaw"
- `ServoID.RIGHT_SHOULDER_ROLL` / "rightSholderRoll"

## Command Structure

The library sends JSON commands via serial communication:

```json
{
    "commandType": "command",
    "dataType": "servo|head|leftHand|rightHand|base",
    "payload": {
        // Command-specific data
    },
    "interval": 0
}
```

### Servo Command Example

```json
{
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
```

### Head Command Example

```json
{
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
            "angle": -10.0,
            "speed": 200,
            "acc": 50
        }
    },
    "interval": 0
}
```

## Error Handling

The library raises specific exceptions:

- `ConnectionError`: Serial connection issues
- `ValueError`: Invalid parameters or servo IDs
- `RuntimeError`: Command transmission failures

Always use try-catch blocks for robust error handling:

```python
try:
    with BonicBotController('/dev/ttyUSB0') as bot:
        bot.control_servo('headPan', 45.0)
except ConnectionError as e:
    print(f"Connection failed: {e}")
except ValueError as e:
    print(f"Invalid parameter: {e}")
```

## Best Practices

1. **Use Context Managers**: Always use `with` statements for automatic cleanup
2. **Handle Exceptions**: Wrap robot operations in try-catch blocks
3. **Validate Angles**: Ensure angles are within valid ranges for each servo
4. **Gradual Movements**: Use reasonable speeds and accelerations
5. **Test Safely**: Start with small movements and low speeds
6. **Emergency Stop**: Always have a way to quickly stop the robot

## GUI Interface

### BonicBotGUI Class

```python
class BonicBotGUI:
    def __init__(self, root)
```

### Running the GUI

```python
from bonicbot.gui import run_servo_controller
run_servo_controller()
```

Or from command line:
```bash
bonicbot-gui
```

The GUI provides:
- Individual servo control with sliders
- Group control for head, hands, and base
- Preset positions and custom position saving
- Real-time connection status
- Safety controls and limits