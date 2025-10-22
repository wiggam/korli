"""
HTTP Utilities
--------------
Shared HTTP utilities for all services, including SSL context creation
and common session configuration.
"""

from __future__ import annotations

import ssl
from typing import Optional

import aiohttp
import certifi


def create_ssl_context() -> ssl.SSLContext:
    """
    Create SSL context with proper certificate verification using certifi.
    
    This resolves SSL certificate verification issues on macOS and other
    platforms where system certificates may not be properly configured.
    
    Returns
    -------
    ssl.SSLContext
        Configured SSL context with certifi certificates
    """
    return ssl.create_default_context(cafile=certifi.where())


def create_tcp_connector(
    ssl_context: Optional[ssl.SSLContext] = None,
    limit: int = 100,
    limit_per_host: int = 30
) -> aiohttp.TCPConnector:
    """
    Create a configured TCP connector for aiohttp sessions.
    
    Parameters
    ----------
    ssl_context : Optional[ssl.SSLContext]
        SSL context to use. If None, creates one with certifi certificates.
    limit : int
        Total number of simultaneous connections (default: 100)
    limit_per_host : int
        Number of simultaneous connections to one host (default: 30)
        
    Returns
    -------
    aiohttp.TCPConnector
        Configured TCP connector
    """
    if ssl_context is None:
        ssl_context = create_ssl_context()
    
    return aiohttp.TCPConnector(
        ssl=ssl_context,
        limit=limit,
        limit_per_host=limit_per_host
    )

