"""MCP OCR MINI: A production-grade OCR server built using MCP (Model Context Protocol)."""

__version__ = "0.1.2"

from .server import mcp, perform_ocr, get_supported_languages

__all__ = ["mcp", "perform_ocr", "get_supported_languages"]
