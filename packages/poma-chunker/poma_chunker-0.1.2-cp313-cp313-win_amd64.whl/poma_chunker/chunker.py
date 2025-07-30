from importlib.util import spec_from_file_location, module_from_spec
from importlib.machinery import EXTENSION_SUFFIXES
import os
from .security import ensure_secure_environment

def _load_native(name):
    ensure_secure_environment()
    here = os.path.dirname(__file__)
    for suffix in EXTENSION_SUFFIXES:
        candidate = os.path.join(here, f"{name}{suffix}")
        if os.path.exists(candidate):
            spec = spec_from_file_location(name, candidate)
            mod = module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError(f"Cannot load native module: {name} (tried: {EXTENSION_SUFFIXES})")

_chunker = _load_native("chunker_core")
process = _chunker.process
__all__ = ["process"]