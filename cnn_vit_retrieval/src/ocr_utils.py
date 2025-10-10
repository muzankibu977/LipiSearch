import pytesseract
from PIL import Image

def ocr_paragraph_and_bbox(page_pil, lang='eng'):
    data = pytesseract.image_to_data(page_pil, lang=lang, output_type=pytesseract.Output.DICT)
    # group words by block_num/paragraph
    paras = {}
    n = len(data['level'])
    for i in range(n):
        block = data['block_num'][i]
        par = data['par_num'][i]
        key = (block,par)
        if key not in paras:
            paras[key] = {'text': [], 'boxes': []}
        word = data['text'][i]
        if word.strip():
            paras[key]['text'].append(word)
            x,y,w,h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            paras[key]['boxes'].append((x,y,w,h))
    # assemble
    out = []
    for k,v in paras.items():
        txt = ' '.join(v['text'])
        # bbox union
        xs = [b[0] for b in v['boxes']]
        ys = [b[1] for b in v['boxes']]
        ws = [b[2] for b in v['boxes']]
        hs = [b[3] for b in v['boxes']]
        bbox = (min(xs), min(ys), max([xs[i]+ws[i] for i in range(len(ws))]) - min(xs), max([ys[i]+hs[i] for i in range(len(hs))]) - min(ys))
        out.append({'text': txt, 'bbox': bbox})
    return out
