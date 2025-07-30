"""Core Data Types

This module defines the framework's core data types.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ─

# standard library import
from __future__ import annotations
from abc import ABC, abstractmethods
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum, auto
from typing import (
    # types
    Any, Final, Iterator, NamedTuple, Protocol, TypeAlias, TypeVar,

    # descriptors
    final, overload, runtime_checkable
)

# third-party imports
import numpy as np

from Bio import SeqIO
from Bio.Seq import Seq
from returns import Maybe, Result

# local imports
# ...


# ─── enums ────────────────────────────────────────────────────────────── ✦✦ ─


class Alphabet(Enum):
    """An enumeration of the alphabets used in sequencing."""
    AA  = auto()
    DNA = auto()
    RNA = auto()
    


# ─── typing ───────────────────────────────────────────────────────────── ✦✦ ─

T: TypeVar = TypeVar("T")
E: TypeVar = TypeVar("E")
S: TypeVar = TypeVar("S")
U: TypeVar = TypeVar("U")


@runtime_checkable
class Parseable(Protocol):
    ...


@dataclass
class Domain(Enum):
    ...


class Genome(ABC):
    domain: Domain
