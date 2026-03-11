# pipeline/run_pipeline.py

import subprocess


def run_step(description, command):

    print("\n===================================")
    print(description)
    print("===================================")

    result = subprocess.run(command, shell=True)

    if result.returncode != 0:
        raise RuntimeError(f"Error ejecutando: {command}")


# Step 1
run_step(
    "STEP 1 - Prepare dataset",
    "python scripts/prepare_dataset.py"
)

# Step 2
run_step(
    "STEP 2 - Generate embeddings",
    "python scripts/generate_embeddings.py"
)

# Step 3
run_step(
    "STEP 3 - Train models",
    "python training/train_model.py"
)

# Step 4
run_step(
    "STEP 4 - Evaluate models",
    "python evaluation/05_evaluate_model.py"
)

# Step 5
run_step(
    "STEP 5 - Filter candidates",
    "python evaluation/04_filter_candidates.py"
)

# Step 6
run_step(
    "STEP 6 - Consistency check",
    "python evaluation/06_consistency_check.py"
)

print("\nPIPELINE COMPLETED SUCCESSFULLY")