import torch.nn as nn


class TransformerEncoder(nn.Module):

    def __init__(self, embed_dim=480):

        super().__init__()

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=8,
            batch_first=True
        )

        self.encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=2
        )

    def forward(self, x):

        x = self.encoder(x)

        return x