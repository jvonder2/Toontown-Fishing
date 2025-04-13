import cv2 as cv
import numpy as np
import pyautogui
import time
import math
import mss

# Load templates
fish_template = cv.imread('fish_shadow_fixed.jpg')
dot_template = cv.imread('cast_dot_fixed.jpg')
red_x_template = cv.imread('red_x_button.png')

fish_w, fish_h = fish_template.shape[1], fish_template.shape[0]
dot_w, dot_h = dot_template.shape[1], dot_template.shape[0]
red_x_w, red_x_h = red_x_template.shape[1], red_x_template.shape[0]

# ---- SETTINGS ----
DRAG_DURATION = 0.7
CONFIDENCE_THRESHOLD = 0.75
RED_X_THRESHOLD = 0.85
ANGLE_CORRECTION_DEGREES = -3
FAST_REFRESH = 0.01
POST_CAST_DELAY = 1.5
SHOW_VISUAL_DEBUG = False
DEBUG_SCALE = 0.4
# ------------------

# Use full monitor for capture
sct = mss.mss()
monitor = sct.monitors[1]  # 1 = full primary screen

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
    red_x_pos, red_x_conf = locate_on_screen(red_x_template, img_bgr)
    if red_x_conf > RED_X_THRESHOLD:
        center = (red_x_pos[0] + red_x_w // 2, red_x_pos[1] + red_x_h // 2)
        pyautogui.moveTo(center)
        pyautogui.click()
        print(" Red X found and clicked!")
        return True
    return False

def get_pullback_distance(distance):
    pullback = distance / 3
    return max(min(pullback, 300), 50)

# ---- MAIN LOOP ----
try:
    while True:
        img_bgr = get_screen()

        if check_and_click_red_x(img_bgr):
            time.sleep(1)
            continue

        fish_pos, fish_conf = locate_on_screen(fish_template, img_bgr)
        dot_pos, dot_conf = locate_on_screen(dot_template, img_bgr)

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

            print(f" CAST: Drag {int(pullback_distance)}px for fish {int(distance)}px away")

            if SHOW_VISUAL_DEBUG:
                debug_img = img_bgr.copy()
                cv.rectangle(debug_img, fish_pos, (fish_pos[0]+fish_w, fish_pos[1]+fish_h), (255, 0, 0), 2)
                cv.rectangle(debug_img, dot_pos, (dot_pos[0]+dot_w, dot_pos[1]+dot_h), (0, 255, 0), 2)
                cv.line(debug_img,
                        (dot_center[0], dot_center[1]),
                        (reverse_x, reverse_y),
                        (0, 255, 255), 2)
                debug_small = cv.resize(debug_img, None, fx=DEBUG_SCALE, fy=DEBUG_SCALE)
                cv.imshow(" Bot Vision", debug_small)
                cv.waitKey(1)

            time.sleep(POST_CAST_DELAY)

        elif SHOW_VISUAL_DEBUG:
            img_small = cv.resize(img_bgr, None, fx=DEBUG_SCALE, fy=DEBUG_SCALE)
            cv.imshow(" Bot Vision", img_small)
            cv.waitKey(1)

        time.sleep(FAST_REFRESH)

except KeyboardInterrupt:
    print("\n Bot stopped.")
    cv.destroyAllWindows()
