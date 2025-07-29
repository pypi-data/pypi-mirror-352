import os
from pathlib import Path


def create_model() -> None:
    """Create the python-test-generator model using a temporary Modelfile"""
 
    print("Creating klaradvn model")
    p = Path(__file__).parent / 'template.modelfile'
    os.system(f"ollama create klaradvn -f {p}")
    print("Model created successfully!")