from .core import Regenerator

__all__ = [
    "Regenerator",
]

from . import _version

__version__ = _version.get_versions()["version"]

from . import _version
__version__ = _version.get_versions()['version']
