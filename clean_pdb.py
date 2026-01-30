import sys

def clean_pdb(input_path, output_path):
    # Lista de aminoacidos estandar
    valid_residues = {
        'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
        'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL'
    }
    
    with open(input_path, 'r') as f_in, open(output_path, 'w') as f_out:
        for line in f_in:
            # Solo queremos lineas que empiecen con ATOM
            if line.startswith('ATOM'):
                res_name = line[17:20].strip()
                # Y solo si son aminoacidos reales (no agua, no sodio)
                if res_name in valid_residues:
                    f_out.write(line)
            # Mantenemos el final del archivo
            elif line.startswith('END'):
                f_out.write(line)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python clean_pdb.py input.pdb output.pdb")
    else:
        clean_pdb(sys.argv[1], sys.argv[2])
        print(f"✅ Archivo limpiado guardado en: {sys.argv[2]}")
