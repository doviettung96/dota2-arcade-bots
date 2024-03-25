import win32api
import win32con
import time
import numpy as np
import pyautogui

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

def find_pattern_and_click(needle_image, haystack_image, button='left', grayscale=True, confidence=0.7, region=None, offset=(0, 0)):
    img = pyautogui.screenshot(region=region)
    img.save(haystack_image)

    try:
        matched_box = pyautogui.locateCenterOnScreen(needle_image, grayscale=grayscale, confidence=confidence, region=region)
        pyautogui.moveTo(matched_box[0] + offset[0], matched_box[1] + offset[1], duration=np.random.uniform(0.1, 0.3))
        if button == 'left':
            pyautogui.click()
        else:
            pyautogui.rightClick()
    except pyautogui.ImageNotFoundException as e:
        print(f"Can't find {needle_image} because of", e)
        matched_box = None

    return matched_box
