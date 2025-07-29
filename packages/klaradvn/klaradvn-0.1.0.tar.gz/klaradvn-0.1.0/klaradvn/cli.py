from pathlib import Path
import subprocess
import os
from typing import Annotated

import typer

from klaradvn.build_model import create_model
from klaradvn.extract import extract_function_code
from klaradvn.extract import extract_class
from klaradvn.generate import generate_tests


def test_class(class_: str):
    result = extract_class(Path(os.getcwd()), class_)
    success, test_path = generate_tests(Path(result['file_path']), result['source_code'], class_)
    if success:
        subprocess.run([f"pytest {test_path} --noconftest"], shell=True)

def test_function(function: str):
    code, path = extract_function_code(os.getcwd(), function)
    success, test_path = generate_tests(path, code, function)
    if success:
        subprocess.run([f"pytest {test_path}"], shell=True)


app = typer.Typer()

@app.command()
def create_model():
    """Command that creates local instance of Klara model using OLLAMA. This action should be perfomed before Klara can be used!"""
    create_model()

@app.command()
def test(name: str, class_: Annotated[bool, typer.Option("--class", "-c")] = False, function_: Annotated[bool, typer.Option("--function", '-f')] = False):
    """Command to create the tests for your code. Either the `class` or the `function` option should be provided!"""
    if not class_ and not function_:
        raise ValueError("Either the class option or function option should be provided. You provided nothing.")
    if class_ and function_:
        raise ValueError("Either the class option or function option should be provided. You provided both.")
    if class_:
        test_class(name)
    if function_:
        test_function(name)

if __name__ == "__main__":
    app()
