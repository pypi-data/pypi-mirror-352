import importlib
from pathlib import Path

from battkit.logging_config import logger
from battkit.data.test_schema.base import TestSchema


# Hides non-specified functions from auto-import
__all__ = [
    "TestSchema", "TEST_SCHEMA_REGISTRY", "register_test_schema", "load_test_schema"
]


# Global registry
TEST_SCHEMA_REGISTRY = {}

def register_test_schema(name: str, module_path: str, exists_ok=False):
    """Registers a custom test schema by name and module path."""
    if name in TEST_SCHEMA_REGISTRY and not exists_ok:
        raise ValueError(f"{name} already exists in the TEST_SCHEMA_REGISTRY")
    TEST_SCHEMA_REGISTRY[name] = module_path

def load_test_schema(name: str) -> TestSchema:
    """Dynamically loads the specified TestSchema class from the registry."""
    if not name in TEST_SCHEMA_REGISTRY:
        raise ValueError(f"{name} does not exist in the TEST_SCHEMA_REGISTRY. Custom TestSchema subclasses must first be registered.")
    
    module_path = TEST_SCHEMA_REGISTRY[name]

    # Dynamically import module
    spec = importlib.util.spec_from_file_location(f"{name}Schema", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Ensure the module contains a valid TestSchema subclass
    for attr in dir(module):
        cls = getattr(module, attr)
        if isinstance(cls, type) and issubclass(cls, TestSchema) and cls is not TestSchema:
            return cls()
        
    raise ValueError(f"No valid TestSchema subclass with name \'{name}\' found in {module_path}.")


# Register built-in converters
DEFAULT_TEST_SCHEMAS = {
    "TimeSeries": str(Path(__file__).parent / "time_series.py"),
    "Frequency": str(Path(__file__).parent / "frequency.py"),
}

for name, path in DEFAULT_TEST_SCHEMAS.items():
    register_test_schema(name, path)