import os
from datetime import datetime
from structured_pipeline.core.pdb_handler import download_pdb
from structured_pipeline.core.rfdiffusion_engine import RFdiffusionEngine
from structured_pipeline.core.mpnn_engine import ProteinMPNNEngine
from structured_pipeline.utils.logger import setup_logger

# --- Inicializar logger ---
logger = setup_logger()  # devuelve un Logger directamente

class DesignPipeline:
    def __init__(self, config):
        self.config = config
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_dir = os.path.join("outputs", f"{timestamp}_{config['experiment']['name']}")
        self.input_dir = os.path.join(self.output_dir, "input")
        os.makedirs(self.input_dir, exist_ok=True)

    def run(self):
        logger.info("Starting experiment")
        logger.info(f"Configuration: {self.config}")

        # --- Descargar PDB ---
        pdb_code = self.config['pdb']['source']
        pdb_path = download_pdb(pdb_code, self.input_dir)

        # --- Ejecutar RFdiffusion ---
        rf_engine = RFdiffusionEngine(
            config=self.config['rfdiffusion'],  # solo la sección rfdiffusion
            pdb_path=pdb_path,
            rf_script="/workspace/RFdiffusion/scripts/run_inference.py"
        )
        rf_engine.run()

        # --- Ejecutar ProteinMPNN ---
        mpnn_engine = ProteinMPNNEngine(self.config['mpnn'], self.output_dir)
        mpnn_engine.run()
