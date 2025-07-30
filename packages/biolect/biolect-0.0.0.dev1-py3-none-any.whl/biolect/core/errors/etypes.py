"""Error Types

This module defines the Biolect DSL framework's error types.
"""

# standard-libary imports

# third-party imports
# ...

# local imports
# ...


# ─── error type hierarchy ─────────────────────────────────────────────── ✦✦ ─
class BiolectError(Exception):
    """Base exception class for the Biolect DSL framework."""
    pass


class DataFormatError(BiolectError):
    """Base class for all sequence format and structure violations."""
    def __init__(
        self,
        sequence,
        position: int | None = None,
        expected_alphabet: Alphabet | None = None
    ) -> None:
        self.sequence = sequence
        self.position = position
        self.expected_alphabet = expected_alphabet
        super().__init__(f"Formatting error at position {position}.")


class InvalidSequenceError(DataFormatError):
    """Raised when invalid characters are detected in a sequence."""
    def __init__(
        self,
        sequence,
        position: int | None = None,
        expected_alphabet: Alphabet | None = None
    ) -> None:
        self.sequence = sequence
        self.position = position
        self.expected_alphabet = expected_alphabet
        super().__init__(f"Invalid sequence at position {position}.")


class FileFormatError(DataFormatError):
    """Raised when the file format does not match the expected standard."""
    def __init__(self, filepath, expected_format, detected_format=None):
        self.filepath = filepath
        self.expected_format = expected_format
        self.detected_format = detected_format

