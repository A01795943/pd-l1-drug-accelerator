import subprocess
import logging

class RFdiffusionEngine:
    def __init__(self, config, pdb_path, rf_script):
        """
        config: dict con la sección rfdiffusion de tu YAML
        pdb_path: ruta al PDB descargado
        rf_script: ruta al script de RFdiffusion (run_inference.py)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.pdb_path = pdb_path
        self.rf_script = rf_script

    def run(self):
        self.logger.info("Running RFdiffusion...")

        # --- Extraer configuración de RFdiffusion ---
        rfdiff_cfg = self.config  # ya debe ser self.config['rfdiffusion']

        # --- Hotspots como lista de Hydra ---
        hotspot_items = rfdiff_cfg.get("hotspot", [])
        if hotspot_items:
            # Hydra lista: sin comillas internas
            hotspot_value = "[" + ",".join(hotspot_items) + "]"
        else:
            hotspot_value = "[]"

        # --- Contigs como string simple ---
        contigs_raw = rfdiff_cfg.get("contigs", "")
        contigs_value = contigs_raw  # SIN comillas

        # --- Construir comando final ---
        command = (
            f"PYTHONPATH=/workspace/RFdiffusion python3 {self.rf_script} "
            f"+experiment.name={rfdiff_cfg.get('name','design')} "
            f"+pdb.source={self.pdb_path} "
            f"+rfdiffusion.contigs={contigs_value} "
            f"+rfdiffusion.hotspot={hotspot_value} "
            f"+rfdiffusion.iterations={rfdiff_cfg.get('iterations',10)} "
            f"+rfdiffusion.num_designs={rfdiff_cfg.get('num_designs',1)} "
            f"+rfdiffusion.visual={rfdiff_cfg.get('visual','image')}"
        )

        self.logger.info(f"Running RFdiffusion with command:\n{command}")

        # --- Ejecutar comando ---
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"RFdiffusion failed with error: {e}")
            raise
