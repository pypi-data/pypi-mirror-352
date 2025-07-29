import os
import re
from typing import Tuple
from pathlib import Path
import datetime


import ollama

def generate_tests(code_file: Path, code: str, function_name: str) -> Tuple[bool, Path]:
    """
    Generate unit tests for a Python file using the custom Ollama model.
    
    Args:
        code_file: Path to the Python file to generate tests for
        output_file: Path to save the generated tests (default: test_{original_filename})
        
    Returns:
        Tuple of (success, output_file_path)
    """

    # Create the prompt
    prompt = f"""
Generate comprehensive pytest unit tests for the following Python code:

```python
{code}
```

The tests should:
1. Not include the original python code
2. Cover all functions and methods
3. Include edge cases
4. Be well-organized and documented
5. Follow pytest best practices
6. Be ready to run without modifications
"""
    
    # Generate tests using Ollama
    print("\n" + "="* 30 + f" Klara is creating the unittest for {function_name} " + "="*30)
    print(f"Generating tests for {function_name} in {code_file}...")
    print("This may take a moment depending on the size of your code...\n")
    print("="*30 + " Klara's response " + "="*30)
    response = ""
    for chunk in ollama.generate(model='klaradvn:latest', prompt=prompt, stream=True):
        response += chunk['response']
        print(chunk['response'], end='', flush=True)
    # Extract the test code
    generated_content = response
    
    # Find the test code (usually between code blocks)
    test_code_match = re.search(r'```python\s*(.*?)\s*```', generated_content, re.DOTALL)
    
    if test_code_match:
        test_code = test_code_match.group(1)
    else:
        # Just use the full response if no code blocks found, but try to clean it up
        test_code = generated_content
        if not test_code.startswith("import"):
            # Try to find where the code actually starts
            import_match = re.search(r'(import \w+|from \w+ import)', test_code)
            if import_match:
                start_pos = import_match.start()
                test_code = test_code[start_pos:]
    import_statement_function = f"\nfrom {code_file.parent.name}.{code_file.stem} import {function_name}\n\n"
    test_code = import_statement_function + test_code
    # Determine output file name if not specified
    output_file = code_file.parent.parent / 'tests' / f"test_{code_file.stem}.py"
    
    # Write the test code to file
    # try:
    with open(str(output_file), "a") as f:
        f.write(test_code)
    print(f"Tests written to {output_file}")
    return True, output_file
    # except Exception as e:
    #     print(f"Error writing test file: {e}")
    #     return False, ""

