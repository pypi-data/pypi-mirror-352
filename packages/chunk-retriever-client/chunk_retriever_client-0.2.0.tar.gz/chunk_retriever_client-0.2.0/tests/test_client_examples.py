import subprocess
import sys
import os
import pytest

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), '../chunk_retriever_client/examples')

EXAMPLES = [
    'basic_usage.py',
    'error_handling.py',
    'advanced_usage.py',
    'docstring_demo.py',
    'uuid_object_usage.py',
]

@pytest.mark.parametrize("script", EXAMPLES)
def test_example_runs(script):
    script_path = os.path.join(EXAMPLES_DIR, script)
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    assert result.returncode == 0, f"Script {script} failed: {result.stderr}" 