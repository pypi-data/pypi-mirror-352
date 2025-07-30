"""Operations Framework Initialization

This module provides the initialization logic for the Biolect DSL's
operations framework at a high level.
"""
from . import (
    alignment, analysis, annotation, phylogenetics,
    sequencing, utilities, visualization
)

from .sequencing import (
    PackedSequence, SequenceStream, SequenceBatch,
    pack_sequence, unpack_sequence, vectorized_decode
)

__all__ = [
    # ─── module-level exports ────────────────────────────────────────────────
    "alignment", "analysis", "annotation", "phylogenetics",
    "sequencing", "utilities", "visualization",

    # ─── class-level exports ─────────────────────────────────────────────────
    "PackedSequence", "SequenceStream", "SequenceBatch",

    # ─── function-level exports ──────────────────────────────────────────────
    "pack_sequence", "unpack_sequence", "vectorized_decode"
]