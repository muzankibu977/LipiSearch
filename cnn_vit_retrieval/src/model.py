import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
import numpy as np

class HybridEncoder(nn.Module):
    def __init__(self, resnet_name='resnet34', embed_dim=512, num_transformer_layers=4, num_heads=8):
        super().__init__()
        resnets = {'resnet34': models.resnet34, 'resnet50': models.resnet50}
        self.backbone = resnets[resnet_name](pretrained=True)
        # remove avgpool & fc
        self.backbone.fc = nn.Identity()
        self.backbone.avgpool = nn.Identity()
        conv_out = 512 if resnet_name=='resnet34' else 2048
        self.proj = nn.Conv2d(conv_out, embed_dim, kernel_size=1)
        encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=num_heads, dim_feedforward=embed_dim*4)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_transformer_layers)
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x):
        # run through resnet until layer4
        x = self.backbone.conv1(x)
        x = self.backbone.bn1(x)
        x = self.backbone.relu(x)
        x = self.backbone.maxpool(x)
        x = self.backbone.layer1(x)
        x = self.backbone.layer2(x)
        x = self.backbone.layer3(x)
        x = self.backbone.layer4(x)  # B x C x h x w
        p = self.proj(x)  # B x D x h x w
        B,D,h,w = p.shape
        seq = p.flatten(2).permute(2,0,1)  # S,B,D
        # simple positional: create zeros (learnable pos could be added)
        pos = torch.zeros(seq.size(0), seq.size(2), device=seq.device)
        seq = seq + pos.unsqueeze(1)
        seq = self.transformer(seq)
        seq = seq.permute(1,2,0)  # B,D,S
        pooled = seq.mean(dim=2)
        pooled = self.norm(pooled)
        pooled = F.normalize(pooled, dim=1)
        return pooled
