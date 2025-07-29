# logmagix/__init__.py
from importlib import metadata

__all__ = ["Logger", "Loader", "Home", "LogLevel", "AutoUpdater", "__version__"]

try:
    __version__ = metadata.version("logmagix")
except metadata.PackageNotFoundError:
    __version__ = "unknown"

def __getattr__(name):
    if name in ("Logger", "Loader", "Home", "LogLevel"):
        from .logger import Logger, Loader, Home, LogLevel
        return locals()[name]
    if name == "AutoUpdater":
        from .updater import AutoUpdater
        return AutoUpdater
    raise AttributeError(f"module {__name__} has no attribute {name}")
