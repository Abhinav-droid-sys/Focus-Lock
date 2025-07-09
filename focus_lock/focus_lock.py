import ctypes
import time
from datetime import datetime, timedelta
import threading
import keyboard  # pip install keyboard

emergency_exit = False

def lock_screen():
    ctypes.windll.user32.LockWorkStation()

def get_idle_duration():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]

    last_input_info = LASTINPUTINFO()
    last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))
    millis = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
    return millis / 1000.0

def check_emergency_key():
    global emergency_exit
    keyboard.wait('ctrl+shift+e')
    emergency_exit = True
    print("\n🚨 Emergency exit triggered.")

def start_focus_session(duration_minutes):
    global emergency_exit
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    lock_screen()
    print(f"🔒 Focus session started. Locking until {end_time.strftime('%H:%M:%S')}.")

    # Start emergency key listener
    threading.Thread(target=check_emergency_key, daemon=True).start()

    while datetime.now() < end_time:
        if emergency_exit:
            print("🔓 Session ended early due to emergency.")
            return

        idle = get_idle_duration()
        if idle < 2:  # User is interacting
            print("⚠️ Unlock attempt detected! Waiting 5 seconds for emergency override...")
            for i in range(5, 0, -1):
                if emergency_exit:
                    print("🔓 Session ended early due to emergency.")
                    return
                print(f"⏳ {i} seconds left before re-locking...", end='\r')
                time.sleep(1)
            print("\n🔒 Re-locking system.")
            lock_screen()
        time.sleep(1)

    print("✅ Focus session complete! You're free now.")

if __name__ == "__main__":
    try:
        minutes = int(input("Enter focus time in minutes: "))
        start_focus_session(minutes)
    except ValueError:
        print("Please enter a valid number.")
