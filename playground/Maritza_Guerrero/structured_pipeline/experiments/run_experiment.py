import yaml
from structured_pipeline.core.pipeline import DesignPipeline

# --- Configuración del experimento ---
config = {
    'experiment': {
        'name': 'PDL1_design',
    },
    'pdb': {
        'source': '6B3J',
        'chain_to_remove': 'P'
    },
    'rfdiffusion': {
        'contigs': '12-15/0 R311-337',
        'hotspot': ['R312', 'R313', 'R314', 'R315'],
        'iterations': 30,
        'num_designs': 2,
        'visual': 'image',
        'symmetry': None,
        'symmetry_order': None,
        'chains': None
    },
    'mpnn': {
        'num_sequences': 5,
        'temperature': 0.1
    }
}

if __name__ == "__main__":
    # --- Inicializar pipeline con toda la configuración ---
    pipeline = DesignPipeline(config)
    pipeline.run()
