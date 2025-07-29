#!/usr/bin/env python3
"""
BonicBot Python Library Setup

Dual Communication Support:
- Serial communication for direct USB/UART connections
- WebSocket communication for remote/network control

Note about GUI dependencies:
- GUI functionality requires tkinter (Python's built-in GUI library)
- tkinter is NOT available via pip - it comes with Python or needs system installation
- Core robot control works without GUI dependencies
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bonicbot",
    version="1.2.0",
    author="Shahir Abdulla",  # Replace with your name
    author_email="shahir@autobonics.com",  # Replace with your email
    description="Python library for controlling BonicBot humanoid robot via serial communication and WebSocket",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Autobonics/bonicbot",  # Replace with your GitHub repo
    project_urls={
        "Bug Tracker": "https://github.com/Autobonics/bonicbot/issues",
        "Documentation": "https://github.com/Autobonics/bonicbot/docs",
        "Source Code": "https://github.com/Autobonics/bonicbot",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        # Note: tkinter is part of Python standard library and cannot be installed via pip
        # GUI functionality requires system installation of tkinter:
        # - Ubuntu/Debian: sudo apt-get install python3-tk
        # - CentOS/RHEL: sudo yum install python3-tkinter
        # - Fedora: sudo dnf install python3-tkinter  
        # - macOS: brew install python-tk (if missing)
        # - Windows: Usually included with Python
        "gui": [],  # Empty - tkinter is not pip-installable
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "examples": [
            # Additional packages that make examples more interesting
            "matplotlib>=3.0",  # For plotting robot movements
            "numpy>=1.19.0",    # For mathematical calculations in examples
        ],
    },
    entry_points={
        "console_scripts": [
            # Note: GUI command will show helpful error if tkinter not available
            "bonicbot-gui=bonicbot.gui:run_servo_controller",
            "bonicbot-test=bonicbot.test_installation:main",  # Installation test
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "robot", "robotics", "servo", "control", "serial", "communication",
        "humanoid", "bonicbot", "hardware", "automation", "websocket", "remote"
    ],
    
    # Custom installation message
    options={
        "egg_info": {
            "tag_build": "",
            "tag_date": False,
        }
    },
)