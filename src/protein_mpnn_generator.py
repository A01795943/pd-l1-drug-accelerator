"""
Módulo para generar secuencias usando Protein MPNN
"""

import subprocess
import json
from pathlib import Path
from typing import Optional, List
import pandas as pd
import shutil


class ProteinMPNNGenerator:
    """
    Clase para generar secuencias usando Protein MPNN vía CLI
    """

    def __init__(
        self,
        mpnn_path: Optional[str] = None,
        use_api: bool = False,
        api_key: Optional[str] = None
    ):
        """
        Inicializa el generador de Protein MPNN
        
        Args:
            mpnn_path: Ruta al ejecutable de Protein MPNN (si se usa localmente)
            use_api: Si True, usa la API de Levitate Bio
            api_key: API key para Levitate Bio (si use_api=True)
        """
        self.use_api = use_api
        self.api_key = api_key

        if not use_api:
            # Intentar detectar el CLI automáticamente si no se da mpnn_path
            if mpnn_path:
                self.mpnn_path = mpnn_path
            else:
                self.mpnn_path = shutil.which("protein_mpnn")  # Busca el ejecutable en PATH

            if not self.mpnn_path:
                raise ValueError(
                    "No se encontró el ejecutable de Protein MPNN. "
                    "Especifica mpnn_path o asegúrate de que 'protein_mpnn' esté en el PATH."
                )

    def generate_sequences(
        self,
        pdb_file: str,
        num_designs: int = 10,
        sampling_temp: float = 0.1,
        fixed_positions: Optional[List[int]] = None,
        model_name: str = "v_48_020",
        output_dir: Path = Path("data/processed/mpnn_outputs")
    ) -> pd.DataFrame:
        """
        Genera secuencias usando Protein MPNN
        
        Args:
            pdb_file: Ruta al archivo PDB de entrada
            num_designs: Número de secuencias a generar
            sampling_temp: Temperatura de muestreo (0.1 = conservador, 1.0 = diverso)
            fixed_positions: Lista de posiciones de residuos a mantener fijas
            model_name: Versión del modelo (v_48_002, v_48_010, v_48_020, v_48_030)
            output_dir: Directorio de salida
            
        Returns:
            DataFrame con las secuencias generadas
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        if self.use_api:
            return self._generate_via_api(
                pdb_file, num_designs, sampling_temp,
                fixed_positions, model_name, output_dir
            )
        else:
            return self._generate_via_cli(
                pdb_file, num_designs, sampling_temp,
                fixed_positions, model_name, output_dir
            )
        
    def _generate_via_cli(
        self,
        pdb_file: str,
        num_designs: int,
        sampling_temp: float,
        fixed_positions: Optional[List[int]],
        model_name: str,
        output_dir: Path
    ) -> pd.DataFrame:
        import subprocess
        import shutil
        from pathlib import Path

        pdb_path = Path(pdb_file)
        pdb_name = pdb_path.name
        pdb_stem = pdb_path.stem

        # Output folders
        out_folder = Path(output_dir) / "mpnn_output"
        seqs_folder = out_folder / "seqs"
        input_pdb_dir = out_folder / "input_pdb"

        seqs_folder.mkdir(parents=True, exist_ok=True)
        input_pdb_dir.mkdir(parents=True, exist_ok=True)

        # 🔥 Copiar PDB a carpeta limpia
        clean_pdb = input_pdb_dir / pdb_name
        shutil.copy(pdb_path, clean_pdb)

        # 🔥 Comando: SOLO el nombre del archivo
        cmd = [
            str(self.mpnn_path),
            "--pdb-path", pdb_name,
            "--num-seq-per-target", str(num_designs),
            "--sampling-temp", str(sampling_temp),
            "--model-name", model_name,
            "--out-folder", str(out_folder),
        ]

        if fixed_positions:
            cmd.extend(["--fixed_positions", ",".join(map(str, fixed_positions))])

        try:
            subprocess.run(
                cmd,
                cwd=input_pdb_dir,   # 🔥 CLAVE ABSOLUTA
                capture_output=True,
                text=True,
                check=True
            )

            fasta_file = seqs_folder / f"{pdb_stem}.fa"
            if not fasta_file.exists():
                raise FileNotFoundError(f"No se generó {fasta_file}")

            # Parse FASTA
            sequences = []
            with open(fasta_file) as f:
                current = ""
                for line in f:
                    if line.startswith(">"):
                        if current:
                            sequences.append(current)
                            current = ""
                    else:
                        current += line.strip()
                if current:
                    sequences.append(current)

            df = pd.DataFrame({
                "sequence_id": [f"mpnn_{i+1}" for i in range(len(sequences))],
                "sequence": sequences,
                "pdb_file": pdb_stem,
                "sampling_temp": sampling_temp,
                "model_name": model_name
            })

            csv_file = Path(output_dir) / f"mpnn_sequences_{pdb_stem}.csv"
            df.to_csv(csv_file, index=False)

            return df

        except subprocess.CalledProcessError as e:
            print("❌ ProteinMPNN stderr:\n", e.stderr)
            raise

    def _generate_via_api(
        self,
        pdb_file: str,
        num_designs: int,
        sampling_temp: float,
        fixed_positions: Optional[List[int]],
        model_name: str,
        output_dir: Path
    ) -> pd.DataFrame:
        """Genera secuencias usando la API de Levitate Bio"""
        import requests

        if not self.api_key:
            raise ValueError("api_key requerido para usar la API")

        url = "https://api.levitate.bio/v1/protein-mpnn"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        with open(pdb_file, 'r') as f:
            pdb_content = f.read()

        payload = {
            "pdb_content": pdb_content,
            "num_designs": num_designs,
            "sampling_temp": sampling_temp,
            "model_name": model_name
        }

        if fixed_positions:
            payload["fixed_positions"] = fixed_positions

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()

            result = response.json()

            sequences = []
            for i, seq in enumerate(result.get("sequences", [])):
                sequences.append({
                    "sequence_id": f"mpnn_{i+1}",
                    "sequence": seq,
                    "pdb_file": pdb_file,
                    "sampling_temp": sampling_temp,
                    "model_name": model_name
                })

            df = pd.DataFrame(sequences)
            output_file = output_dir / f"mpnn_sequences_{Path(pdb_file).stem}.csv"
            df.to_csv(output_file, index=False)

            return df

        except requests.exceptions.RequestException as e:
            print(f"Error usando API de Protein MPNN: {e}")
            raise


def generate_sequences_for_multiple_structures(
    generator: ProteinMPNNGenerator,
    pdb_files: List[str],
    num_designs_per_structure: int = 10,
    output_dir: Path = Path("data/processed/mpnn_outputs")
) -> pd.DataFrame:
    """
    Genera secuencias para múltiples estructuras PDB
    """
    all_sequences = []

    for pdb_file in pdb_files:
        print(f"Generando secuencias para {pdb_file}...")
        try:
            df = generator.generate_sequences(
                pdb_file=pdb_file,
                num_designs=num_designs_per_structure,
                output_dir=output_dir
            )
            all_sequences.append(df)
        except Exception as e:
            print(f"Error procesando {pdb_file}: {e}")
            continue

    if all_sequences:
        combined_df = pd.concat(all_sequences, ignore_index=True)
        output_file = output_dir / "all_mpnn_sequences.csv"
        combined_df.to_csv(output_file, index=False)
        return combined_df
    else:
        return pd.DataFrame()
