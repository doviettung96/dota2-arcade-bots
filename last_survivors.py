import json
import re
import time

import numpy as np
import pyautogui
import gui
import keyboard

from ocr import run_ocr
from gui import find_pattern_and_click, find_and_click_text_line, reset_cursor, move_circular
from skills import detect_skill



def select_stage(region=None, offset=(0, 0), map="Underworld", difficulty="Master", level="1", speed="x1"):
    img = pyautogui.screenshot(region=region)
    img.save("screen/stage_selection_screen.png")
    text_lines = run_ocr(img)
    # # TODO: This box's position is relative to the capture image -> need to turn it to absolute
    matched_boxes = [None for _ in range(5)]
    
    matched_boxes[0] = find_and_click_text_line(text_lines, target=map, region=region, offset=offset, sleep_time=1)
    if matched_boxes[0] is not None:
        candidate_boxes = [text_line for text_line in text_lines if text_line['top'] > matched_boxes[0][0][1]]
        matched_boxes[1] = find_and_click_text_line(candidate_boxes, target=difficulty, region=region, offset=offset, sleep_time=1)
    if matched_boxes[1] is not None:
        candidate_boxes = [text_line for text_line in text_lines if text_line['top'] > matched_boxes[1][0][1]]
        matched_boxes[2] = find_and_click_text_line(candidate_boxes, target=level, region=region, offset=offset, sleep_time=1)
    if matched_boxes[2] is not None:
        candidate_boxes = [text_line for text_line in text_lines if text_line['top'] > matched_boxes[2][0][1]]
        matched_boxes[3] = find_and_click_text_line(candidate_boxes, target=speed, region=region, offset=offset, sleep_time=1)
    
    confirm_box = pyautogui.locateCenterOnScreen("assets/confirm.png", grayscale=True, confidence=0.7, region=region)
    if confirm_box is not None:
        pyautogui.moveTo(confirm_box[0], confirm_box[1], duration=np.random.uniform(0.1, 0.3))
        pyautogui.click()
        time.sleep(1 + np.random.uniform(0.1, 0.3))

        return confirm_box


def select_hero(hero="drow", hero_region=None, start_region=None):
    hero_box = find_pattern_and_click(f"assets/{hero}.png", "screen/hero_selection_screen.png", grayscale=True, confidence=0.7, region=hero_region, sleep_time=1)
    start_box = find_pattern_and_click("assets/fight.png", "screen/start_screen.png", grayscale=True, confidence=0.7, region=start_region, sleep_time=1)

    return hero_box, start_box

def select_portal_back(region=None, minimap_region=None, center=(0, 0), step=1):
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

        gui.click(x + minimap_region[0], y + minimap_region[1])
        time.sleep(1 + np.random.uniform(0.1, 0.3))

    # TODO: detect the portal given that view
    portal_back_box = find_pattern_and_click("assets/portal_back.png", "screen/portal_back_screen.png", button='right', grayscale=False, confidence=0.6, region=region, sleep_time=3)

    return portal_back_box

def select_skill(current_skills, region=None):
    new_skill_box = detect_skill(current_skills, region=region)
    if new_skill_box is not None:
        print('New skill', new_skill_box)
        print("Current skills", current_skills)
        current_skills[new_skill_box['text']] = current_skills.get(new_skill_box['text'], 0) + 1
        pyautogui.moveTo(new_skill_box['left'] + new_skill_box['width'] // 2 + region[0], new_skill_box['top'] + new_skill_box['height'] // 2 + region[1], duration=np.random.uniform(0.1, 0.3))
        pyautogui.click()
        time.sleep(2 + np.random.uniform(0.1, 0.3))
    else:
        time.sleep(1 + np.random.uniform(0.1, 0.3))
    
    return current_skills, new_skill_box


def center_courier():
    pyautogui.keyDown("Space")
    time.sleep(np.random.uniform(0.1, 0.3))
    pyautogui.keyUp("Space")


if __name__ == "__main__":
    configs = json.load(open('config.json', 'r'))
    H = configs['screen_resolution']['H']
    W = configs['screen_resolution']['W']
    center_region = (W // 4, H // 4, W // 2, H // 2)
    select_duration = configs['select_duration']
    match_duration = configs['match_duration']
    stage_config = configs['stage_config']
    hero_config = configs['hero_config']

    finished_matches = 0
    while not keyboard.is_pressed('q'):
        current_match_duration = match_duration
        current_skills = {}
        next_move = 0

        print("New match starts")
        time.sleep(2 + np.random.uniform(0.1, 0.3))

        stage_npc_box = None
        while stage_npc_box is None:
            center_courier()
            stage_npc_box = find_pattern_and_click("assets/guide.png", "screen/stage_npc_screen.png", grayscale=True, confidence=0.7, region=center_region, offset=(0, H // 50), sleep_time=1)
            time.sleep(1 + np.random.uniform(0.1, 0.3))

        confirm_box = None
        while confirm_box is None:
            confirm_box = select_stage(region=(W // 6, H // 6, 2 * W // 3, 2 * H // 3), **stage_config)

        portal_box = None
        while portal_box is None:
            portal_box = find_pattern_and_click("assets/portal.png", "screen/portal_screen.png", button='right', grayscale=True, confidence=0.7, region=center_region, sleep_time=3)
        
        hero_box, start_box  = select_hero(hero=hero_config['name'], hero_region=(0, 0, W // 2, H), start_region=(5 * W // 6, 5 * H // 6, W // 6, H // 6))

        if hero_box is None or start_box is None:
            print("Play with random hero")
            time.sleep(select_duration + np.random.uniform(0.1, 0.3))
        else:
            print(f"Play with {hero_config['name']} hero")


        start_time = time.time()

        end_match_box = None
        skill_selection_region = (3 * W // 4, H // 5, W // 4, 4 * H // 5)
        while end_match_box is None:
            # TODO: we do the in game actions here
            # TODO: first will be check for skill
            current_skills, new_skill_box = select_skill(current_skills, region=skill_selection_region)
            if new_skill_box is not None:
                reset_cursor(region=skill_selection_region, rand_range=(skill_selection_region[2] // 10, skill_selection_region[3] // 10))

            # only check for the end after a fix amount of time
            current_time = time.time() 
            in_game_time = current_time - start_time
            if in_game_time > current_match_duration:
                end_match_box = find_pattern_and_click("assets/confirm.png", "screen/end_match_screen.png", grayscale=True, confidence=0.7, region=(W // 3, H // 3, W // 3, 2 * H // 3), sleep_time=2)
            else:
                next_move = move_circular(next_move)
            
        portal_back_box = None
        while portal_back_box is None:
            portal_back_box = select_portal_back(region=(W // 4, H // 4, W // 2, H // 2), minimap_region=(0, 3 * H // 4, W // 8, H // 4), center=(W // 2, H // 2), step=2)

        finished_matches += 1
        print(f"Finished {finished_matches}")
        