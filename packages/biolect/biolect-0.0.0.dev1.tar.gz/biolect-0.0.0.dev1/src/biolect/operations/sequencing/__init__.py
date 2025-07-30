"""Sequencing Framework Initialization

This module provides the initialization logic for the Biolect DSL
sequencing framework.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ─
from . import analysis, encoding, manipulation, search, translation

from .encoding import (
    DECODE_TABLE, ENCODE_TABLE,
    PackedSequence, SequenceBatch, SequenceStream,
    iter_kmers, pack_sequence, unpack_sequence, vectorized_decode
)


__all__ = [
    # ─── constants ───────────────────────────────────────────────────────────
    "DECODE_TABLE", "ENCODE_TABLE",

    # ─── modules ─────────────────────────────────────────────────────────────
    "analysis", "encoding", "manipulation", "search", "translation",

    # ─── classes ─────────────────────────────────────────────────────────────
    "PackedSequence", "SequenceBatch", "SequenceStream",

    # ─── functions ───────────────────────────────────────────────────────────
    "iter_kmers", "pack_sequence", "unpack_sequence", "vectorized_decode"
]