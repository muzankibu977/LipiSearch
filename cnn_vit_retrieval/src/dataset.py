import json
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

class SnippetPairsDataset(Dataset):
    def __init__(self, meta_json, transform=None):
        with open(meta_json, 'r', encoding='utf-8') as f:
            self.meta = json.load(f)
        self.transform = transform or transforms.Compose([
            transforms.Resize((512,512)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
        ])

    def __len__(self):
        return len(self.meta)

    def __getitem__(self, idx):
        sample = self.meta[idx]
        page = Image.open(sample['path']).convert('RGB')
        x,y,w,h = sample['bbox']
        crop = page.crop((x,y,x+w,y+h))
        page_t = self.transform(page)
        crop_t = self.transform(crop)
        return crop_t, page_t
