# This is free and unencumbered software released into the public domain.

"""ASIMOV for LlamaIndex: Document stores."""

from ._version import __version__, __version_tuple__
from .base import AsimovDocumentStore

__all__ = [
    'AsimovDocumentStore',
    '__version__',
    '__version_tuple__',
]
