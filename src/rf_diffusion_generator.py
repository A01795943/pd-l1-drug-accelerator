"""
Módulo para generar estructuras proteicas usando RF Diffusion (NVIDIA NIM API)
"""

import requests
import json
from pathlib import Path
from typing import Optional, Dict, List
import time


class RFDiffusionGenerator:
    """
    Clase para interactuar con la API de NVIDIA NIM RFdiffusion
    """
    
    def __init__(self, api_key: str, base_url: str = "https://health.api.nvidia.com/v1/biology/ipd/rfdiffusion"):
        """
        Inicializa el generador de RF Diffusion
        
        Args:
            api_key: API key de NVIDIA Build
            base_url: URL base de la API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_structure(
        self,
        contigs: str,
        input_pdb: Optional[str] = None,
        hotspot_res: Optional[List[int]] = None,
        diffusion_steps: int = 50,
        output_dir: Path = Path("data/processed/rfdiffusion_outputs")
    ) -> Dict:
        """
        Genera una estructura proteica usando RF Diffusion
        
        Args:
            contigs: Especificación de contigs (ej: "A1-100" para generar 100 residuos)
            input_pdb: Ruta opcional a un archivo PDB de template
            hotspot_res: Lista opcional de residuos hotspot
            diffusion_steps: Número de pasos de difusión (default: 50)
            output_dir: Directorio donde guardar los resultados
            
        Returns:
            Dict con información de la estructura generada
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        payload = {
            "contigs": contigs,
            "diffusion_steps": diffusion_steps
        }
        
        if input_pdb:
            # Leer el archivo PDB si se proporciona
            with open(input_pdb, 'r') as f:
                pdb_content = f.read()
            payload["input_pdb"] = pdb_content

       
        if hotspot_res:
            print(f"hotspot_res: {hotspot_res}")
            payload["hotspot_res"] = hotspot_res

        
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                headers=self.headers,
                json=payload,
                timeout=300  # 5 minutos timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Guardar el resultado
            output_file = output_dir / f"rfdiffusion_{int(time.time())}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            # Si hay un PDB en la respuesta, guardarlo
            if "pdb" in result:
                pdb_file = output_dir / f"rfdiffusion_{int(time.time())}.pdb"
                with open(pdb_file, 'w') as f:
                    f.write(result["pdb"])
                result["pdb_file"] = str(pdb_file)
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error al generar estructura con RF Diffusion: {e}")
            if hasattr(e.response, 'text'):
                print(f"Respuesta del servidor: {e.response.text}")
            raise
    
    def generate_pdl1_binder(
        self,
        pdl1_pdb: str,
        binder_length: int = 50,
        hotspot_residues: Optional[List[int]] = None,
        output_dir: Path = Path("data/processed/rfdiffusion_outputs")
    ) -> Dict:
        """
        Genera un ligando/binder para PD-L1 usando RF Diffusion
        
        Args:
            pdl1_pdb: Ruta al archivo PDB de PD-L1
            binder_length: Longitud del binder a generar
            hotspot_residues: Residuos específicos de PD-L1 a targetear
            output_dir: Directorio de salida
            
        Returns:
            Dict con la estructura del binder generado
        """
        # Contigs para generar un binder de longitud específica
        #contigs = f"A1-{binder_length}"
        #contigs = f"B1-{binder_length}"
        #contigs = f"A18-374/B1-{binder_length}"
        contigs = f"A1-117/{binder_length}"

        return self.generate_structure(
            contigs=contigs,
            input_pdb=pdl1_pdb,
            hotspot_res=hotspot_residues,
            output_dir=output_dir
        )


def generate_multiple_structures(
    generator: RFDiffusionGenerator,
    contigs_list: List[str],
    output_dir: Path = Path("data/processed/rfdiffusion_outputs"),
    delay: float = 2.0
) -> List[Dict]:
    """
    Genera múltiples estructuras con un delay entre requests
    
    Args:
        generator: Instancia de RFDiffusionGenerator
        contigs_list: Lista de especificaciones de contigs
        output_dir: Directorio de salida
        delay: Delay en segundos entre requests
        
    Returns:
        Lista de resultados
    """
    results = []
    
    for i, contigs in enumerate(contigs_list):
        print(f"Generando estructura {i+1}/{len(contigs_list)}: {contigs}")
        try:
            result = generator.generate_structure(
                contigs=contigs,
                output_dir=output_dir
            )
            results.append(result)
            
            if i < len(contigs_list) - 1:
                time.sleep(delay)  # Evitar rate limiting
                
        except Exception as e:
            print(f"Error generando estructura {i+1}: {e}")
            results.append({"error": str(e)})
    
    return results
