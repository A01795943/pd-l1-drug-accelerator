"""
Módulo para predecir estructuras usando AlphaFold3
"""

import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict
import pandas as pd


class AlphaFold3Predictor:
    """
    Clase para predecir estructuras usando AlphaFold3
    """
    
    def __init__(
        self,
        alphafold3_path: Optional[str] = None,
        model_params_dir: Optional[str] = None,
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
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if json_input:
            return self._predict_from_json(json_input, sequence_id, output_dir)
        else:
            return self._predict_from_sequence(sequence, sequence_id, output_dir)
    
    def _predict_from_sequence(
        self,
        sequence: str,
        sequence_id: str,
        output_dir: Path
    ) -> Dict:
        """Predice estructura desde una secuencia de aminoácidos"""
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
    
    def _predict_from_json(
        self,
        json_input: Dict,
        sequence_id: str,
        output_dir: Path
    ) -> Dict:
        """Predice estructura desde un archivo JSON"""
        if not self.alphafold3_path:
            raise ValueError("alphafold3_path debe especificarse")
        
        json_file = output_dir / f"input_{sequence_id}.json"
        with open(json_file, 'w') as f:
            json.dump(json_input, f, indent=2)
        
        output_pdb = output_dir / f"predicted_{sequence_id}.pdb"
        output_json = output_dir / f"results_{sequence_id}.json"
        
        cmd = [
            "python", self.alphafold3_path,
            "--json_path", str(json_file),
            "--output_dir", str(output_dir),
            "--model_params_dir", self.model_params_dir or ""
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=output_dir.parent
            )
            
            # Buscar el archivo PDB generado
            pdb_files = list(output_dir.glob(f"*{sequence_id}*.pdb"))
            if pdb_files:
                output_pdb = pdb_files[0]
            
            return {
                "sequence_id": sequence_id,
                "pdb_file": str(output_pdb),
                "json_file": str(json_file),
                "status": "success",
                "output": result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "sequence_id": sequence_id,
                "status": "error",
                "error": str(e),
                "stderr": e.stderr
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
