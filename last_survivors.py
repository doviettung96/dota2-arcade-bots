import re
import time

import numpy as np
import pyautogui
import gui
import keyboard

from ocr import run_ocr, is_same_line, merge_boxes, convert_to_absolute, find_text_line, find_and_click_text_line, binarize_image
from gui import find_pattern_and_click

H, W = 2160, 3840


def select_stage(region=None, offset=(0, 0), map="Underworld", difficulty="Master", level="1", speed="x1"):
    img = pyautogui.screenshot(region=region)
    img.save("screen/stage_selection_screen.png")
    text_lines = run_ocr(img)
    # # TODO: This box's position is relative to the capture image -> need to turn it to absolute
    matched_boxes = [None for _ in range(5)]
    
    matched_boxes[0] = find_and_click_text_line(text_lines, target=map, region=region, offset=offset)
    time.sleep(np.random.uniform(0.5, 1.0))
    if matched_boxes[0] is not None:
        candidate_boxes = [text_line for text_line in text_lines if text_line['top'] > matched_boxes[0][0][1]]
        matched_boxes[1] = find_and_click_text_line(candidate_boxes, target=difficulty, region=region, offset=offset)
        time.sleep(np.random.uniform(0.5, 1.0))
    if matched_boxes[1] is not None:
        candidate_boxes = [text_line for text_line in text_lines if text_line['top'] > matched_boxes[1][0][1]]
        matched_boxes[2] = find_and_click_text_line(candidate_boxes, target=level, region=region, offset=offset)
        time.sleep(np.random.uniform(0.5, 1.0))
    if matched_boxes[2] is not None:
        candidate_boxes = [text_line for text_line in text_lines if text_line['top'] > matched_boxes[2][0][1]]
        matched_boxes[3] = find_and_click_text_line(candidate_boxes, target=speed, region=region, offset=offset)
        time.sleep(np.random.uniform(0.5, 1.0))
    
    confirm_box = pyautogui.locateCenterOnScreen("assets/confirm.png", grayscale=True, confidence=0.7, region=region)
    if confirm_box is not None:
        pyautogui.moveTo(confirm_box[0], confirm_box[1], duration=np.random.uniform(0.1, 0.3))
        pyautogui.click()

        return confirm_box


def select_hero(hero="drow", hero_region=None, start_region=None):
    hero_box = find_pattern_and_click(f"assets/{hero}.png", "screen/hero_selection_screen.png", grayscale=True, confidence=0.7, region=hero_region)
    time.sleep(1 + np.random.uniform(0.1, 0.3))

    start_box = find_pattern_and_click("assets/fight.png", "screen/start_screen.png", grayscale=True, confidence=0.7, region=start_region)
    time.sleep(1 + np.random.uniform(0.1, 0.3))

    return hero_box, start_box

def select_portal_back(region=None, minimap_region=None, step=1):
    # TODO: locate the portal in the minimap instead
    img = pyautogui.screenshot(region=minimap_region)
    img.save("screen/minimap.png")

    found = False
    count = 0
    for x in range(0, minimap_region[2], step):
        if found:
            break
        for y in range(0, minimap_region[3], step):
            count += 1
            if img.getpixel((x, y)) == (0, 255, 0):
                found = True
                break

    if found:
        print(f"Found portal at minimap ({x + minimap_region[0]}, {y + minimap_region[1]})")

        # gui.click(x + minimap_region[0], y + minimap_region[1])
        pyautogui.moveTo(x + minimap_region[0], y + minimap_region[1], duration=np.random.uniform(0.1, 0.3))
        pyautogui.click()
        time.sleep(1 + np.random.uniform(0.1, 0.3))

    # TODO: detect the portal given that view
    portal_back_box = find_pattern_and_click("assets/portal_back.png", "screen/portal_back_screen.png", button='right', grayscale=False, confidence=0.7, region=region)
    return portal_back_box


def center_courier():
    pyautogui.keyDown("Space")
    time.sleep(np.random.uniform(0.1, 0.3))
    pyautogui.keyUp("Space")


if __name__ == "__main__":
    center_region = (W // 4, H // 4, W // 2, H // 2)
    # match_duration = 300
    select_duration = 30
    match_duration = 30
    stage_config = {
        "map": "Underworld",
        "difficulty": "Master",
        "level": "1",
        "speed": "x2",
    }
    hero_config = {
        'name': "drow"
    }


    finished_matches = 0
    while not keyboard.is_pressed('q'):
        print("New match starts")
        time.sleep(2 + np.random.uniform(0.1, 0.3))

        stage_npc_box = None
        while stage_npc_box is None:
            center_courier()
            stage_npc_box = find_pattern_and_click("assets/guide.png", "screen/stage_npc_screen.png", grayscale=True, confidence=0.7, region=center_region, offset=(0, H // 50))
            time.sleep(1 + np.random.uniform(0.1, 0.3))

        confirm_box = None
        while confirm_box is None:
            confirm_box = select_stage(region=(W // 6, H // 6, 2 * W // 3, 2 * H // 3), **stage_config)
            time.sleep(2 + np.random.uniform(0.1, 0.3))

        portal_box = None
        while portal_box is None:
            portal_box = find_pattern_and_click("assets/portal.png", "screen/portal_screen.png", button='right', grayscale=True, confidence=0.7, region=center_region)
            time.sleep(3 + np.random.uniform(0.1, 0.3))
        
        hero_box, start_box  = select_hero(hero=hero_config['name'], hero_region=(0, 0, W // 2, H), start_region=(5 * W // 6, 5 * H // 6, W // 6, H // 6))

        if hero_box is None or start_box is None:
            print("Play with random hero")
            time.sleep(select_duration + np.random.uniform(0.1, 0.3))
        else:
            print(f"Play with {hero_config['name']} hero")

        # we still can play no matter what
        ratio = int(re.search(r'x(\d+)', stage_config['speed']).group(1))
        current_match_duration = match_duration // ratio
        print(f"Wait for {current_match_duration} seconds for {stage_config['speed']} speed")
        time.sleep(current_match_duration + np.random.uniform(0.1, 0.3))


        end_match_box = None
        while end_match_box is None:
            end_match_box = find_pattern_and_click("assets/confirm.png", "screen/end_match_screen.png", grayscale=True, confidence=0.7, region=(W // 3, H // 3, W // 3, 2 * H // 3))
            time.sleep(2 + np.random.uniform(0.1, 0.3))


        portal_back_box = None
        while portal_back_box is None:
            portal_back_box = select_portal_back(region=(W // 4, H // 4, W // 2, H // 2), minimap_region=(0, 3 * H // 4, W // 8, H // 4), step=2)
            time.sleep(3 + np.random.uniform(0.1, 0.3))

        finished_matches += 1
        print(f"Finished {finished_matches}")
        