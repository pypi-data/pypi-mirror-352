# This is free and unencumbered software released into the public domain.

"""ASIMOV for LlamaIndex: Readers."""

from ._version import __version__, __version_tuple__
from .base import AsimovReader

__all__ = [
    'AsimovReader',
    '__version__',
    '__version_tuple__',
]
