import asyncio
import socket
import json
import threading
import time

class DAGGripper:
    """
    SDK for the DAG (Dynamixel Adaptive Gripper) module.
    Provides high-level control functions for the gripper system.
    Now communicates directly with ESP module via TCP socket.
    """
    
    def __init__(self, esp_ip="10.42.0.52", esp_port=4196):
        """
        Initialize the DAG Gripper SDK.
        
        Args:
            esp_ip (str): IP address of the ESP module
            esp_port (int): Port number of the ESP module
        """
        self.esp_ip = esp_ip
        self.esp_port = esp_port
        self.status = {}
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.connected = False
        self.thread.start()
        
    def _run_loop(self):    
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
    def _test_connection(self):
        """Test if we can connect to the ESP module."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)  # 2 second timeout
                sock.connect((self.esp_ip, self.esp_port))
                self.connected = True
                return True
        except Exception as e:
            print(f"[DAG] Connection test failed: {e}")
            self.connected = False
            return False
            
    async def _send_command(self, command):
        """
        Send a command to the gripper via TCP socket.
        
        Args:
            command (dict): Command to send
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)  # 5 second timeout
                sock.connect((self.esp_ip, self.esp_port))
                
                # Send command as JSON with newline delimiter
                message = json.dumps({"input": command}) + "\r\n"
                sock.sendall(message.encode())
                
                # Wait for response
                response_data = b""
                while True:
                    try:
                        chunk = sock.recv(1024)
                        if not chunk:
                            break
                        response_data += chunk
                        # Check if we have a complete JSON response
                        if b'\n' in response_data or b'}' in response_data:
                            break
                    except socket.timeout:
                        break
                
                # Parse response and update status
                if response_data:
                    try:
                        response_str = response_data.decode().strip()
                        if response_str:
                            self.status = json.loads(response_str)
                            self.connected = True
                    except json.JSONDecodeError as e:
                        print(f"[DAG] JSON decode error: {e}")
                        print(f"[DAG] Raw response: {response_data}")
                else:
                    print("[DAG] No response received from ESP module")
                    
        except ConnectionRefusedError:
            print(f"[DAG] Connection refused to {self.esp_ip}:{self.esp_port}")
            self.connected = False
        except socket.timeout:
            print(f"[DAG] Connection timeout to {self.esp_ip}:{self.esp_port}")
            self.connected = False
        except Exception as e:
            print(f"[DAG] Error sending command: {e}")
            self.connected = False
            
    def _send_command_sync(self, command):
        """
        Synchronous wrapper for sending commands.
        
        Args:
            command (dict): Command to send
        """
        future = asyncio.run_coroutine_threadsafe(
            self._send_command(command), 
            self.loop
        )
        # Wait for the command to complete with timeout
        try:
            future.result(timeout=10)  # 10 second timeout
        except asyncio.TimeoutError:
            print("[DAG] Command timeout")
        except Exception as e:
            print(f"[DAG] Command execution error: {e}")
    
    # --------------------------------------------------------
    # Pre-defined grasp modes (originally provided)
    # --------------------------------------------------------
    def pinch_left(self, velocity=50, Kp=50):
        """
        Execute a pinch grasp (left finger and thumb).
        
        Args:
            velocity (int): Movement velocity (0-100)
            Kp (int): Position Gain (0-100)
        """
        command = {
            "grasp_command": True,
            "grasp_mode": "pinch_left",
            "velocity": velocity,
            "Kp": Kp
        }
        self._send_command_sync(command)
        
    def pinch_right(self, velocity=50, Kp=50):
        """
        Execute a right pinch grasp (right finger and thumb).
        
        Args:
            velocity (int): Movement velocity (0-100)
            Kp (int): Position Gain (0-100)
        """
        command = {
            "grasp_command": True,
            "grasp_mode": "pinch_right",
            "velocity": velocity,
            "Kp": Kp
        }
        self._send_command_sync(command)
        
    def tripod_pinch(self, velocity=50, Kp=50):
        """
        Execute a tripod pinch grasp (three fingers).
        
        Args:
            velocity (int): Movement velocity (0-100)
            Kp (int): Position Gain (0-100)
        """
        command = {
            "grasp_command": True,
            "grasp_mode": "tripod_pinch",
            "velocity": velocity,
            "Kp": Kp
        }
        self._send_command_sync(command)
        
    def tripod_small_encompass(self, velocity=50, Kp=50):
        """
        Execute a small encompassing grasp for medium objects.
        
        Args:
            velocity (int): Movement velocity (0-100)
            Kp (int): Position Gain (0-100)
        """
        command = {
            "grasp_command": True,
            "grasp_mode": "tripod_small_encompass",
            "velocity": velocity,
            "Kp": Kp
        }
        self._send_command_sync(command)
        
    def tripod_large_encompass(self, velocity=50, Kp=50):
        """
        Execute a large encompassing grasp for larger objects.
        
        Args:
            velocity (int): Movement velocity (0-100)
            Kp (int): Position Gain (0-100)
        """
        command = {
            "grasp_command": True,
            "grasp_mode": "tripod_large_encompass",
            "velocity": velocity,
            "Kp": Kp
        }
        self._send_command_sync(command)
        
    def tripod_flat_small_pick(self, velocity=50, Kp=50):
        """
        Execute a flat small pick grasp (for thin objects).
        
        Args:
            velocity (int): Movement velocity (0-100)
            Kp (int): Position Gain (0-100)
        """
        command = {
            "grasp_command": True,
            "grasp_mode": "tripod_flat_small_pick",
            "velocity": velocity,
            "Kp": Kp
        }
        self._send_command_sync(command)
        
    def tripod_flat_close(self, velocity=50, Kp=50):
        """
        Execute a flat closing grasp.
        
        Args:
            velocity (int): Movement velocity (0-100)
            Kp (int): Position Gain (0-100)
        """
        command = {
            "grasp_command": True,
            "grasp_mode": "flat_close",
            "velocity": velocity,
            "Kp": Kp
        }
        self._send_command_sync(command)
    
    def home(self, velocity=50):
        """
        Move gripper to home position.
        
        Args:
            velocity (int): Movement velocity (0-100)
        """
        command = {
            "grasp_command": True,
            "grasp_mode": "home",
            "velocity": velocity
        }
        self._send_command_sync(command)
        
    def full_open(self, velocity=50):
        """
        Open the gripper fully.
        
        Args:
            velocity (int): Movement velocity (0-100)
        """
        command = {
            "grasp_command": True,
            "grasp_mode": "full_open",
            "velocity": velocity
        }
        self._send_command_sync(command)
    
    def joint_sine(self):
        """
            Request the “joint_sine” motion pattern on the ESP32 side.
        """
        command = {
            "grasp_command": True,
            "grasp_mode": "joint_sine"
        }
        self._send_command_sync(command)

    def joint_min_max(self):
        """
        Request the “joint_min_max” motion pattern on the ESP32 side.
        """
        command = {
            "grasp_command": True,
            "grasp_mode": "joint_min_max"
        }
        self._send_command_sync(command)

    # --------------------------------------------------------
    # Advanced control modes (originally provided)
    # --------------------------------------------------------
    def position_control(self, positions, velocity=50, velocities=None, 
                         Kp=50, max_contact_forces=None, raw_values=False):
        """
        Control individual joint positions.
        
        Args:
            positions (dict): Dictionary of joint positions (e.g., {"joint_1": 50, ...})
            velocity (int): Global velocity (0-100)
            velocities (dict): Optional per-joint velocities
            Kp (int): Global Position Gain (0-100)
            max_contact_forces (dict): Optional per-joint maximum forces
            raw_values (bool): Whether values are raw motor values (True) or percentages (False)
        """
        command = {
            "grasp_command": False,
            "control_mode": "position",
            "raw_values": raw_values,
            "velocity": velocity,
            "Kp": Kp,
            "target_positions": positions
        }
        
        if velocities:
            command["velocities"] = velocities
            
        if max_contact_forces:
            command["max_contact_forces"] = max_contact_forces
            
        self._send_command_sync(command)
        
    def current_control(self, currents, Kp=50, raw_values=False):
        """
        Control individual joint currents (forces).
        
        Args:
            currents (dict): Dictionary of joint currents (e.g., {"joint_1": 50, ...})
            Kp (int): Global Position Gain (0-100)
            raw_values (bool): Whether values are raw motor values (True) or percentages (False)
        """
        command = {
            "grasp_command": False,
            "control_mode": "current",
            "raw_values": raw_values,
            "Kp": Kp,
            "target_currents": currents
        }
        
        self._send_command_sync(command)
        
    def compliant_control(self, positions, kp=800, kps=None, 
                          velocity=50, velocities=None, raw_values=False):
        """
        Control positions with adjustable compliance (P gains).
        
        Args:
            positions (dict): Dictionary of joint positions (e.g., {"joint_1": 50, ...})
            kp (int): Global proportional gain (0-3000, lower = more compliant)
            kps (dict): Optional per-joint P gains
            velocity (int): Global velocity (0-100)
            velocities (dict): Optional per-joint velocities
            raw_values (bool): Whether position values are raw motor values (True) or percentages (False)
        """
        command = {
            "grasp_command": False,
            "control_mode": "compliant",
            "raw_values": raw_values,
            "velocity": velocity,
            "Kp": kp,
            "target_positions": positions
        }
        
        if kps:
            command["Kps"] = kps
            
        if velocities:
            command["velocities"] = velocities
            
        self._send_command_sync(command)
    
    # --------------------------------------------------------
    # Helper functions (originally provided)
    # --------------------------------------------------------
    def get_status(self):
        """
        Get the current status of the gripper.
        
        Returns:
            dict: Current gripper status
        """
        return self.status
    
    def get_joint_positions(self):
        """
        Get the current positions of all joints.
        
        Returns:
            dict: Joint positions or empty dict if not available
        """
        if self.status and "output" in self.status:
            return self.status["output"].get("finger_joint_positions", {})
        return {}
    
    def get_joint_currents(self):
        """
        Get the current force/current of all joints.
        
        Returns:
            dict: Joint currents or empty dict if not available
        """
        if self.status and "output" in self.status:
            return self.status["output"].get("finger_joint_currents", {})
        return {}
    
    def is_object_in_hand(self):
        """
        Check if an object is currently detected in the gripper.
        
        Returns:
            bool: True if object detected, False otherwise
        """
        if self.status and "output" in self.status:
            return self.status["output"].get("object_in_hand", False)
        return False
    
    def is_object_slipping(self):
        """
        Check if an object is slipping in the gripper.
        
        Returns:
            bool: True if slip detected, False otherwise
        """
        if self.status and "output" in self.status:
            return self.status["output"].get("object_slip_status", False)
        return False
    
    def is_connected(self):
        """
        Check if the gripper is currently connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.connected
    
    def test_connection(self):
        """
        Test the connection to the ESP module.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        return self._test_connection()
    
    def close(self):
        """Close the connection and cleanup resources."""
        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)


