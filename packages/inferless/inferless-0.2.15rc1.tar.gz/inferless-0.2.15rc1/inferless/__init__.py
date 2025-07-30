# __init__.py
from inferless.api import (
    call,
    call_async,
    method,
    Cls,
    response,
    request,
    local_entry_point,
)

__version__ = "0.2.15rc1"
__all__ = [
    "call",
    "call_async",
    "method",
    "Cls",
    "request",
    "response",
    "local_entry_point",
]
