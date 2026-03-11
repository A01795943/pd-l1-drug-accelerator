import shutil
import os

if os.path.exists("outputs"):
    shutil.rmtree("outputs")

os.makedirs("outputs/models", exist_ok=True)
os.makedirs("outputs/plots", exist_ok=True)

print("Outputs cleaned")