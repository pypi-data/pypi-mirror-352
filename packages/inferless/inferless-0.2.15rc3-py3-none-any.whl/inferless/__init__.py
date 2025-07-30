# __init__.py
from inferless.api import (
    call,
    call_async,
    method,
    Cls,
    response,
    request,
    local_entry_point,
    config
)

__version__ = "0.2.15rc3"
__all__ = [
    "call",
    "call_async",
    "method",
    "Cls",
    "request",
    "response",
    "local_entry_point",
    "config"
]
