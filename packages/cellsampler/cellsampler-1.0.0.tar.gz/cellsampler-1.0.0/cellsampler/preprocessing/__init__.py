import importlib
import os


def __getattr__(name):
    try:
        # Construct the module's full name
        module_name = f"{__name__}.{name}"
        # Dynamically import the module
        return importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise AttributeError(
            f"Module '{name}' not found in 'modules' directory"
        ) from e


def __dir__():
    # Get the path of the current file
    current_dir = os.path.dirname(__file__)
    # List all files in the current directory
    files = os.listdir(current_dir)
    # Filter only .py files and exclude __init__.py
    module_files = [
        f[:-3] for f in files if f.endswith(".py") and f != "__init__.py"
    ]
    # Return the module names
    return module_files