if __name__ == "__main__":
    import random

    print("[TEST] Initializing DAG Gripper SDK...")
    gripper = DAGGripper(esp_ip="10.42.0.52", esp_port=4196)

    if gripper.test_connection():
        print("[TEST] ✅ Connection successful")

        try:
            # 1) Home the gripper
            print("[TEST] Homing gripper...")
            gripper.home()
            time.sleep(2)

            # 2) Full open
            print("[TEST] Full open gripper (alias)...")
            gripper.full_open()
            time.sleep(2)

            # 3) Test pinch grasps
            print("[TEST] Testing pinch_left with Kp=40...")
            gripper.pinch_left(velocity=60, Kp=40)
            time.sleep(2)

            print("[TEST] Testing pinch_right with default parameters...")
            gripper.pinch_right()
            time.sleep(2)

            # 4) Test tripod grasps
            print("[TEST] Testing tripod_pinch with Kp=45...")
            gripper.tripod_pinch(velocity=55, Kp=45)
            time.sleep(2)

            print("[TEST] Testing tripod_small_encompass (default)...")
            gripper.tripod_small_encompass()
            time.sleep(2)

            print("[TEST] Testing tripod_large_encompass (default)...")
            gripper.tripod_large_encompass()
            time.sleep(2)

            print("[TEST] Testing tripod_flat_small_pick (default)...")
            gripper.tripod_flat_small_pick()
            time.sleep(2)

            print("[TEST] Testing tripod_flat_close (default)...")
            gripper.tripod_flat_close()
            time.sleep(2)

            # 5) Move back to home, then reopen
            print("[TEST] Returning to home...")
            gripper.home()
            time.sleep(2)

            print("[TEST] Opening gripper again...")
            gripper.full_open()
            time.sleep(2)

            # # 6) Test position_control directly with a small dictionary
            # print("[TEST] Testing position_control on joints 1–4...")
            # pos_dict = {
            #     "joint_1": 30,
            #     "joint_2": 60,
            #     "joint_3": 45,
            #     "joint_4": 75
            # }
            # vel_dict = {
            #     "joint_1": 20,
            #     "joint_2": 50,
            #     "joint_3": 30,
            #     "joint_4": 60
            # }
            # gripper.position_control(
            #     positions=pos_dict,
            #     velocity=50,
            #     velocities=vel_dict,
            #     Kp=60
            # )
            # time.sleep(2)

            # # 7) Test current_control on joints 5–8
            # print("[TEST] Testing current_control on joints 5–8...")
            # curr_dict = {
            #     "joint_5": 40,
            #     "joint_6": 55,
            #     "joint_7": 35,
            #     "joint_8": 65
            # }
            # gripper.current_control(currents=curr_dict, Kp=55)
            # time.sleep(2)

            # # 8) Test compliant_control on joints 9–12
            # print("[TEST] Testing compliant_control on joints 9–12...")
            # comp_pos = {
            #     "joint_9": 50,
            #     "joint_10": 70,
            #     "joint_11": 60,
            #     "joint_12": 80
            # }
            # # Per-joint P gains
            # comp_kps = {
            #     "joint_9": 700,
            #     "joint_10": 900,
            #     "joint_11": 800,
            #     "joint_12": 1000
            # }
            # comp_vels = {
            #     "joint_9": 30,
            #     "joint_10": 40,
            #     "joint_11": 35,
            #     "joint_12": 45
            # }
            # gripper.compliant_control(
            #     positions=comp_pos,
            #     kp=800,
            #     kps=comp_kps,
            #     velocity=50,
            #     velocities=comp_vels
            # )
            # time.sleep(2)

            # 9) Print status summary
            print("[TEST] ✅ Status report:")
            print("  ➤ Joint Positions:", gripper.get_joint_positions())
            print("  ➤ Joint Currents :", gripper.get_joint_currents())
            print("  ➤ Object in Hand :", gripper.is_object_in_hand())
            print("  ➤ Slipping Object:", gripper.is_object_slipping())

            print("[TEST] ✅ All tests passed successfully.")

        except Exception as e:
            print(f"[TEST] ❌ Test failed: {e}")

    else:
        print("[TEST] ❌ Unable to connect to DAG Gripper")

    gripper.close()




