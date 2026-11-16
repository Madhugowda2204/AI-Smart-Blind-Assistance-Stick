import serial

def connect_arduino(port="COM3", baud=9600):
    try:
        arduino = serial.Serial(port, baud, timeout=1)
        print("✅ Arduino connected")
        return arduino
    except Exception:
        print("⚠️ Arduino not found, running without vibration support")
        return None

def vibrate(arduino, state="0"):
    """
    Send vibration signal:
    - "1" = Vibrate
    - "0" = Stop
    """
    if arduino:
        try:
            arduino.write(state.encode())
        except:
            print("⚠️ Failed to send to Arduino")
