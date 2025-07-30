# This is free and unencumbered software released into the public domain.

"""ASIMOV for LlamaIndex: Key/value (KV) stores."""

from ._version import __version__, __version_tuple__
from .base import AsimovKVStore

__all__ = [
    'AsimovKVStore',
    '__version__',
    '__version_tuple__',
]
