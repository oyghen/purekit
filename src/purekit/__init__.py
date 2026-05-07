__all__ = ("__version__", "core", "meta", "text")

from importlib import metadata

__version__ = metadata.version(__name__)

from purekit import core, meta, text
