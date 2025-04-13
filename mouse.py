import tkinter as tk
import pyautogui
import threading
import time
import keyboard  # pip install keyboard
import datetime

class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖱️ Mouse Tracker")
        self.root.attributes('-topmost', True)
        self.root.geometry("500x125+50+50")
        self.root.resizable(False, False)
        self.root.configure(bg="black")

        self.label = tk.Label(
            root,
            text="Mouse Position: ",
            font=("Helvetica", 14),
            fg="lime",
            bg="black"
        )
        self.label.pack(pady=5)

        self.hint = tk.Label(
            root,
            text="Press 'c' to copy position",
            font=("Helvetica", 9),
            fg="gray",
            bg="black"
        )
        self.hint.pack()

        self.running = True
        threading.Thread(target=self.update_loop, daemon=True).start()
        threading.Thread(target=self.check_keypress, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self.stop)

    def update_loop(self):
        while self.running:
            x, y = pyautogui.position()
            self.label.config(text=f"({x}, {y})")
            time.sleep(0.01)

    def check_keypress(self):
        while self.running:
            if keyboard.is_pressed("c"):
                x, y = pyautogui.position()
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open("mouse_positions.txt", "a") as f:
                    f.write(f"{y}\n")
                print(f"[✓] Copied position: ({x}, {y})")
                time.sleep(0.3)  # prevent spamming

    def stop(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseTrackerApp(root)
    root.mainloop()
