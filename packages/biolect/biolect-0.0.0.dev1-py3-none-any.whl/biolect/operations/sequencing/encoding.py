"""Core Encodings

This module defines the encodings that Biolect uses in its
approach to sequence compression.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ─

# standard library imports
from collections.abc import Generator
from typing import Final, Iterator, NamedTuple

# third-party imports
import Bio
import numpy as np

# local imports


# ─── interface ────────────────────────────────────────────────────────── ✦✦ ─

class PackedSequence(NamedTuple):
    data: np.ndarray
    length: int
    ambiguous_positions: dict[int, str] | None


# ─── bit-packing ──────────────────────────────────────────────────────── ✦✦ ─

ENCODE_TABLE = str.maketrans("ATGC", "\x00\x01\x02\x03")
DECODE_TABLE = ["A", "T", "G", "C"]

def pack_sequence(seq: str | Bio.Seq) -> (
    tuple[np.ndarray, dict[int, str] | None]
):
    """Pack a sequence of DNA nucleobases with ambiguity extraction."""
    cleaned = []
    ambiguous = {}

    for i, base in enumerate(seq.upper()):
        if base in "ATGC":
            cleaned.append(ord(base.translate(ENCODE_TABLE)))
        else:
            # Use "A" as a plaecholder, and track the base.
            cleaned.append(0)
            ambiguous[i] = base

    # ─── pack 4 bases per byte ───────────────────────────────────────────────
    packed_length = (len(cleaned) + 3) // 4
    packed = np.zeros(packed_length, dtype=np.uint8)

    for i, base_code in enumerate(cleaned):
        byte_idx = i // 4
        bit_offset = (i % 4) * 2
        packed[byte_idx] |= base_code << bit_offset

    return packed, ambiguous if ambiguous else None


def unpack_sequence(packed_seq: PackedSequence, start: int, end: int) -> str:
    """Unpack a bit-packed subsequence into string representation."""
    result = []

    for pos in range(start, min(end, packed_seq.length)):
        # Check for ambiguous base.
        if packed_seq.ambiguous_positions and (
            pos in packed_seq.ambiguous_positions
        ):
            result.append(packed_seq.ambiguous_positions[pos])
            continue

        # Extract from packed data
        byte_idx = pos // 4
        bit_offset = (pos % 4) * 2
        base_code = (packed_seq.data[byte_idx] >> bit_offset) & 0b11
        result.append(DECODE_TABLE[base_code])

    return "".join(result)


def vectorized_decode(packed_seq: PackedSequence) -> str:
    """High-performance full-sequence decode using NumPy."""
    if packed_seq.length == 0:
        return ""

    # Expand packed bytes to individual bases.
    expanded = np.zeros(packed_seq.length, dtype=np.uint8)

    for i in range(packed_seq.length):
        byte_idx = i // 4
        bit_offset = (i % 4) * 2
        expanded[i] = (packed_seq.data[byte_idx] >> bit_offset) & 0b11

    base_chars = np.array(DECODE_TABLE, dtype="U1")[expanded]
    result = "".join(base_chars)

    # Apply ambiguous base substitutions.
    if packed_seq.ambiguous_positions:
        result_list = list(result)
        for pos, ambiguous_base in packed_seq.ambiguous_positions.items():
            if pos < len(result_list):
                result_list[pos] = ambiguous_base
        result = "".join(result_list)

    return result


def iter_kmers(packed_seq: PackedSequence, k: int) -> (
    Generator[str, None, None]
):
    """Memory-efficient k-mer generation."""
    if packed_seq.length < k:
        return

    # Use a "sliding window" approach.
    window = unpack_sequence(packed_seq, 0, k)
    yield window

    for i in range(1, packed_seq.length - k + 1):
        # "Slide" the window by one position.
        new_pos = i + k - 1
        
        if packed_seq.ambiguous_positions and (
            new_pos in packed_seq.ambiguous_positions
        ):
            new_base = packed_seq.ambiguous_positions[new_pos]
        else:
            byte_idx = new_pos // 4
            bit_offset = (new_pos % 4) * 2
            base_code = (packed_seq.data[byte_idx] >> bit_offset) & 0b11
            new_base = DECODE_TABLE[base_code]

        window = window[1:] + new_base
        yield window

class SequenceStream:
    def __init__(self, file_handle):
        self.file_handle = file_handle
        self._buffer = bytearray(8192)
        
    
    def iter_sequences(self) -> Generator[PackedSequence, None, None]:
        """Yield packed sequences from a FASTA stream."""
        current_header = None
        sequence_parts = []

        for line in self.file_handle:
            line = line.strip()
            if line.startswith(">"):
                if current_header and sequence_parts:
                    # Process accumulated sequence
                    full_seq = "".join(sequence_parts)
                    packed_data, ambiguous = pack_sequence(full_seq)

                    yield PackedSequence(
                        data=packed_data,
                        length=len(full_seq),
                        ambiguous_positions=ambiguous
                    )

                current_header = line[1:]
                sequence_parts = []
            else:
                sequence_parts.append(line)
            
        # Handle final sequence
        if current_header and sequence_parts:
            full_seq = "".join(sequence_parts)
            packed_data, ambiguous = pack_sequence(full_seq)
            
            yield PackedSequence(
                data=packed_data,
                length=len(full_seq),
                ambiguous_positions=ambiguous
            )


class SequenceBatch:
    """Process multiple sequences efficiently."""

    def __init__(self, batch_size: int = 1000) -> None:
        self.batch_size = batch_size
        self._sequence_buffer = []


    def process_batch(self, sequences: list[PackedSequence]) -> Iterator[str]:
        """Vectorized processing of a sequence batch."""
        # Sort by length for better cache behavior.
        sorted_seqs = sorted(sequences, key=lambda s: s.length)

        for seq in sorted_seqs:
            yield vectorized_decode(seq)

    