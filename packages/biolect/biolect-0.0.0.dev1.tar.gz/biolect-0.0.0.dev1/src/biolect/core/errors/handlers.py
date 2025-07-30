"""Core Error Handlers

This module implements the core error-handling logic for
Biolect workflows.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ─

# standard library imports
from abc import ABC, abstractmethod

# third-party imports
# ...

# local imports
from .etypes import BiolectError, FileFormatError


class ErrorHandler(ABC):
    @abstractmethod
    def attempt_recovery(
        self,
        error: BiolectError,
        context: dict
    ) -> bool:
        """Attempt to recover from a raised exception."""
        ...

    @abstractmethod
    def should_retry(
        self,
        error: BiolectError,
        attempt_count: int
    ) -> bool:
        """Determine if the recovery operation should be reattempted."""
        ...


class FileFormatErrorHandler(ErrorHandler):
    def attempt_recovery(
        self,
        error: FileFormatError,
        context: dict
    ) -> bool:
        """Attempt to recover from an file formatting error.

        Args:
          error (FileFormatError):
            The exception object raised by the caller.
          context (dict):
            A dictionary object that contains details about the context
            surrounding the error.

        Returns:
            `True` if successful, otherwise `False`.
        """
        pass

    
    def should_retry(
        self,
        error: FileFormatError,
        context: dict
    ) -> bool:
        """Deterimine if the recovery operation should be reattempted.

        Args:
          error (FileFormatError):
            The exception object raised by the caller.
          context (dict):
            A dictionary object that contains details about the context
            surrounding the error.

        Returns:
            `True` if successful, otherwise `False`.
        """
        pass