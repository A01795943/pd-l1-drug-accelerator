"""
Módulo para predecir estructuras usando AlphaFold3
"""

import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict
import pandas as pd
import textwrap
import re

class AlphaFold3Predictor:
    """
    Clase para predecir estructuras usando AlphaFold3
    """
    
    def __init__(
        self,
        alphafold3_path: Optional[str] = None,
        model_params_dir: Optional[str] = None,
        db_dir: Optional[str] = None,
        use_api: bool = False
    ):
        """
        Inicializa el predictor de AlphaFold3
        
        Args:
            alphafold3_path: Ruta al script de AlphaFold3
            model_params_dir: Directorio con los parámetros del modelo
            use_api: Si True, usa una API (si está disponible)
        """
        self.alphafold3_path = alphafold3_path
        self.model_params_dir = model_params_dir
        self.db_dir = Path(db_dir).expanduser().resolve() if db_dir else None
        self.use_api = use_api
        
        if not alphafold3_path:
            # Intentar encontrar el script en el PATH
            import shutil
            af3_path = shutil.which("alphafold3")
            if af3_path:
                self.alphafold3_path = af3_path
            else:
                print("ADVERTENCIA: AlphaFold3 no encontrado en PATH")
                print("Instala AlphaFold3 desde: https://github.com/google-deepmind/alphafold3")
    


    def _safe_id(self, s: str) -> str:
        s = str(s).strip()
        s = s.rstrip(",")  # quita comas finales como en tu error
        # reemplaza cualquier cosa rara por guion bajo (incluye =, espacios, etc.)
        s = re.sub(r"[^A-Za-z0-9_.-]+", "_", s)
        return s

    def predict_structure(
        self,
        sequence: str,
        sequence_id: str,
        output_dir: Path = Path("data/processed/alphafold3_outputs"),
        json_input: Optional[Dict] = None
    ) -> Dict:
        """
        Predice la estructura 3D de una secuencia
        
        Args:
            sequence: Secuencia de aminoácidos
            sequence_id: Identificador único para la secuencia
            output_dir: Directorio de salida
            json_input: Input JSON personalizado (opcional)
            
        Returns:
            Dict con información de la predicción
        """
        sequence_id = self._safe_id(sequence_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if json_input:
            return self._predict_from_json(json_input, sequence_id, output_dir)
        else:
            return self._predict_from_sequence(sequence, sequence_id, output_dir)
    
    def _predict_from_sequence(self, sequence: str, sequence_id: str, output_dir: Path) -> Dict:
        if not self.alphafold3_path:
            raise ValueError("alphafold3_path debe especificarse")

        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        json_input = {
            "name": str(sequence_id),
            "modelSeeds": [1],                 # ✅ requerido (al menos 1) :contentReference[oaicite:2]{index=2}
            "sequences": [                     # ✅ nombre correcto :contentReference[oaicite:3]{index=3}
                {
                    "protein": {
                        "id": "A",
                        "sequence": str(sequence),
                        "templates": []        # opcional, pero evita algunos defaults raros
                    }
                }
            ],
            "dialect": "alphafold3",           # ✅ requerido :contentReference[oaicite:4]{index=4}
            "version": 4                       # ✅ el doc actual usa 4 (y describe versiones 1–4) :contentReference[oaicite:5]{index=5}
        }

        return self._predict_from_json(json_input, sequence_id, output_dir)


    def _predict_from_sequence_oldjeje(
        self,
        sequence: str,
        sequence_id: str,
        output_dir: Path
    ) -> Dict:
        """Predice estructura desde una secuencia de aminoácidos"""
        sequence_id = self._safe_id(sequence_id)
        if not self.alphafold3_path:
            raise ValueError("alphafold3_path debe especificarse")
        
        # Crear input JSON para AlphaFold3
        json_input = {
            "molecules": [
                {
                    "name": sequence_id,
                    "sequence": sequence,
                    "type": "protein"
                }
            ]
        }
        
        json_file = output_dir / f"input_{sequence_id}.json"
        with open(json_file, 'w') as f:
            json.dump(json_input, f, indent=2)
        
        return self._predict_from_json(json_input, sequence_id, output_dir)

    def _predict_from_json(self, json_input: Dict, sequence_id: str, output_dir: Path) -> Dict:
        if not self.alphafold3_path:
            raise ValueError("alphafold3_path debe especificarse")

        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        json_file = (output_dir / f"input_{sequence_id}.json").resolve()
        with open(json_file, "w") as f:
            json.dump(json_input, f, indent=2)

        cmd = [
            "python", str(Path(self.alphafold3_path).resolve()),
            "--json_path", str(json_file),
            "--output_dir", str(output_dir),
            "--model_dir", str(Path(self.model_params_dir).resolve() if self.model_params_dir else ""),
            "--db_dir", str(self.db_dir)
        ]

        stdout_log = output_dir / f"{sequence_id}.stdout.log"
        stderr_log = output_dir / f"{sequence_id}.stderr.log"

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        stdout_log.write_text(result.stdout or "", encoding="utf-8")
        stderr_log.write_text(result.stderr or "", encoding="utf-8")

        if result.returncode != 0:
            print("\n" + "="*90)
            print(f"[AlphaFold3 ERROR] sequence_id={sequence_id}")
            print("CMD:", " ".join(cmd))
            print(f"STDOUT log: {stdout_log}")
            print(f"STDERR log: {stderr_log}")
            print("-"*90)
            print(result.stderr or result.stdout or f"returncode={result.returncode}")
            print("="*90 + "\n")

            return {
                "sequence_id": sequence_id,
                "status": "error",
                "returncode": result.returncode,
                "error_summary": (result.stderr or result.stdout or "")[:500],
                "stdout_log": str(stdout_log),
                "stderr_log": str(stderr_log),
                "json_file": str(json_file),
                "output_dir": str(output_dir),
            }

        # ✅ ÉXITO: regresar algo (antes aquí regresaba None)
        pdb_files = list(output_dir.rglob("*.pdb"))
        mmcif_files = list(output_dir.rglob("*.cif")) + list(output_dir.rglob("*.mmcif"))

        return {
            "sequence_id": sequence_id,
            "status": "success",
            "returncode": result.returncode,
            "json_file": str(json_file),
            "stdout_log": str(stdout_log),
            "stderr_log": str(stderr_log),
            "output_dir": str(output_dir),
            "pdb_file": str(pdb_files[0]) if pdb_files else None,
            "mmcif_file": str(mmcif_files[0]) if mmcif_files else None,
        }



    def _predict_from_json_oldjeje(self, json_input: Dict, sequence_id: str, output_dir: Path) -> Dict:
        if not self.alphafold3_path:
            raise ValueError("alphafold3_path debe especificarse")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        sequence_id = self._safe_id(sequence_id)
        json_file = output_dir / f"input_{sequence_id}.json"
        with open(json_file, "w") as f:
            json.dump(json_input, f, indent=2)

        cmd = [
            "python", str(self.alphafold3_path),
            "--json_path", str(json_file),
            "--output_dir", str(output_dir),
            "--model_dir", str(self.model_params_dir or ""),
            "--db_dir", str(self.db_dir)
        ]

        # Archivos de log por secuencia (para ver TODO sin recortes)
        stdout_log = output_dir / f"{sequence_id}.stdout.log"
        stderr_log = output_dir / f"{sequence_id}.stderr.log"

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=output_dir.parent
            )

            # Guardar logs (aunque sea success)
            stdout_log.write_text(result.stdout or "", encoding="utf-8")
            stderr_log.write_text(result.stderr or "", encoding="utf-8")

            pdb_files = list(output_dir.glob(f"*{sequence_id}*.pdb"))
            output_pdb = pdb_files[0] if pdb_files else None

            return {
                "sequence_id": sequence_id,
                "status": "success",
                "pdb_file": str(output_pdb) if output_pdb else None,
                "json_file": str(json_file),
                "stdout_log": str(stdout_log),
                "stderr_log": str(stderr_log),
            }

        except subprocess.CalledProcessError as e:
            # Guardar TODO en archivos
            (stdout_log).write_text(e.stdout or "", encoding="utf-8")
            (stderr_log).write_text(e.stderr or "", encoding="utf-8")

            # Imprimir completo en output de la celda (con separadores)
            print("\n" + "="*90)
            print(f"[AlphaFold3 ERROR] sequence_id={sequence_id}")
            print("CMD:", " ".join(cmd))
            print(f"STDOUT log: {stdout_log}")
            print(f"STDERR log: {stderr_log}")
            print("-"*90)
            if e.stdout:
                print("[STDOUT]")
                print(e.stdout)
            if e.stderr:
                print("[STDERR]")
                print(e.stderr)
            print("="*90 + "\n")

            # Resumen corto para el DF (sin recortes)
            err_text = e.stderr or e.stdout or str(e)
            err_summary = textwrap.shorten(err_text.replace("\n", " "), width=250, placeholder="...")

            return {
                "sequence_id": sequence_id,
                "status": "error",
                "returncode": e.returncode,
                "error_summary": err_summary,
                "stdout_log": str(stdout_log),
                "stderr_log": str(stderr_log),
            }

    def predict_multiple_sequences(
        self,
        sequences: List[str],
        sequence_ids: Optional[List[str]] = None,
        output_dir: Path = Path("data/processed/alphafold3_outputs")
    ) -> pd.DataFrame:
        """
        Predice estructuras para múltiples secuencias
        
        Args:
            sequences: Lista de secuencias de aminoácidos
            sequence_ids: Lista opcional de IDs (si no se proporciona, se generan)
            output_dir: Directorio de salida
            
        Returns:
            DataFrame con los resultados
        """
        if sequence_ids is None:
            sequence_ids = [f"seq_{i+1}" for i in range(len(sequences))]
        
        results = []
        
        for seq, seq_id in zip(sequences, sequence_ids):
            print(f"Prediciendo estructura para {seq_id}...")
            result = self.predict_structure(
                sequence=seq,
                sequence_id=seq_id,
                output_dir=output_dir
            )
            results.append(result)
        
        df = pd.DataFrame(results)
        output_file = output_dir / "alphafold3_predictions.csv"
        df.to_csv(output_file, index=False)
        
        return df
    
