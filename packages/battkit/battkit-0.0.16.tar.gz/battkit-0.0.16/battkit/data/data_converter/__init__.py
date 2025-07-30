
import importlib
from pathlib import Path

from battkit.data.data_converter.base import DataConverter


# Hides non-specified functions from auto-import
__all__ = [
    "DataConverter", "DATA_CONVERTER_REGISTRY", "register_data_converter", "load_data_converter"
]



# Global registry
DATA_CONVERTER_REGISTRY = {}


def register_data_converter(name: str, module_path: str, exists_ok=False):
    """Registers a custom data converter by name and module path."""
    if name in DATA_CONVERTER_REGISTRY and not exists_ok:
        raise ValueError(f"{name} already exists in the DATA_CONVERTER_REGISTRY")
    DATA_CONVERTER_REGISTRY[name] = module_path

def load_data_converter(name: str) -> DataConverter:
    """Dynamically loads the specified DataConverter class from the registry."""

    if not name in DATA_CONVERTER_REGISTRY:
        raise ValueError(f"{name} does not exist in the DATA_CONVERTER_REGISTRY. Custom DataConverter subclasses must first be registered.")
    
    module_path = DATA_CONVERTER_REGISTRY[name]

    # Dynamically import module
    spec = importlib.util.spec_from_file_location(f"{name}DataConverter", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Ensure the module contains a valid DataConverter subclass
    for attr in dir(module):
        cls = getattr(module, attr)
        if isinstance(cls, type) and issubclass(cls, DataConverter) and cls is not DataConverter:
            return cls()
        
    raise ValueError(f"No valid DataConverter subclass with name \'{name}\' found in {module_path}.")


# Register built-in converters
DEFAULT_CONVERTERS = {
    "Neware": str(Path(__file__).parent / "neware.py"),
}

for name, path in DEFAULT_CONVERTERS.items():
    register_data_converter(name, path)