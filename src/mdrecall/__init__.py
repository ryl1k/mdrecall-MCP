"""Local MCP server over a markdown knowledge vault."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mdrecall")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
