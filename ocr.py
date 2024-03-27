import pytesseract
from pytesseract.pytesseract import Output

# from gui_utils import click

def run_ocr(img):
    results = pytesseract.image_to_data(img, output_type=Output.DICT)
    converted_results = []
    for idx, result in enumerate(results['text']):
        converted_results.append({
            'text': result,
            'left': results['left'][idx],
            'top': results['top'][idx],
            'width': results['width'][idx],
            'height': results['height'][idx],
        })
    return converted_results

def calculate_vertical_overlap(rect1, rect2):
    # Unpack rectangle coordinates
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    # Calculate y-coordinates of top and bottom edges for both rectangles
    top1, bottom1 = y1, y1 + h1
    top2, bottom2 = y2, y2 + h2

    # Calculate the intersection of y-coordinates
    intersection_y = max(0, min(bottom1, bottom2) - max(top1, top2))

    return intersection_y

def is_same_line(rect1, rect2, threshold=0.5):
    return calculate_vertical_overlap(rect1, rect2) >= threshold

def merge_boxes(rect1, rect2):
    # Unpack box coordinates
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    
    # Calculate coordinates of the merged box
    min_x = min(x1, x2)
    min_y = min(y1, y2)
    max_x = max(x1 + w1, x2 + w2)
    max_y = max(y1 + h1, y2 + h2)
    
    # Calculate width and height of the merged box
    merged_w = max_x - min_x
    merged_h = max_y - min_y
    
    return min_x, min_y, merged_w, merged_h

def convert_to_absolute(bbox, region):
    return [
        bbox[0] + region[0],
        bbox[1] + region[1],
        bbox[2],
        bbox[3]
    ]

def find_text_line(text_lines, target=''):
    bboxes = []
    # single line contain all
    for text_line in text_lines:
        if target in text_line['text']:
            bbox = [
                text_line['left'],
                text_line['top'],
                text_line['width'],
                text_line['height'],
            ]
            bboxes.append(bbox)

    return bboxes

    
def binarize_image(img, threshold):
    # Convert the image to grayscale
    grayscale_img = img.convert("L")
    
    # Binarize the image using the specified threshold
    binarized_img = grayscale_img.point(lambda p: p > threshold and 255)
    
    return binarized_img