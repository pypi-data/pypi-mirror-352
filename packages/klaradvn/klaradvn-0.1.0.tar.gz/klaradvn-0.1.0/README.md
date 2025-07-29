# KLARAVDN

Klaravdn is a python library, named after Klara Dan Von Neumann, the famous revolutionary computer scientist/computer programmer.
The library is a wrapper around ollama and aims to automate writing unit tests for your python code.

## Installation

The package is still under active development and not yet published on the PyPI

To run to code under development. Clone the repository to your local computer, navigate to the top level folder of the repo and install with poetry.

```bash
poetry install
```

## Usage

```python
from klaradvn.generate import create_model, generate_tests
from klaradvn.extract import extract_function_code

# Create custom ollama model
create_model()

# Extract python function
function = "another_function"
code, path = extract_function_code(Path(__file__).parent / 'test-package', function)

# Create and run tests
success, test_path = generate_tests(path, code, function)
if success:
    pytest.main(["-x", test_path])
```

## Development roadmap
Steps:
1. Get it working with generic tests on function
2. Get it working with generic tests on classes
3. Extend functionality to make personalized tests
4. Add feedback of SLM to test_xxx.py 
5. Improve SLM accuracy and performance

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)