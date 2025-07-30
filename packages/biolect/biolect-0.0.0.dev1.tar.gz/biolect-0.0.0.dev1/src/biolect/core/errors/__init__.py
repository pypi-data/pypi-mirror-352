"""Core Error Framework

This module defines the Biolect DSL's core error-handling mechanisms.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ─
from . import handlers, monadic, recovery, types

from .handlers import ErrorHandler, DefaultErrorHandler

__all__ = [
    # ─── module-level exports ────────────────────────────────────────────────
    "handlers", "monadic", "recovery", "types"

    # ─── class-level exports ─────────────────────────────────────────────────

    # error handlers
    "ErrorHandler", "DefaultErrorHandler"

    # monadic error handling

    # error recovery
    "Recovery",

    # error typedefs
    "SequencingError"
]
