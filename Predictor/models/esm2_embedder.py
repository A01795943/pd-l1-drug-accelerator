import torch
import esm
from tqdm import tqdm

class ESM2Embedder:
    def __init__(self, model_name="esm2_t12_35M_UR50D", device=None, batch_size=16):
        self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.batch_size = batch_size
        
        print(f"Loading {model_name} on {self.device}...")
        self.model, self.alphabet = esm.pretrained.load_model_and_alphabet(model_name)
        self.model.to(self.device)
        self.model.eval()
        self.batch_converter = self.alphabet.get_batch_converter()

    def embed(self, sequences):
        # Limpieza de secuencias: ESM2 no reconoce el carácter '/' de complejos
        # Se recomienda reemplazarlo por un espacio o eliminarlo según el paper de ESM
        clean_seqs = [s.replace("/", "") for s in sequences]
        
        all_embeddings = []
        
        for i in tqdm(range(0, len(clean_seqs), self.batch_size), desc="Extracting ESM embeddings"):
            batch_seqs = clean_seqs[i : i + self.batch_size]
            
            # Formato requerido por ESM: [(id, seq), ...]
            data = [(f"seq_{j}", seq) for j, seq in enumerate(batch_seqs)]
            batch_labels, batch_strs, batch_tokens = self.batch_converter(data)
            batch_tokens = batch_tokens.to(self.device)

            with torch.no_grad():
                results = self.model(batch_tokens, repr_layers=[self.model.num_layers], return_contacts=False)
            
            token_representations = results["representations"][self.model.num_layers]

            # Generar Mean Pooling (promedio de la secuencia omitiendo padding y tokens especiales)
            for j, seq in enumerate(batch_strs):
                mean_embedding = token_representations[j, 1 : len(seq) + 1].mean(0)
                all_embeddings.append(mean_embedding.cpu())

        return torch.stack(all_embeddings)

if __name__ == "__main__":
    # Test rápido si se ejecuta directamente
    print("Clase ESM2Embedder lista.")