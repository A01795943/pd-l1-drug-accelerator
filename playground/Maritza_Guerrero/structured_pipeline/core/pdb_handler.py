import os
import requests
from pathlib import Path
from structured_pipeline.utils.logger import setup_logger

logger = setup_logger()

def download_pdb(pdb_code: str, output_dir: str) -> str:
    url = f"https://files.rcsb.org/download/{pdb_code}.pdb"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    pdb_path = os.path.join(output_dir, f"{pdb_code}.pdb")
    logger.info(f"Downloading PDB {pdb_code} from RCSB...")
    
    r = requests.get(url)
    if r.status_code == 200:
        with open(pdb_path, "w") as f:
            f.write(r.text)
        logger.info(f"PDB saved at {pdb_path}")
        return pdb_path
    else:
        raise Exception(f"Failed to download PDB {pdb_code}, status code {r.status_code}")
