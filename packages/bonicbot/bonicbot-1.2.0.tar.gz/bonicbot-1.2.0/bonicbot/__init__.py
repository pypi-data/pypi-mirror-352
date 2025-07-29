"""
BonicBot Python Library

A comprehensive Python library for controlling BonicBot humanoid robots 
via serial communication.

Main Components:
- BonicBotController: Core controller class for robot communication
- BonicBotGUI: Graphical user interface for robot control (optional)
- ServoID: Enumeration of available servo identifiers

Example:
    Basic usage:
    
    >>> from bonicbot import BonicBotController
    >>> bot = BonicBotController('/dev/ttyUSB0')
    >>> bot.control_head(pan_angle=45.0)
    >>> bot.close()
    
    With context manager:
    
    >>> with BonicBotController('/dev/ttyUSB0') as bot:
    ...     bot.move_forward(speed=100)
"""

__version__ = "1.2.0"
__author__ = "Shahir Abdulla"
__email__ = "shahir@autobonics.com"
__license__ = "MIT"
__description__ = "Python library for controlling BonicBot humanoid robot via serial communication"

from .controller import (
    BonicBotController, 
    ServoID, 
    CommunicationType,
    create_serial_controller,
    create_websocket_controller
)

# Try to import GUI components (optional)
try:
    from .gui import BonicBotGUI, run_servo_controller
    _GUI_AVAILABLE = True
    __all__ = [
        "BonicBotController",
        "ServoID", 
        "CommunicationType",
        "create_serial_controller",
        "create_websocket_controller",
        "BonicBotGUI",
        "run_servo_controller",
        "is_gui_available",
    ]
except ImportError as e:
    # GUI not available (likely missing tkinter)
    _GUI_AVAILABLE = False
    __all__ = [
        "BonicBotController",
        "ServoID", 
        "CommunicationType",
        "create_serial_controller",
        "create_websocket_controller",
        "is_gui_available",
    ]
    
    # Create dummy functions that provide helpful error messages
    def BonicBotGUI(*args, **kwargs):
        raise ImportError(
            "GUI functionality requires tkinter. Install it with:\n"
            "  Ubuntu/Debian: sudo apt-get install python3-tk\n"
            "  CentOS/RHEL: sudo yum install python3-tkinter\n"
            "  Fedora: sudo dnf install python3-tkinter\n"
            "  macOS: brew install python-tk\n"
            "  Windows: Reinstall Python with tkinter support"
        )
    
    def run_servo_controller(*args, **kwargs):
        raise ImportError(
            "GUI functionality requires tkinter. Install it with:\n"
            "  Ubuntu/Debian: sudo apt-get install python3-tk\n"
            "  CentOS/RHEL: sudo yum install python3-tkinter\n"
            "  Fedora: sudo dnf install python3-tkinter\n"
            "  macOS: brew install python-tk\n"
            "  Windows: Reinstall Python with tkinter support"
        )

def is_gui_available():
    """Check if GUI functionality is available."""
    return _GUI_AVAILABLE