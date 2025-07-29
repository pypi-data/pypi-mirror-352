"""
Binary Arithmetic Library with 2's Complement Operations.

This library provides functions for binary arithmetic operations using 2's complement 
representation without converting to decimal during operations, as well as binary-decimal 
conversion utilities.
"""

from .binary_ops import (
    binary_addition,
    binary_subtraction,
    decimal_to_binary,
    binary_to_decimal,
    twos_complement
)

__version__ = '0.1.0'
__author__ = 'Gurdeep'
