import torch.nn as nn


class MLPPredictor(nn.Module):

    def __init__(self, input_dim=480):

        super().__init__()

        self.model = nn.Sequential(

            nn.Linear(input_dim,256),
            nn.ReLU(),

            nn.Linear(256,128),
            nn.ReLU(),

            nn.Linear(128,64),
            nn.ReLU(),

            nn.Linear(64,2)

        )

    def forward(self,x):

        return self.model(x)