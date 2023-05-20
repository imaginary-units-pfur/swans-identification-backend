from torch import nn
import open_clip
import albumentations as A
import torch
import math
import numpy as np
import torch.nn.functional as F
import pandas as pd
import os
from PIL import Image


class ArcMarginProduct_subcenter(nn.Module):
    def __init__(self, in_features, out_features, k=3):
        super().__init__()
        self.weight = nn.Parameter(torch.FloatTensor(out_features * k, in_features))
        self.reset_parameters()
        self.k = k
        self.out_features = out_features

    def reset_parameters(self):
        stdv = 1.0 / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)

    def forward(self, features):
        cosine_all = F.linear(F.normalize(features), F.normalize(self.weight))
        cosine_all = cosine_all.view(-1, self.out_features, self.k)
        cosine, _ = torch.max(cosine_all, dim=2)
        return cosine


class Head(nn.Module):
    def __init__(self, hidden_size):
        super(Head, self).__init__()

        self.emb = nn.Linear(hidden_size, CFG.emb_size, bias=False)
        self.arc = ArcMarginProduct_subcenter(CFG.emb_size, CFG.n_classes)
        self.dropout = Multisample_Dropout()

    def forward(self, x):
        embeddings = self.dropout(x, self.emb)

        output = self.arc(embeddings)

        return output, F.normalize(embeddings)


class Multisample_Dropout(nn.Module):
    def __init__(self):
        super(Multisample_Dropout, self).__init__()
        self.dropout = nn.Dropout(0.1)
        self.dropouts = nn.ModuleList([nn.Dropout((i + 1) * 0.1) for i in range(5)])

    def forward(self, x, module):
        x = self.dropout(x)
        return torch.mean(
            torch.stack([module(dropout(x)) for dropout in self.dropouts], dim=0), dim=0
        )


class Model(nn.Module):
    def __init__(self, vit_backbone):
        super(Model, self).__init__()

        vit_backbone = vit_backbone.visual
        self.img_size = vit_backbone.image_size
        if type(self.img_size) == tuple:
            self.img_size = self.img_size[1]
        hidden_size = vit_backbone(
            torch.zeros((1, 3, self.img_size, self.img_size))
        ).shape[1]
        self.vit_backbone = vit_backbone
        self.head = Head(hidden_size)

    def forward(self, x):
        x = self.vit_backbone(x)
        return self.head(x)


class CFG:
    model_name = "ViT-L-14-336"
    model_data = "openai"
    emb_size = 512
    n_classes = 3
    label2idx = {"шипун": 0, "кликун": 1, "малый": 2}


device = "cpu"
vit_backbone, model_transforms, _ = open_clip.create_model_and_transforms(
    CFG.model_name, pretrained=False
)
image_size = model_transforms.transforms[0].size[0]
mean, std = model_transforms.transforms[-1].mean, model_transforms.transforms[-1].std
val_aug = A.Compose(
    [A.Resize(image_size, image_size), A.Normalize(mean=mean, std=std, p=1)]
)
model = Model(vit_backbone.cpu()).to(device)
model.load_state_dict(
    torch.load("./ViT-L-14-336_openai_0.987.pth", map_location=torch.device("cpu"))
)


def process_files(paths: list):
    result_df = pd.DataFrame(
        columns=[
            "filename",
            "шипун",
            "кликун",
            "малый",
        ]
    )

    for img_path in paths:
        img = Image.open(img_path)
        prepared_img = val_aug(image=np.array(img))["image"]
        prepared_img = torch.from_numpy(prepared_img).permute(2, 0, 1).unsqueeze(0)
        with torch.no_grad():
            predict = model(prepared_img)[0].softmax(1).detach().cpu()
            result_df.loc[len(result_df)] = [os.path.basename(img_path)] + predict[
                0
            ].tolist()

    return result_df.to_dict("records")
