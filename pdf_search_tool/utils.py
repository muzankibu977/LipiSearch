import pytesseract
from PIL import Image
import json
from difflib import SequenceMatcher

def load_index(json_path='indexed_texts.json'):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def search_line(text, index, threshold=0.7):
    results = []
    for pdf, pages in index.items():
        for page_num, lines in enumerate(pages):
            for line_num, line in enumerate(lines):
                if similar(text.lower(), line.lower()) >= threshold:
                    results.append({
                        'pdf': pdf,
                        'page': page_num + 1,
                        'line_number': line_num + 1,
                        'line': line
                    })
    return results

def ocr_from_image(image_file, langs='eng+ben+urd+heb'):
    img = Image.open(image_file)
    return pytesseract.image_to_string(img, lang=langs)