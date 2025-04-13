import pyautogui
import time
import threading
import tkinter as tk
import keyboard  # For global hotkey detection

# Global control variable
running = False

# Function that presses '=' repeatedly when running is True
def press_space():
    while True:
        if running:
            pyautogui.press('=')  # Replace '=' with ' ' if you prefer spacebar
        time.sleep(0.01)

# Function to toggle the running state 
def toggle():
    global running
    running = not running 
    status_label.config(text=f"Status: {'ON' if running else 'OFF'}", 
                        fg="green" if running else "red")
    toggle_button.config(text="Stop" if running else "Start")

# Start the background thread for key pressing
threading.Thread(target=press_space, daemon=True).start()

# Setup GUI
root = tk.Tk()         
root.title("Spacebar Presser")    
root.geometry("600x300")   
root.attributes('-topmost', True)  # Keep the window always on top

status_label = tk.Label(root, text="Status: OFF", font=("Arial", 16), fg="red")
status_label.pack(pady=10)

toggle_button = tk.Button(root, text="Start", command=toggle, font=("Arial", 14), width=10)
toggle_button.pack(pady=10)

# When quitting, also remove all global hotkeys
quit_button = tk.Button(root, text="Quit", 
                        command=lambda: (keyboard.unhook_all_hotkeys(), root.destroy()), 
                        font=("Arial", 12))
quit_button.pack(pady=5)

# Register the global hotkey for "0" to toggle the state
keyboard.add_hotkey('0', toggle)

root.mainloop()