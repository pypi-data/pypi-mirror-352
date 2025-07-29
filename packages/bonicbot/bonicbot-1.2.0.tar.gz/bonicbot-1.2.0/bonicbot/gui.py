#!/usr/bin/env python3
"""
BonicBot GUI Controller

A graphical user interface for controlling BonicBot servos and base motors.
Supports both serial and WebSocket communication.
Designed for Raspberry Pi with tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
from .controller import BonicBotController, ServoID, CommunicationType

class ServoLimits:
    """Servo angle limits based on the C++ code"""
    LIMITS = {
        "rightGripper": (-90.0, 90.0),
        "rightWrist": (-90.0, 90.0),
        "rightElbow": (-90.0, 0.0),
        "rightSholderPitch": (-45.0, 180.0),
        "rightSholderYaw": (-90.0, 90.0),
        "rightSholderRoll": (-3.0, 144.0),
        "leftGripper": (-90.0, 90.0),
        "leftWrist": (-90.0, 90.0),
        "leftElbow": (-90.0, 0.0),
        "leftSholderPitch": (-45.0, 180.0),
        "leftSholderYaw": (-90.0, 90.0),
        "leftSholderRoll": (-3.0, 144.0),
        "headPan": (-90.0, 90.0),
        "headTilt": (-38.0, 45.0)
    }
    
    @classmethod
    def get_limits(cls, servo_id):
        return cls.LIMITS.get(servo_id, (-90.0, 90.0))

class BonicBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BonicBot Controller")
        self.root.geometry("1000x750")
        
        # Controller instance
        self.controller = None
        self.connected = False
        
        # Communication variables
        self.comm_type_var = tk.StringVar(value="serial")
        self.port_var = tk.StringVar(value="/dev/ttyUSB0")
        self.websocket_uri_var = tk.StringVar(value="ws://192.168.1.100:8080/control")
        self.baudrate_var = tk.IntVar(value=115200)
        
        # Create GUI elements
        self.create_widgets()
        
        # Initialize UI state
        self.on_comm_type_change()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection frame
        self.create_connection_frame()
        
        # Individual servo control tab
        self.create_servo_tab()
        
        # Head control tab
        self.create_head_tab()
        
        # Left hand control tab
        self.create_left_hand_tab()
        
        # Right hand control tab
        self.create_right_hand_tab()
        
        # Base control tab
        self.create_base_tab()
        
        # Preset positions tab
        # self.create_presets_tab()
        
    def create_connection_frame(self):
        """Create connection control frame"""
        conn_frame = tk.Frame(self.root)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Communication type selection
        comm_type_frame = tk.LabelFrame(conn_frame, text="Communication Type")
        comm_type_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Radiobutton(comm_type_frame, text="Serial", variable=self.comm_type_var, 
                      value="serial", command=self.on_comm_type_change).pack(side=tk.LEFT)
        tk.Radiobutton(comm_type_frame, text="WebSocket", variable=self.comm_type_var, 
                      value="websocket", command=self.on_comm_type_change).pack(side=tk.LEFT)
        
        # Connection parameters frame
        params_frame = tk.LabelFrame(conn_frame, text="Connection Parameters")
        params_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Serial parameters
        self.serial_frame = tk.Frame(params_frame)
        self.serial_frame.pack(fill=tk.X)
        
        tk.Label(self.serial_frame, text="Port:").pack(side=tk.LEFT)
        self.port_entry = tk.Entry(self.serial_frame, textvariable=self.port_var, width=15)
        self.port_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.serial_frame, text="Baudrate:").pack(side=tk.LEFT, padx=(10, 0))
        self.baudrate_entry = tk.Entry(self.serial_frame, textvariable=self.baudrate_var, width=8)
        self.baudrate_entry.pack(side=tk.LEFT, padx=5)
        
        # WebSocket parameters
        self.websocket_frame = tk.Frame(params_frame)
        self.websocket_frame.pack(fill=tk.X)
        
        tk.Label(self.websocket_frame, text="WebSocket URI:").pack(side=tk.LEFT)
        self.websocket_entry = tk.Entry(self.websocket_frame, textvariable=self.websocket_uri_var, width=35)
        self.websocket_entry.pack(side=tk.LEFT, padx=5)
        
        # Connection control
        control_frame = tk.Frame(conn_frame)
        control_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.connect_btn = tk.Button(control_frame, text="Connect", 
                                    command=self.toggle_connection, bg="green", font=("Arial", 10, "bold"))
        self.connect_btn.pack()
        
        self.status_label = tk.Label(control_frame, text="Disconnected", fg="red", font=("Arial", 10))
        self.status_label.pack()
        
    def on_comm_type_change(self):
        """Handle communication type selection change"""
        comm_type = self.comm_type_var.get()
        
        if comm_type == "serial":
            self.serial_frame.pack(fill=tk.X)
            self.websocket_frame.pack_forget()
        else:  # websocket
            self.websocket_frame.pack(fill=tk.X)
            self.serial_frame.pack_forget()
        
    def create_servo_tab(self):
        """Create individual servo control tab"""
        servo_frame = ttk.Frame(self.notebook)
        self.notebook.add(servo_frame, text="Individual Servos")
        
        # Create scrollable frame
        canvas = tk.Canvas(servo_frame)
        scrollbar = ttk.Scrollbar(servo_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create servo controls
        self.servo_controls = {}
        
        for i, servo in enumerate(ServoID):
            servo_id = servo.value
            min_angle, max_angle = ServoLimits.get_limits(servo_id)
            
            frame = tk.LabelFrame(scrollable_frame, text=servo_id.replace("Sholder", "Shoulder"))
            frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            
            # Angle control
            tk.Label(frame, text="Angle:").grid(row=0, column=0, sticky="w")
            angle_var = tk.DoubleVar(value=0.0)
            angle_scale = tk.Scale(frame, from_=min_angle, to=max_angle, 
                                 variable=angle_var, orient=tk.HORIZONTAL, 
                                 resolution=0.1, length=200)
            angle_scale.grid(row=0, column=1, columnspan=2)
            
            # Speed control
            tk.Label(frame, text="Speed:").grid(row=1, column=0, sticky="w")
            speed_var = tk.IntVar(value=200)
            speed_scale = tk.Scale(frame, from_=1, to=1000, 
                                 variable=speed_var, orient=tk.HORIZONTAL, length=150)
            speed_scale.grid(row=1, column=1)
            
            # Acceleration control
            tk.Label(frame, text="Acc:").grid(row=2, column=0, sticky="w")
            acc_var = tk.IntVar(value=20)
            acc_scale = tk.Scale(frame, from_=1, to=100, 
                               variable=acc_var, orient=tk.HORIZONTAL, length=150)
            acc_scale.grid(row=2, column=1)
            
            # Control button
            btn = tk.Button(frame, text="Move", 
                          command=lambda sid=servo_id, av=angle_var, sv=speed_var, accv=acc_var: 
                          self.control_individual_servo(sid, av.get(), sv.get(), accv.get()))
            btn.grid(row=0, column=3, rowspan=3, padx=5)
            
            self.servo_controls[servo_id] = {
                'angle': angle_var,
                'speed': speed_var,
                'acc': acc_var,
                'button': btn
            }
            
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_head_tab(self):
        """Create head control tab"""
        head_frame = ttk.Frame(self.notebook)
        self.notebook.add(head_frame, text="Head Control")
        
        main_frame = tk.Frame(head_frame)
        main_frame.pack(padx=20, pady=20)
        
        # Pan control
        pan_frame = tk.LabelFrame(main_frame, text="Head Pan")
        pan_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.head_pan_var = tk.DoubleVar(value=0.0)
        tk.Label(pan_frame, text="Angle:").grid(row=0, column=0)
        tk.Scale(pan_frame, from_=-90, to=90, variable=self.head_pan_var,
                orient=tk.HORIZONTAL, resolution=0.1, length=300).grid(row=0, column=1)
        
        self.head_pan_speed_var = tk.IntVar(value=200)
        tk.Label(pan_frame, text="Speed:").grid(row=1, column=0)
        tk.Scale(pan_frame, from_=1, to=1000, variable=self.head_pan_speed_var,
                orient=tk.HORIZONTAL, length=200).grid(row=1, column=1)
        
        # Tilt control
        tilt_frame = tk.LabelFrame(main_frame, text="Head Tilt")
        tilt_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.head_tilt_var = tk.DoubleVar(value=0.0)
        tk.Label(tilt_frame, text="Angle:").grid(row=0, column=0)
        tk.Scale(tilt_frame, from_=-38, to=45, variable=self.head_tilt_var,
                orient=tk.HORIZONTAL, resolution=0.1, length=300).grid(row=0, column=1)
        
        self.head_tilt_speed_var = tk.IntVar(value=200)
        tk.Label(tilt_frame, text="Speed:").grid(row=1, column=0)
        tk.Scale(tilt_frame, from_=1, to=1000, variable=self.head_tilt_speed_var,
                orient=tk.HORIZONTAL, length=200).grid(row=1, column=1)
        
        # Control buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, pady=20)
        
        tk.Button(btn_frame, text="Move Head", command=self.control_head,
                 bg="lightblue", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Center Head", command=self.center_head,
                 bg="lightgreen", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
    def create_left_hand_tab(self):
        """Create left hand control tab"""
        self.create_hand_tab("Left Hand Control", "left")
        
    def create_right_hand_tab(self):
        """Create right hand control tab"""
        self.create_hand_tab("Right Hand Control", "right")
        
    def create_hand_tab(self, tab_name, side):
        """Create hand control tab (left or right)"""
        hand_frame = ttk.Frame(self.notebook)
        self.notebook.add(hand_frame, text=tab_name)
        
        main_frame = tk.Frame(hand_frame)
        main_frame.pack(padx=20, pady=20)
        
        # Define servo limits for this side
        prefix = side.lower()
        servo_configs = [
            ("Gripper", f"{prefix}Gripper", ServoLimits.get_limits(f"{prefix}Gripper")),
            ("Wrist", f"{prefix}Wrist", ServoLimits.get_limits(f"{prefix}Wrist")),
            ("Elbow", f"{prefix}Elbow", ServoLimits.get_limits(f"{prefix}Elbow")),
            ("Shoulder Pitch", f"{prefix}SholderPitch", ServoLimits.get_limits(f"{prefix}SholderPitch")),
            ("Shoulder Yaw", f"{prefix}SholderYaw", ServoLimits.get_limits(f"{prefix}SholderYaw")),
            ("Shoulder Roll", f"{prefix}SholderRoll", ServoLimits.get_limits(f"{prefix}SholderRoll")),
        ]
        
        # Create controls for each servo
        hand_vars = {}
        for i, (display_name, servo_key, (min_angle, max_angle)) in enumerate(servo_configs):
            frame = tk.LabelFrame(main_frame, text=display_name)
            frame.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="ew")
            
            angle_var = tk.DoubleVar(value=0.0)
            tk.Label(frame, text="Angle:").grid(row=0, column=0)
            tk.Scale(frame, from_=min_angle, to=max_angle, variable=angle_var,
                    orient=tk.HORIZONTAL, resolution=0.1, length=250).grid(row=0, column=1)
            
            hand_vars[servo_key] = angle_var
            
        # Store variables for later use
        if side == "left":
            self.left_hand_vars = hand_vars
        else:
            self.right_hand_vars = hand_vars
            
        # Control buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        move_cmd = self.control_left_hand if side == "left" else self.control_right_hand
        reset_cmd = self.reset_left_hand if side == "left" else self.reset_right_hand
        
        tk.Button(btn_frame, text=f"Move {side.title()} Hand", command=move_cmd,
                 bg="lightblue", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text=f"Reset {side.title()} Hand", command=reset_cmd,
                 bg="lightgreen", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
    def create_base_tab(self):
        """Create base motor control tab"""
        base_frame = ttk.Frame(self.notebook)
        self.notebook.add(base_frame, text="Base Control")
        
        main_frame = tk.Frame(base_frame)
        main_frame.pack(padx=20, pady=20)
        
        # Speed control
        speed_frame = tk.LabelFrame(main_frame, text="Movement Speed")
        speed_frame.pack(pady=20)
        
        self.base_speed_var = tk.IntVar(value=100)
        tk.Label(speed_frame, text="Speed:").pack()
        tk.Scale(speed_frame, from_=0, to=255, variable=self.base_speed_var,
                orient=tk.HORIZONTAL, length=300).pack()
        
        # Movement buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        # Top row - Forward
        tk.Button(btn_frame, text="Forward", command=self.move_forward,
                 bg="lightgreen", font=("Arial", 14), width=10).grid(row=0, column=1, padx=5, pady=5)
        
        # Middle row - Left, Stop, Right
        tk.Button(btn_frame, text="Left", command=self.turn_left,
                 bg="lightblue", font=("Arial", 14), width=10).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="STOP", command=self.stop_base,
                 bg="red", fg="white", font=("Arial", 14, "bold"), width=10).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="Right", command=self.turn_right,
                 bg="lightblue", font=("Arial", 14), width=10).grid(row=1, column=2, padx=5, pady=5)
        
        # Bottom row - Backward
        tk.Button(btn_frame, text="Backward", command=self.move_backward,
                 bg="orange", font=("Arial", 14), width=10).grid(row=2, column=1, padx=5, pady=5)
        
        # Manual motor control
        manual_frame = tk.LabelFrame(main_frame, text="Manual Motor Control")
        manual_frame.pack(pady=20)
        
        tk.Label(manual_frame, text="Left Motor:").grid(row=0, column=0)
        self.left_motor_var = tk.IntVar(value=0)
        tk.Scale(manual_frame, from_=-255, to=255, variable=self.left_motor_var,
                orient=tk.HORIZONTAL, length=200).grid(row=0, column=1)
        
        tk.Label(manual_frame, text="Right Motor:").grid(row=1, column=0)
        self.right_motor_var = tk.IntVar(value=0)
        tk.Scale(manual_frame, from_=-255, to=255, variable=self.right_motor_var,
                orient=tk.HORIZONTAL, length=200).grid(row=1, column=1)
        
        tk.Button(manual_frame, text="Apply", command=self.apply_manual_motors,
                 bg="yellow").grid(row=2, column=0, columnspan=2, pady=10)
                 
    def create_presets_tab(self):
        """Create preset positions tab"""
        preset_frame = ttk.Frame(self.notebook)
        self.notebook.add(preset_frame, text="Preset Positions")
        
        main_frame = tk.Frame(preset_frame)
        main_frame.pack(padx=20, pady=20)
        
        # Preset buttons
        preset_buttons_frame = tk.LabelFrame(main_frame, text="Quick Presets")
        preset_buttons_frame.pack(pady=10, fill=tk.X)
        
        presets = [
            ("Home Position", self.goto_home),
            ("Attention", self.goto_attention),
            ("Wave Hello", self.wave_hello),
            ("Arms Up", self.arms_up),
            ("Look Around", self.look_around)
        ]
        
        for i, (name, command) in enumerate(presets):
            tk.Button(preset_buttons_frame, text=name, command=command,
                     bg="lightcyan", font=("Arial", 10), width=15).grid(
                     row=i//3, column=i%3, padx=5, pady=5)
        
        # Save/Load custom positions
        custom_frame = tk.LabelFrame(main_frame, text="Custom Positions")
        custom_frame.pack(pady=20, fill=tk.X)
        
        tk.Button(custom_frame, text="Save Current Position", 
                 command=self.save_position, bg="lightgreen").pack(side=tk.LEFT, padx=5)
        tk.Button(custom_frame, text="Load Position", 
                 command=self.load_position, bg="lightblue").pack(side=tk.LEFT, padx=5)
        
    # Connection methods
    def toggle_connection(self):
        """Toggle robot connection"""
        if not self.connected:
            self.connect_robot()
        else:
            self.disconnect_robot()
            
    def connect_robot(self):
        """Connect to robot"""
        try:
            comm_type = self.comm_type_var.get()
            
            if comm_type == "serial":
                port = self.port_var.get().strip()
                if not port:
                    messagebox.showerror("Error", "Please enter a serial port")
                    return
                
                baudrate = self.baudrate_var.get()
                self.controller = BonicBotController(
                    comm_type=CommunicationType.SERIAL,
                    port=port,
                    baudrate=baudrate
                )
                connection_info = f"Serial: {port} @ {baudrate}"
                
            elif comm_type == "websocket":
                websocket_uri = self.websocket_uri_var.get().strip()
                if not websocket_uri:
                    messagebox.showerror("Error", "Please enter a WebSocket URI")
                    return
                
                self.controller = BonicBotController(
                    comm_type=CommunicationType.WEBSOCKET,
                    websocket_uri=websocket_uri
                )
                connection_info = f"WebSocket: {websocket_uri}"
            
            # Check if connection is successful
            if self.controller.is_connected():
                self.connected = True
                self.connect_btn.config(text="Disconnect", bg="red")
                self.status_label.config(text="Connected", fg="green")
                messagebox.showinfo("Success", f"Connected via {connection_info}")
            else:
                raise ConnectionError("Failed to establish connection")
                
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            if self.controller:
                try:
                    self.controller.close()
                except:
                    pass
                self.controller = None
            
    def disconnect_robot(self):
        """Disconnect from robot"""
        try:
            if self.controller:
                self.controller.close()
                self.controller = None
                
            self.connected = False
            self.connect_btn.config(text="Connect", bg="green")
            self.status_label.config(text="Disconnected", fg="red")
            messagebox.showinfo("Info", "Disconnected from robot")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during disconnect: {str(e)}")
            
    # Control methods
    def control_individual_servo(self, servo_id, angle, speed, acc):
        """Control individual servo"""
        if not self.connected or not self.controller:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
            
        try:
            self.controller.control_servo(servo_id, angle, speed, acc)
        except Exception as e:
            messagebox.showerror("Error", f"Servo control error: {str(e)}")
            
    def control_head(self):
        """Control head movement"""
        if not self.connected or not self.controller:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
            
        try:
            pan_angle = self.head_pan_var.get()
            tilt_angle = self.head_tilt_var.get()
            pan_speed = self.head_pan_speed_var.get()
            tilt_speed = self.head_tilt_speed_var.get()
            
            self.controller.control_head(pan_angle, tilt_angle, pan_speed, 20, tilt_speed, 50)
        except Exception as e:
            messagebox.showerror("Error", f"Head control error: {str(e)}")
            
    def center_head(self):
        """Center head position"""
        self.head_pan_var.set(0.0)
        self.head_tilt_var.set(0.0)
        self.control_head()
        
    def control_left_hand(self):
        """Control left hand movement"""
        if not self.connected or not self.controller:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
            
        try:
            self.controller.control_left_hand(
                gripper_angle=self.left_hand_vars['leftGripper'].get(),
                wrist_angle=self.left_hand_vars['leftWrist'].get(),
                elbow_angle=self.left_hand_vars['leftElbow'].get(),
                shoulder_pitch=self.left_hand_vars['leftSholderPitch'].get(),
                shoulder_yaw=self.left_hand_vars['leftSholderYaw'].get(),
                shoulder_roll=self.left_hand_vars['leftSholderRoll'].get()
            )
        except Exception as e:
            messagebox.showerror("Error", f"Left hand control error: {str(e)}")
            
    def control_right_hand(self):
        """Control right hand movement"""
        if not self.connected or not self.controller:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
            
        try:
            self.controller.control_right_hand(
                gripper_angle=self.right_hand_vars['rightGripper'].get(),
                wrist_angle=self.right_hand_vars['rightWrist'].get(),
                elbow_angle=self.right_hand_vars['rightElbow'].get(),
                shoulder_pitch=self.right_hand_vars['rightSholderPitch'].get(),
                shoulder_yaw=self.right_hand_vars['rightSholderYaw'].get(),
                shoulder_roll=self.right_hand_vars['rightSholderRoll'].get()
            )
        except Exception as e:
            messagebox.showerror("Error", f"Right hand control error: {str(e)}")
            
    def reset_left_hand(self):
        """Reset left hand to neutral position"""
        for var in self.left_hand_vars.values():
            var.set(0.0)
        self.control_left_hand()
        
    def reset_right_hand(self):
        """Reset right hand to neutral position"""
        for var in self.right_hand_vars.values():
            var.set(0.0)
        self.control_right_hand()
        
    # Base movement methods
    def move_forward(self):
        """Move robot forward"""
        if not self.connected or not self.controller:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
        speed = self.base_speed_var.get()
        self.controller.move_forward(speed)
        
    def move_backward(self):
        """Move robot backward"""
        if not self.connected or not self.controller:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
        speed = self.base_speed_var.get()
        self.controller.move_backward(speed)
        
    def turn_left(self):
        """Turn robot left"""
        if not self.connected or not self.controller:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
        speed = self.base_speed_var.get()
        self.controller.turn_left(speed)
        
    def turn_right(self):
        """Turn robot right"""
        if not self.connected or not self.controller:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
        speed = self.base_speed_var.get()
        self.controller.turn_right(speed)
        
    def stop_base(self):
        """Stop robot movement"""
        if not self.connected or not self.controller:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
        self.controller.stop()
        
    def apply_manual_motors(self):
        """Apply manual motor speeds"""
        if not self.connected or not self.controller:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
        left_speed = self.left_motor_var.get()
        right_speed = self.right_motor_var.get()
        self.controller.control_base(left_speed, right_speed)
        
    # Preset position methods
    def goto_home(self):
        """Go to home position"""
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
            
        # Reset all servos to neutral positions
        self.head_pan_var.set(0.0)
        self.head_tilt_var.set(0.0)
        
        for var in self.left_hand_vars.values():
            var.set(0.0)
        for var in self.right_hand_vars.values():
            var.set(0.0)
            
        # Apply positions
        self.control_head()
        time.sleep(0.5)
        self.control_left_hand()
        time.sleep(0.5)
        self.control_right_hand()
        
    def goto_attention(self):
        """Attention pose"""
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
            
        # Head looking forward
        self.head_pan_var.set(0.0)
        self.head_tilt_var.set(10.0)
        
        # Arms at sides
        self.left_hand_vars['leftSholderPitch'].set(0.0)
        self.left_hand_vars['leftSholderRoll'].set(10.0)
        self.right_hand_vars['rightSholderPitch'].set(0.0)
        self.right_hand_vars['rightSholderRoll'].set(-10.0)
        
        self.control_head()
        self.control_left_hand()
        self.control_right_hand()
        
    def wave_hello(self):
        """Wave hello gesture"""
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
            
        def wave_sequence():
            # Raise right arm
            self.right_hand_vars['rightSholderPitch'].set(-45.0)
            self.right_hand_vars['rightElbow'].set(45.0)
            self.control_right_hand()
            time.sleep(1)
            
            # Wave motion
            for _ in range(3):
                self.right_hand_vars['rightWrist'].set(30.0)
                self.control_right_hand()
                time.sleep(0.5)
                self.right_hand_vars['rightWrist'].set(-30.0)
                self.control_right_hand()
                time.sleep(0.5)
            
            # Return to neutral
            self.reset_right_hand()
            
        threading.Thread(target=wave_sequence, daemon=True).start()
        
    def arms_up(self):
        """Raise both arms up"""
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
            
        # Raise both arms
        self.left_hand_vars['leftSholderPitch'].set(90.0)
        self.right_hand_vars['rightSholderPitch'].set(-90.0)
        
        self.control_left_hand()
        self.control_right_hand()
        
    def look_around(self):
        """Look around sequence"""
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to robot")
            return
            
        def look_sequence():
            positions = [(-60, 0), (60, 0), (0, 20), (0, -20), (0, 0)]
            for pan, tilt in positions:
                self.head_pan_var.set(pan)
                self.head_tilt_var.set(tilt)
                self.control_head()
                time.sleep(1)
                
        threading.Thread(target=look_sequence, daemon=True).start()
        
    def save_position(self):
        """Save current position to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                position_data = {
                    'head': {
                        'pan': self.head_pan_var.get(),
                        'tilt': self.head_tilt_var.get()
                    },
                    'left_hand': {k: v.get() for k, v in self.left_hand_vars.items()},
                    'right_hand': {k: v.get() for k, v in self.right_hand_vars.items()}
                }
                
                with open(filename, 'w') as f:
                    json.dump(position_data, f, indent=2)
                    
                messagebox.showinfo("Success", f"Position saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save position: {str(e)}")
            
    def load_position(self):
        """Load position from file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'r') as f:
                    position_data = json.load(f)
                
                # Load head position
                if 'head' in position_data:
                    self.head_pan_var.set(position_data['head']['pan'])
                    self.head_tilt_var.set(position_data['head']['tilt'])
                
                # Load hand positions
                if 'left_hand' in position_data:
                    for k, v in position_data['left_hand'].items():
                        if k in self.left_hand_vars:
                            self.left_hand_vars[k].set(v)
                            
                if 'right_hand' in position_data:
                    for k, v in position_data['right_hand'].items():
                        if k in self.right_hand_vars:
                            self.right_hand_vars[k].set(v)
                
                messagebox.showinfo("Success", f"Position loaded from {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load position: {str(e)}")

def run_servo_controller():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = BonicBotGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.connected and app.controller:
            app.controller.close()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    run_servo_controller()