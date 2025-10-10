import os, json, random, math
from PIL import Image
import argparse

def list_pages(pages_dir):
    imgs = [f for f in os.listdir(pages_dir) if f.lower().endswith(('.png','.jpg','.jpeg'))]
    out = []
    for im in imgs:
        # Expect filenames like <pdfname>_page_0001.png
        # We'll store pdf_id as prefix before _page_
        name = os.path.splitext(im)[0]
        if '_page_' in name:
            pdf_id = name.split('_page_')[0]
            # parse page num
            try:
                page_num = int(name.split('_page_')[1])
            except:
                page_num = -1
        else:
            pdf_id = name
            page_num = -1
        out.append((pdf_id, page_num, os.path.join(pages_dir, im)))
    return out

def make_crops_for_page(path, crops=6, min_area=0.03, max_area=0.5):
    img = Image.open(path)
    W, H = img.size
    samples = []
    for _ in range(crops):
        for attempt in range(10):
            area = random.uniform(min_area, max_area)
            target_area = area * W * H
            aspect = random.uniform(0.4, 2.5)
            w = int(round((target_area*aspect)**0.5))
            h = int(round((target_area/aspect)**0.5))
            if w>0 and h>0 and w < W and h < H:
                x = random.randint(0, W-w)
                y = random.randint(0, H-h)
                samples.append((x,y,w,h))
                break
    return samples

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages_dir', required=True)
    parser.add_argument('--out_meta', required=True)
    parser.add_argument('--crops_per_page', type=int, default=6)
    args = parser.parse_args()
    pages = list_pages(args.pages_dir)
    meta = []
    for pdf_id, page_num, path in pages:
        crops = make_crops_for_page(path, crops=args.crops_per_page)
        for bbox in crops:
            meta.append({'pdf_id': pdf_id, 'page': page_num, 'path': path, 'bbox': bbox})
    with open(args.out_meta, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print('Wrote meta with', len(meta), 'samples to', args.out_meta)
