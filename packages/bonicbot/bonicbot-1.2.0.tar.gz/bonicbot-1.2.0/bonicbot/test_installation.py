#!/usr/bin/env python3
"""
BonicBot Installation Test Module

Test your BonicBot installation:
  python -m bonicbot.test_installation
  OR  
  bonicbot-test
  OR
  from bonicbot.test_installation import main; main()
"""

import sys

def test_core_imports():
    """Test core BonicBot functionality."""
    print("Testing core imports...")
    try:
        from . import (
            BonicBotController, 
            ServoID, 
            CommunicationType,
            create_serial_controller,
            create_websocket_controller
        )
        print("✅ Core imports successful")
        return True
    except ImportError as e:
        print(f"❌ Core import failed: {e}")
        return False

def test_gui_availability():
    """Test if GUI functionality is available."""
    print("\nTesting GUI availability...")
    try:
        from . import is_gui_available
        if is_gui_available():
            from . import BonicBotGUI, run_servo_controller
            print("✅ GUI functionality available")
            return True
        else:
            print("⚠️  GUI functionality not available (tkinter missing)")
            print("   Core robot control still works!")
            return False
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def test_communication_types():
    """Test communication type functionality."""
    print("\nTesting communication types...")
    try:
        from . import CommunicationType, create_serial_controller, create_websocket_controller
        
        # Test enum values
        assert CommunicationType.SERIAL.value == "serial"
        assert CommunicationType.WEBSOCKET.value == "websocket"
        print("  ✅ CommunicationType enum working")
        
        # Test convenience functions exist
        assert callable(create_serial_controller)
        assert callable(create_websocket_controller)
        print("  ✅ Convenience functions available")
        
        print("✅ Communication types working")
        return True
    except Exception as e:
        print(f"❌ Communication types test failed: {e}")
        return False
    
def test_servo_ids():
    """Test ServoID enumeration."""
    print("\nTesting ServoID enumeration...")
    try:
        from . import ServoID
        
        # Test a few key servo IDs
        test_servos = [
            ServoID.HEAD_PAN,
            ServoID.HEAD_TILT,
            ServoID.LEFT_GRIPPER,
            ServoID.RIGHT_GRIPPER
        ]
        
        for servo in test_servos:
            assert hasattr(servo, 'value')
            print(f"  {servo.name}: {servo.value}")
        
        print("✅ ServoID enumeration working")
        return True
    except Exception as e:
        print(f"❌ ServoID test failed: {e}")
        return False

def provide_installation_help():
    """Provide installation help based on platform."""
    print("\n" + "="*50)
    print("INSTALLATION HELP")
    print("="*50)
    
    if sys.platform.startswith('linux'):
        print("For Linux systems:")
        print("  Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  CentOS/RHEL:   sudo yum install python3-tkinter")
        print("  Fedora:        sudo dnf install python3-tkinter")
        print("  Arch:          sudo pacman -S tk")
    
    elif sys.platform == 'darwin':
        print("For macOS:")
        print("  brew install python-tk")
        print("  Or reinstall Python with tkinter support")
    
    elif sys.platform.startswith('win'):
        print("For Windows:")
        print("  Reinstall Python from python.org")
        print("  Make sure to check 'tcl/tk and IDLE' during installation")
    
    print("\nCore functionality (robot control) works without GUI!")

def test():
    """Run all tests."""
    print("BonicBot Installation Test")
    print("=" * 30)
    
    results = []
    
    # Run tests
    results.append(("Core Imports", test_core_imports()))
    results.append(("ServoID Enum", test_servo_ids()))
    results.append(("Communication Types", test_communication_types()))
    results.append(("GUI Availability", test_gui_availability()))
    
    # Summary
    print("\n" + "="*30)
    print("TEST SUMMARY")
    print("="*30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed >= 3:  # Core functionality works (core imports + servo ids + comm types)
        print("\n🎉 BonicBot installation successful!")
        if passed < len(results):
            print("💡 GUI not available, but robot control works fine.")
            provide_installation_help()
    else:
        print("\n🚨 Installation issues detected.")
        provide_installation_help()
    
    return passed == len(results)

if __name__ == "__main__":
    test()