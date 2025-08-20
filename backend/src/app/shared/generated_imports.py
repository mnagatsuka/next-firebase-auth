"""Utility to handle generated code imports."""

import sys
from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=1)
def setup_generated_imports() -> Path:
    """
    Set up the generated code path for imports.
    
    This function ensures that generated FastAPI models are importable
    from anywhere in the application.
    
    Returns:
        Path: The generated code directory path
    """
    # Calculate path relative to this file
    current_file = Path(__file__)
    generated_dir = current_file.parent.parent / "generated" / "src"
    
    # Add to Python path if not already present
    generated_str = str(generated_dir)
    if generated_str not in sys.path:
        sys.path.insert(0, generated_str)
    
    return generated_dir


# Initialize on import
setup_generated_imports()