import cv2 as cv
import numpy as np
import pyautogui
import time
import math
import mss
from concurrent.futures import ThreadPoolExecutor

# Load templates
fish_template = cv.imread('fish_shadow_fixed.jpg', cv.IMREAD_COLOR)
dot_template = cv.imread('cast_dot_fixed.jpg', cv.IMREAD_COLOR)
red_x_template = cv.imread('red_x_button.png', cv.IMREAD_COLOR)

fish_w, fish_h = fish_template.shape[1], fish_template.shape[0]
dot_w, dot_h = dot_template.shape[1], dot_template.shape[0]
red_x_w, red_x_h = red_x_template.shape[1], red_x_template.shape[0]

# ---- SETTINGS ----
DRAG_DURATION = 0.7
CONFIDENCE_THRESHOLD = 0.75
RED_X_THRESHOLD = 0.85
ANGLE_CORRECTION_DEGREES = 0
FAST_REFRESH = 0.005
POST_CAST_DELAY = 3
SHOW_VISUAL_DEBUG = False
DEBUG_SCALE = 0.4 
NUM_WORKERS = 8 # Number of cores working on process
# ------------------

# Setup screen capture with mss
sct = mss.mss()
monitor = sct.monitors[1]

def get_screen():
    sct_img = sct.grab(monitor)
    img = np.array(sct_img)
    img_bgr = cv.cvtColor(img, cv.COLOR_BGRA2BGR)
    return img_bgr

def locate_on_screen(template, screenshot_bgr):
    result = cv.matchTemplate(screenshot_bgr, template, cv.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv.minMaxLoc(result)
    return max_loc, max_val

def check_and_click_red_x(img_bgr):
    pos, conf = locate_on_screen(red_x_template, img_bgr)
    if conf > RED_X_THRESHOLD:
        center = (pos[0] + red_x_w // 2, pos[1] + red_x_h // 2)
        pyautogui.moveTo(center)
        pyautogui.click()
        pyautogui.moveTo((0,0))
        return True
    return False

def get_pullback_distance(distance):
    pullback = distance / 3
    return max(min(pullback, 300), 50)

def process_frame():
    # Capture screen once per loop
    img_bgr = get_screen()
    
    # Use ThreadPoolExecutor to run template matching concurrently
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        future_fish = executor.submit(locate_on_screen, fish_template, img_bgr)
        future_dot = executor.submit(locate_on_screen, dot_template, img_bgr)
        future_red_x = executor.submit(locate_on_screen, red_x_template, img_bgr)
        
        # Check red X first
        red_x_pos, red_x_conf = future_red_x.result()
        if red_x_conf > RED_X_THRESHOLD:
            center = (red_x_pos[0] + red_x_w // 2, red_x_pos[1] + red_x_h // 2)
            pyautogui.moveTo(center)
            pyautogui.click()
            return None, None, None, None, img_bgr
        
        # Get fish and dot positions
        fish_pos, fish_conf = future_fish.result()
        dot_pos, dot_conf = future_dot.result()
    
    return fish_pos, fish_conf, dot_pos, dot_conf, img_bgr

def main():
    try:
        while True:
            fish_pos, fish_conf, dot_pos, dot_conf, img_bgr = process_frame()
            # Skip if red X was clicked
            if fish_pos is None:
                time.sleep(1)
                continue

            if fish_conf > CONFIDENCE_THRESHOLD and dot_conf > CONFIDENCE_THRESHOLD:
                fish_center = (fish_pos[0] + fish_w // 2, fish_pos[1] + fish_h // 2)
                dot_center = (dot_pos[0] + dot_w // 2, dot_pos[1] + dot_h // 2)
                
                dx = fish_center[0] - dot_center[0]
                dy = fish_center[1] - dot_center[1]
                distance = math.hypot(dx, dy)
                angle = math.atan2(dy, dx) + math.radians(ANGLE_CORRECTION_DEGREES)
                
                pullback_distance = get_pullback_distance(distance)
                reverse_x = int(dot_center[0] - pullback_distance * math.cos(angle))
                reverse_y = int(dot_center[1] - pullback_distance * math.sin(angle))
                
                pyautogui.moveTo(dot_center[0], dot_center[1])
                pyautogui.dragTo(reverse_x, reverse_y, duration=DRAG_DURATION)
                time.sleep(POST_CAST_DELAY)
            
    except KeyboardInterrupt:
        print("\nBot stopped.")
        cv.destroyAllWindows()

if __name__ == "__main__":
    main()
