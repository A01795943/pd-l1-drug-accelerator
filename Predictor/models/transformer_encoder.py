import torch
import torch.nn as nn

class TransformerEncoder(nn.Module):
    def __init__(self, embed_dim=1280):
        super().__init__()
        
        # d_model debe ser divisible por nhead (480 / 8 = 60, es correcto)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=8,
            batch_first=True,
            dropout=0.1
        )

        self.encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=3
        )

    def forward(self, x):
        # Si x viene como (Batch, EmbedDim), agregamos dimensión de secuencia (Batch, 1, EmbedDim)
        if x.dim() == 2:
            x = x.unsqueeze(1)
            
        x = self.encoder(x)
        
        # Devolvemos a (Batch, EmbedDim) si la secuencia era 1
        if x.size(1) == 1:
            x = x.squeeze(1)
            
        return x