def validate_mpnn_sequences_with_alphafold3(
        mpnn_sequences_df: pd.DataFrame,
        predictor: AlphaFold3Predictor,
        output_dir: Path = Path("data/processed/alphafold3_validation")
    ) -> pd.DataFrame:
        """
        Valida secuencias generadas por Protein MPNN usando AlphaFold3
        
        Compara las estructuras predichas por AlphaFold3 con las estructuras
        originales usadas por Protein MPNN para verificar que las secuencias
        se plieguen correctamente.
        
        Args:
            mpnn_sequences_df: DataFrame con secuencias de Protein MPNN
            predictor: Instancia de AlphaFold3Predictor
            output_dir: Directorio de salida
            
        Returns:
            DataFrame con resultados de validación
        """
        sequences = mpnn_sequences_df['sequence'].tolist()
        sequence_ids = mpnn_sequences_df['sequence_id'].tolist()
        
        print(f"Validando {len(sequences)} secuencias con AlphaFold3...")
        
        validation_df = predictor.predict_multiple_sequences(
            sequences=sequences,
            sequence_ids=sequence_ids,
            output_dir=output_dir
        )
        print("mpnn_sequences_df cols:", mpnn_sequences_df.columns.tolist())
        print("validation_df cols:", validation_df.columns.tolist())
        print("validation_df index name:", validation_df.index.name)
        print("validation_df head:\n", validation_df.head(3))

        # --- Ensure validation_df has sequence_id ---
        if "sequence_id" not in validation_df.columns:
            # If it's the index, move it to a column
            if validation_df.index.name == "sequence_id":
                validation_df = validation_df.reset_index()
            else:
                # Common alternative names
                for alt in ("id", "seq_id", "name", "header"):
                    if alt in validation_df.columns:
                        validation_df = validation_df.rename(columns={alt: "sequence_id"})
                        break

        # If still missing, fail with a clear error
        if "sequence_id" not in validation_df.columns:
            raise KeyError(
                "validation_df no contiene 'sequence_id'. "
                f"Columnas: {validation_df.columns.tolist()} | index.name={validation_df.index.name}"
            )


        # Combinar con información original
        combined_df = mpnn_sequences_df.merge(
            validation_df,
            left_on='sequence_id',
            right_on='sequence_id',
            how='left'
        )
        
        output_file = output_dir / "mpnn_alphafold3_validation.csv"
        combined_df.to_csv(output_file, index=False)
        
        return combined_df    
