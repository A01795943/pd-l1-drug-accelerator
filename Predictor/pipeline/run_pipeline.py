import subprocess
import os
import sys

def run_step(description, command):
    print("\n" + "="*40)
    print(f"🚀 {description}")
    print("="*40)

    # Ejecutamos el comando
    result = subprocess.run(command, shell=True)

    if result.returncode != 0:
        print(f"\n❌ ERROR CRÍTICO: El {description} falló.")
        sys.exit(1)

# Asegurarse de que el script se ejecute desde la raíz del proyecto
if os.path.basename(os.getcwd()) == "pipeline":
    os.chdir("..")

# --- FLUJO PRINCIPAL ---

# Step 0 - Limpieza inicial (Opcional pero recomendado)
run_step(
    "STEP 0 - Cleaning previous outputs",
    "python3 scripts/clean_outputs.py"
)

# Step 1 - Preparar CSV
run_step(
    "STEP 1 - Prepare dataset",
    "python3 scripts/prepare_dataset.py"
)

# Step 2 - Generar embeddings con ESM-2
# Usamos el script dedicado para esto
run_step(
    "STEP 2 - Generate embeddings",
    "python3 scripts/generate_embeddings.py"
)

# Step 3 - Entrenamiento de modelos
# Ajustado a la ruta de tu carpeta de entrenamiento
run_step(
    "STEP 3 - Train models",
    "python3 training/train_model.py"
)

# Step 4 - Evaluación y Métricas
run_step(
    "STEP 4 - Evaluate models",
    "python3 evaluation/05_evaluate_model.py"
)

# Step 5 - Selección de mejores secuencias
run_step(
    "STEP 5 - Filter candidates",
    "python3 evaluation/04_filter_candidates.py"
)

# Step 6 - Verificación de integridad
run_step(
    "STEP 6 - Consistency check",
    "python3 evaluation/06_consistency_check.py"
)

# Step 7 - Generación de gráficos finales (Profesionales)
run_step(
    "STEP 7 - Final Visualization",
    "python3 evaluation/09_plot_professional_candidates.py"
)

print("\n" + "*"*40)
print("🎊 PIPELINE COMPLETED SUCCESSFULLY 🎊")
print("*"*40)