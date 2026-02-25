import os
from datetime import datetime

def create_experiment_folder(base_name):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"{timestamp}_{base_name}"

    path = os.path.join("outputs", folder_name)
    os.makedirs(path, exist_ok=True)

    return path
