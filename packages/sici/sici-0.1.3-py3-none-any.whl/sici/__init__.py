# sici/__init__.py
try:
    from importlib.metadata import version
    __version__ = version("sici")
except Exception:
    __version__ = "0.1.0"  # fallback
