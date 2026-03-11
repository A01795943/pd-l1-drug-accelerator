import torch
import esm

class ESM2Embedder:
    def __init__(self, model_name="esm2_t12_35M_UR50D", device=None, batch_size=1):
        self.device = device or (torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu"))
        self.batch_size = batch_size

        # Cargar modelo más pequeño
        self.model, self.alphabet = esm.pretrained.load_model_and_alphabet(model_name)
        self.model = self.model.to(self.device)
        self.model.eval()  # Modo evaluación

        self.batch_converter = self.alphabet.get_batch_converter()

    def embed(self, sequences, pooling='mean'):
        """
        Genera embeddings para una lista de secuencias.
        Se reemplaza '/' por 'X' temporalmente para multichain sequences.
        """
        all_embeddings = []

        for i in range(0, len(sequences), self.batch_size):
             
            print(f"Embedding batch {i} / {len(sequences)}")
             
            batch_seqs = sequences[i:i+self.batch_size]

            # Reemplazar '/' por 'X' temporalmente
            batch_seqs_clean = [seq.replace("/", "X") for seq in batch_seqs]

            data = [(str(idx), seq) for idx, seq in enumerate(batch_seqs_clean)]
            labels, strs, tokens = self.batch_converter(data)
            tokens = tokens.to(self.device)

            with torch.no_grad():
                results = self.model(tokens, repr_layers=[self.model.num_layers])
                batch_embeddings = results["representations"][self.model.num_layers]  # [B, L, D]

                # Pooling para obtener embedding fijo por secuencia
                if pooling == 'mean':
                    pooled = batch_embeddings.mean(dim=1)  # [B, D]
                elif pooling == 'max':
                    pooled, _ = batch_embeddings.max(dim=1)
                else:
                    raise ValueError("Pooling debe ser 'mean' o 'max'")

                all_embeddings.append(pooled.cpu())

        return torch.cat(all_embeddings, dim=0)