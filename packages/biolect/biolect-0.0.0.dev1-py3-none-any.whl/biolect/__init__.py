"""Biolect

This module initializes the Biolect DSL framework at its highest level.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ─
from . import core, formats, integrations, operations, utilities, visualization

from .operations import (
    PackedSequence, SequenceBatch, SequenceStream,
    pack_sequence, unpack_sequence, vectorized_decode
)


__all__ = [
    # ─── module-level exports ────────────────────────────────────────────────
    "core", "formats", "integrations", "operations", "utilities",
    "visualization",

    # ─── class-level exports ─────────────────────────────────────────────────
    "PackedSequence", "SequenceBatch", "SequenceStream",

    # ─── function-level exports ──────────────────────────────────────────────
    "pack_sequence", "unpack_sequence", "vectorized_decode",

    # ─── object-level exports ────────────────────────────────────────────────
    # ...
]