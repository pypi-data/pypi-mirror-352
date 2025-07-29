import json
import socket
import threading
import time
import traceback

class SARModule:
    def __init__(self, esp_ip="10.42.0.53", esp_port=4196):
        print(f"[DEBUG] Initializing SARModule with IP: {esp_ip}, Port: {esp_port}")
        self.esp_ip = esp_ip
        self.esp_port = esp_port
        self.status = {}
        self._closing = False
        self.lock = threading.Lock()
        self._stroke_max = 100  # Default value
        self._stroke_min = 0    # Default value

    def _send_command(self, command):
        print(f"[DEBUG] Sending command to ESP: {command}")
        try:
            with self.lock, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                print(f"[DEBUG] Connecting to {self.esp_ip}:{self.esp_port}")
                sock.connect((self.esp_ip, self.esp_port))

                message = json.dumps({"input": command}) + "\n"
                print(f"[DEBUG] Sending message: {message.strip()}")
                sock.sendall(message.encode())

                response_data = b""
                while True:
                    chunk = sock.recv(4096)
                    print(f"[DEBUG] Received chunk: {chunk}")
                    if not chunk:
                        break
                    response_data += chunk
                    if b'\n' in chunk:
                        break

                decoded_response = response_data.decode()
                print(f"[DEBUG] Full response: {decoded_response.strip()}")
                self.status = json.loads(decoded_response)

        except Exception as e:
            print(f"[ERROR] Command send error: {e}")
            traceback.print_exc()
            self.status = {"error": str(e)}

    def grip_close(self, velocity=50, strokeMin=0, strokeMax=100, maxContactForce=50):
        print(f"[DEBUG] grip_close called with velocity={velocity}, strokeMin={strokeMin}, strokeMax={strokeMax}, maxContactForce={maxContactForce}")
        self._stroke_max = strokeMax
        self._stroke_min = strokeMin
        command = {
            "graspCommand": True,
            "setVelocity": velocity,
            "strokeMin": strokeMin,
            "strokeMax": strokeMax,
            "setMaxContactForce": maxContactForce
        }
        self._send_command(command)

    def grip_open(self, velocity=50, strokeMin=0, strokeMax=100, maxContactForce=50):
        print(f"[DEBUG] grip_open called with velocity={velocity}, strokeMin={strokeMin}, strokeMax={strokeMax}, maxContactForce={maxContactForce}")
        self._stroke_max = strokeMax
        self._stroke_min = strokeMin
        command = {
            "graspCommand": False,
            "setVelocity": velocity,
            "strokeMin": strokeMin,
            "strokeMax": strokeMax,
            "setMaxContactForce": maxContactForce
        }
        self._send_command(command)

    def get_status(self):
        print("[DEBUG] get_status called")
        self._send_command({"getStatus": True})
        print(f"[DEBUG] Current status: {json.dumps(self.status, indent=2)}")
        return self.status

    def is_grasp_attempt_complete(self, tolerance=2):
        print("[DEBUG] Checking if grasp attempt is complete with tolerance:", tolerance)
        self.get_status()
        stroke = self.status.get("currentStroke", 0)
        print(f"[DEBUG] currentStroke: {stroke}, targetStroke: {self._stroke_max}")
        return abs(stroke - self._stroke_max) <= tolerance

    def is_open_attempt_complete(self, threshold=None):
        if threshold is None:
            threshold = self._stroke_min
        print(f"[DEBUG] Checking if gripper is fully open with threshold {threshold}")
        self.get_status()
        stroke = self.status.get("currentStroke", 0)
        print(f"[DEBUG] currentStroke: {stroke}")
        return stroke <= threshold

    def wait_until(self, condition_func, timeout=10, interval=0.5):
        print(f"[DEBUG] Waiting until condition is met (timeout: {timeout}s, interval: {interval}s)")
        start = time.time()
        while time.time() - start < timeout:
            result = condition_func()
            print(f"[DEBUG] Condition result: {result}")
            if result:
                print("[DEBUG] Condition satisfied")
                return True
            time.sleep(interval)
        print("[WARNING] Condition wait timed out.")
        return False

    def exit(self):
        print("[DEBUG] exit called")
        self._closing = True


if __name__ == "__main__":
    print("[DEBUG] Starting SARModule test loop")
    sar = SARModule()

    stroke_min = 40
    stroke_max = 60
    max_force = 60

    sar.grip_close(
        velocity=100,
        strokeMin=stroke_min,
        strokeMax=stroke_max,
        maxContactForce=max_force
    )
    sar.wait_until(sar.is_grasp_attempt_complete, timeout=15)
    
    time.sleep(2)

    sar.grip_open(
        velocity=100,
        strokeMin=stroke_min,
        strokeMax=stroke_max,
        maxContactForce=max_force
    )
    sar.wait_until(sar.is_open_attempt_complete, timeout=15)

    sar.exit()
    print("[DEBUG] Test loop complete. Exiting.")
