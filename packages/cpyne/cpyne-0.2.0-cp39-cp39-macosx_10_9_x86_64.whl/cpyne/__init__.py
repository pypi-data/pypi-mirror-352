"""
Spine Python ctypes binding package init.
"""

from . import spine_bindings as _b

__all__ = []

for name in dir(_b):
    if name.startswith("sp"):
        globals()[name] = getattr(_b, name)
        __all__.append(name)