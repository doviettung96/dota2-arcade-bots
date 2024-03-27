
import time

import win32api
import win32con
import numpy as np
import pyautogui

from ocr import find_text_line, convert_to_absolute

def click(x, y, button="left"):
    win32api.SetCursorPos((x, y))
    if button == "left":
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(np.random.uniform(0.1, 0.3))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    if button == "right":
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        time.sleep(np.random.uniform(0.1, 0.3))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

def find_pattern_and_click(needle_image, haystack_image, button='left', grayscale=True, confidence=0.7, region=None, offset=(0, 0), sleep_time=1):
    img = pyautogui.screenshot(region=region)
    img.save(haystack_image)

    try:
        matched_box = pyautogui.locateCenterOnScreen(needle_image, grayscale=grayscale, confidence=confidence, region=region)
        pyautogui.moveTo(matched_box[0] + offset[0], matched_box[1] + offset[1], duration=np.random.uniform(0.1, 0.3))
        if button == 'left':
            pyautogui.click()
        else:
            pyautogui.rightClick()
        
        time.sleep(sleep_time + np.random.uniform(0.1, 0.3))
    except pyautogui.ImageNotFoundException as e:
        print(f"Can't find {needle_image} because of", e)
        matched_box = None

    return matched_box

def find_and_click_text_line(text_lines, target, region, offset, sleep_time=1):
    matched_boxes = find_text_line(text_lines, target=target)
    print(f"Target {target} matched boxes {matched_boxes}")

    if len(matched_boxes) >= 1:
        matched_box = matched_boxes[0]
        absolute_box = convert_to_absolute(matched_box, region)
        pyautogui.moveTo(absolute_box[0] + absolute_box[2] // 2 + offset[0], absolute_box[1] + absolute_box[3] // 2 + offset[1], duration=np.random.uniform(0.1, 0.3))
        pyautogui.click()
        time.sleep(sleep_time + np.random.uniform(0.1, 0.3))
        return matched_box, absolute_box

def reset_cursor(region=None, rand_range=(5, 5)):
    pyautogui.moveTo(region[0] + np.random.randint(0, rand_range[0]), region[1] + np.random.randint(0, rand_range[1]), duration=np.random.uniform(0.1, 0.3))
    time.sleep(1 + np.random.uniform(0.1, 0.3))

def move_circular(next_move: int, movements=['d', 's', 'a', 'w'], sleep_time=1):
    pyautogui.keyDown(movements[next_move % len(movements)])
    time.sleep(np.random.uniform(0.1, 0.3))
    pyautogui.keyUp(movements[next_move % len(movements)])

    time.sleep(sleep_time + np.random.uniform(0.1, 0.3))

    return next_move + 1