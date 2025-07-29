"""
VSCode Command Client

A Python client for communicating with VSCode Command Server extension.
"""

from .client import VSCodeHTTPClient

__version__ = "1.0.0"
__author__ = "Sisung Kim"
__email__ = "sisung.kim1@gmail.com"

__all__ = ["VSCodeHTTPClient"] 