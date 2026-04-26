from __future__ import annotations

from importlib import import_module


GENERATOR_REGISTRY = {
    "curriculum": "repo_generators.curriculum",
}


def load_generator(generator_id: str):
    module_path = GENERATOR_REGISTRY.get(generator_id)
    if not module_path:
        raise ValueError(f"unknown generator: {generator_id}")
    module = import_module(module_path)
    if not hasattr(module, "generate"):
        raise ValueError(f"generator module missing generate(): {module_path}")
    return module
