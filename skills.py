import pyautogui
from ocr import run_ocr

# TODO: define the relationship between different skills
# NOTE: the skills are ranked from the most favorite to the least in active and passive

ITEMS = [
    'midas',
    'armlet',
    'dagon',
    'bloodthorn',
    "bridgan's",
    "shiva's",
    'desolator',
    'veil',
    'quickening',
    'satanic',
    'aegis',
    'eternal',
    'divine',
    'fusion',
]


ACTIVE_SKILLS = {
    'frost': 'crown',
    'refraction': 'secret',
    'void': None,
    'diabolic': 'time crystal',
    'psi': 'secret',
    'headshot': 'reload',
    'attack': 'tooth',
    'meat': 'flesh',
    'aphotic': 'dark energy',
    'shrapnel': 'reload',
}
PASSIVE_SKILLS = [
    'dark',
    'secret',
    'flame',
    'crown',
    'reload',
    'time',
    'flesh',
    'tooth',
]


OTHERS = [
    'rising'
    'dice'
]
SKIP = "skip"
REFRESH = "refresh"

def detect_skill(current_skills, region=None):
    img = pyautogui.screenshot(region=region)
    img.save("screen/skill_selection_screen.png")
    text_lines = run_ocr(img)

    matched_items =[]
    matched_active = []
    matched_passive = []
    matched_other = []
    matched_skip = []
    matched_refresh = []
    for text_line in text_lines:
        splited_text = text_line['text'].lower().split(" (")
        for text in splited_text:
            if text in ITEMS:
                text_line['text'] = text
                matched_items.append(text_line)
                break

            if text in ACTIVE_SKILLS:
                text_line['text'] = text
                matched_active.append(text_line)
                break
            
            if text in PASSIVE_SKILLS:
                text_line['text'] = text
                matched_passive.append(text_line)
                break

            if text in OTHERS:
                text_line['text'] = text
                matched_other.append(text_line)
                break

            if text == REFRESH:
                text_line['text'] = text
                matched_refresh.append(text_line)
                break

            if text == SKIP:
                text_line['text'] = text
                matched_skip.append(text_line)
                break
    
    if matched_items:
        return min(matched_items, key=lambda x: ITEMS.index(x['text']))
    
    if matched_active:
        return min(matched_active, key=lambda x: list(ACTIVE_SKILLS.keys()).index(x['text']))
    
    if matched_passive:
        prefered_unlearn_passive = [ACTIVE_SKILLS[active] for active in set(current_skills.keys()).intersection(ACTIVE_SKILLS.keys())]
        for text_line in matched_passive:
            if text_line['text'] in prefered_unlearn_passive:
                return text_line

        # prioritize the other items over new passive
        if matched_other:
            return min(matched_other, key=lambda x: OTHERS.index(x['text']))
        
        return min(matched_passive, key=lambda x: PASSIVE_SKILLS.index(x['text']))
    
    if matched_other:
        return min(matched_other, key=lambda x: OTHERS.index(x['text']))
    
    if matched_refresh:
        return matched_refresh[0]

    if matched_skip:
        return matched_skip[0]
    
    print("No skill detected with", [text_line['text'] for text_line in text_lines])
    
    return None



