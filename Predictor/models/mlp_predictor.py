import torch.nn as nn

class MLPPredictor(nn.Module):
    def __init__(self, input_dim=480):
        super().__init__()
        # Arquitectura feed-forward para regresión multisalida (2 targets: PTM e IPTM)
        self.model = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.BatchNorm1d(512), # Estabiliza los gradientes de ESM-2
            nn.ReLU(),
            nn.Dropout(0.2),      # Aumentado para evitar memorización de secuencias
            
            # Bloque 2: Compresión de información
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.1),
            
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1), # Añadido para evitar sobreajuste
            
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            
            nn.Linear(128, 64),
            nn.ReLU(),
            
            nn.Linear(64, 2) # Salida de 2 neuronas para PTM e IPTM
        )

    def forward(self, x):
        return self.model(x)