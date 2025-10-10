import argparse, torch
from torch.utils.data import DataLoader
from dataset import SnippetPairsDataset
from model import HybridEncoder
import torch.nn.functional as F

def nt_xent_loss(z1, z2, temp=0.07):
    z = torch.cat([z1, z2], dim=0)
    sim = F.cosine_similarity(z.unsqueeze(1), z.unsqueeze(0), dim=2) / temp
    N = z1.size(0)
    diag = torch.eye(2*N, device=z.device).bool()
    sim[diag] = -1e9
    pos_idx = (torch.arange(2*N, device=z.device) + N) % (2*N)
    loss = F.cross_entropy(sim, pos_idx)
    return loss

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--meta', required=True)
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--device', default='cpu')
    args = parser.parse_args()
    ds = SnippetPairsDataset(args.meta)
    dl = DataLoader(ds, batch_size=args.batch_size, shuffle=True, num_workers=0)
    device = torch.device(args.device)
    model = HybridEncoder(resnet_name='resnet34', embed_dim=384, num_transformer_layers=3).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    for epoch in range(args.epochs):
        tot=0.0
        for i, (crop, page) in enumerate(dl):
            crop = crop.to(device); page = page.to(device)
            zc = model(crop); zp = model(page)
            loss = nt_xent_loss(zc, zp)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item()
            if (i+1)%10==0:
                print(f"Epoch {epoch+1} iter {i+1} avg_loss {tot/(i+1):.4f}")
        print(f"Epoch {epoch+1} finished avg_loss {tot/len(dl):.4f}")
    # save model
    torch.save(model.state_dict(), 'model_checkpoint.pt')
    print('Saved model_checkpoint.pt')
