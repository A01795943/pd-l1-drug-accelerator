import torch
import pandas as pd
from models.esm2_embedder import ESM2Embedder
from models.transformer_encoder import TransformerEncoder
from models.mlp_predictor import MLPPredictor
from tqdm import tqdm  # barra de progreso

# -----------------------------
# Device
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

# -----------------------------
# Cargar dataset procesado
# -----------------------------
df = pd.read_csv("data/processed_dataset.csv")

# Secuencias
sequences = df["seq"].tolist()

# Targets PTM/IPTM
targets = torch.tensor(df[["PTM","IPTM"]].values, dtype=torch.float32).to(device)

# -----------------------------
# Inicializar embedder
# -----------------------------
embedder = ESM2Embedder(batch_size=2)  # batch pequeño si GPU limitada

# -----------------------------
# Generar embeddings
# -----------------------------
print("Generating embeddings...")
embeddings_list = []

for i in tqdm(range(0, len(sequences), embedder.batch_size), desc="Embedding batches"):
    batch_seqs = sequences[i:i+embedder.batch_size]
    
    # Reemplazar '/' por 'X' temporalmente solo para ESM2
    batch_seqs_sanitized = [seq.replace("/", "X") for seq in batch_seqs]
    
    # Generar embeddings
    batch_emb = embedder.embed(batch_seqs_sanitized, pooling='mean')  # pooling para tamaño fijo
    embeddings_list.append(batch_emb)

# Concatenar todos los embeddings
embeddings = torch.cat(embeddings_list, dim=0).to(device)
print("Embeddings shape:", embeddings.shape)

# -----------------------------
# Agregar dim para transformer
# -----------------------------
embeddings = embeddings.unsqueeze(1)  # [B, 1, D]

# -----------------------------
# Inicializar modelos
# -----------------------------
transformer = TransformerEncoder().to(device)
mlp = MLPPredictor().to(device)

optimizer = torch.optim.Adam(list(transformer.parameters()) + list(mlp.parameters()), lr=1e-4)
loss_fn = torch.nn.MSELoss()

# -----------------------------
# Training loop
# -----------------------------
epochs = 10
for epoch in range(epochs):
    transformer.train()
    mlp.train()
    
    optimizer.zero_grad()
    
    # Pasar embeddings por transformer
    encoded = transformer(embeddings)  # [B, L, D]
    pooled = encoded.mean(1)           # pool para tamaño fijo [B, D]
    
    # Pasar por MLP
    preds = mlp(pooled)                # [B, 2]
    
    # Calcular loss
    loss = loss_fn(preds, targets)
    loss.backward()
    optimizer.step()
    
    print(f"Epoch {epoch+1}/{epochs} - Loss: {loss.item():.4f}")

# -----------------------------
# Guardar modelos
# -----------------------------
torch.save({
    "transformer": transformer.state_dict(),
    "mlp": mlp.state_dict()
}, "outputs/model.pt")
print("Model saved to outputs/model.pt")