import os
import subprocess
from structured_pipeline.utils.logger import setup_logger

logger = setup_logger()

class ProteinMPNNEngine:
    def __init__(self, config, input_dir):
        self.config = config
        self.input_dir = input_dir

    def run(self):
        logger.info("Running ProteinMPNN...")
        pdb_files = [f for f in os.listdir(self.input_dir) if f.endswith(".pdb")]
        for pdb in pdb_files:
            pdb_path = os.path.join(self.input_dir, pdb)
            command = [
                "docker", "run", "--rm", "--gpus", "all",
                "-v", f"{os.path.abspath(pdb_path)}:/workspace/input.pdb",
                "rfdiffusion",
                "python3", "/workspace/RFdiffusion/protein_mpnn_run.py",
                f"--input {pdb_path}",
                f"--num_sequences {self.config['num_sequences']}",
                f"--temperature {self.config['temperature']}"
            ]
            logger.info("Command: " + " ".join(command))
            subprocess.run(command, check=True)
        logger.info("ProteinMPNN finished.")
