import argparse, torch, numpy as np, faiss
from model import HybridEncoder
from PIL import Image
from torchvision import transforms
import json

def load_meta(meta_json):
    import json
    with open(meta_json,'r',encoding='utf-8') as f:
        meta = json.load(f)
    # dedupe pages
    pages = {}
    for m in meta:
        key = (m['pdf_id'], m['page'], m['path'])
        pages[key] = m['path']
    out = [(k[0], k[1], v) for k,v in pages.items()]
    return out

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--meta', required=True)
    parser.add_argument('--model_ckpt', default='model_checkpoint.pt')
    parser.add_argument('--index_out', default='index.faiss')
    parser.add_argument('--emb_out', default='embeddings.npy')
    parser.add_argument('--device', default='cpu')
    args = parser.parse_args()
    pages = load_meta(args.meta)
    device = torch.device(args.device)
    model = HybridEncoder(resnet_name='resnet34', embed_dim=384, num_transformer_layers=3).to(device)
    model.load_state_dict(torch.load(args.model_ckpt, map_location=device))
    model.eval()
    preprocess = transforms.Compose([
        transforms.Resize((512,512)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
    ])
    embs = []
    meta_list = []
    with torch.no_grad():
        for pdf_id, page_num, path in pages:
            img = Image.open(path).convert('RGB')
            x = preprocess(img).unsqueeze(0).to(device)
            z = model(x).cpu().numpy()
            embs.append(z)
            meta_list.append({'pdf_id': pdf_id, 'page': page_num, 'path': path})
    embs = np.vstack(embs).astype('float32')
    faiss.normalize_L2(embs)
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embs)
    faiss.write_index(index, args.index_out)
    np.save(args.emb_out, embs)
    with open('pages_meta_index.json','w',encoding='utf-8') as f:
        json.dump(meta_list, f, ensure_ascii=False, indent=2)
    print('Wrote index and embeddings, pages_meta_index.json')
