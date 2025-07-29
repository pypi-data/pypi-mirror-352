"""
Core binary arithmetic operations using 2's complement.

This module contains functions for binary addition, subtraction, 
and conversions between binary and decimal, all operating on
string representations of binary numbers.
"""


def decimal_to_binary(decimal_number: int, bits: int) -> str:
    """
    Convert decimal number to binary string representation with specified bit length.
    
    Args:
        decimal_number: Integer to convert to binary
        bits: Number of bits in the output binary string
        
    Returns:
        Binary string representation with specified length
    
    Example:
        >>> decimal_to_binary(8, 5)
        '01000'
        >>> decimal_to_binary(-8, 5)
        '11000'
    """
    if decimal_number < 0:
        # For negative numbers, calculate 2's complement
        # First, get positive binary value
        positive_binary = bin(abs(decimal_number))[2:].zfill(bits)
        
        # Calculate 2's complement
        return twos_complement(positive_binary, bits)
    else:
        # For positive numbers, just convert and zero-fill
        binary = bin(decimal_number)[2:].zfill(bits)
        
        # Ensure the binary number fits in the specified bits
        if len(binary) > bits:
            return binary[-bits:]
        
        return binary


def binary_to_decimal(binary_str: str) -> int:
    """
    Convert binary string representation to decimal number.
    Handles 2's complement for negative numbers.
    
    Args:
        binary_str: Binary string to convert
        
    Returns:
        Integer decimal representation
        
    Example:
        >>> binary_to_decimal('01000')
        8
        >>> binary_to_decimal('11000')
        -8
    """
    if binary_str[0] == '0':  # Positive number
        return int(binary_str, 2)
    else:  # Negative number in 2's complement
        # Calculate 2's complement to get the positive value
        inverted = twos_complement(binary_str, len(binary_str))
        # Return the negative of that value
        return -int(inverted, 2)


def twos_complement(binary_str: str, bits: int) -> str:
    """
    Calculate the 2's complement of a binary string.
    
    Args:
        binary_str: Binary string to complement
        bits: Number of bits to consider
        
    Returns:
        2's complement as a binary string
    """
    # Ensure the binary string has the correct length
    binary_str = binary_str.zfill(bits)[-bits:]
    
    # Step 1: Invert all bits
    inverted = ''.join('1' if bit == '0' else '0' for bit in binary_str)
    
    # Step 2: Add 1
    # Initialize carry bit
    carry = 1
    result = ''
    
    # Process from right to left (least to most significant bit)
    for bit in inverted[::-1]:  # Reverse the string
        if bit == '0' and carry == 1:
            result = '1' + result
            carry = 0
        elif bit == '1' and carry == 1:
            result = '0' + result
            carry = 1
        else:  # carry == 0
            result = bit + result
    
    # Ensure result is the correct length
    return result[-bits:]


def binary_addition(binary_a: str, binary_b: str, bits: int) -> str:
    """
    Add two binary numbers represented as strings using 2's complement.
    
    Args:
        binary_a: First binary number
        binary_b: Second binary number
        bits: Number of bits to use for the result
        
    Returns:
        Binary string representing the sum
    
    Example:
        >>> binary_addition('01010', '00011', 5)  # 10 + 3
        '01101'
    """
    # Ensure both binary strings are the same length
    binary_a = binary_a.zfill(bits)[-bits:]
    binary_b = binary_b.zfill(bits)[-bits:]
    
    # Initialize result and carry
    result = ''
    carry = 0
    
    # Perform addition from right to left
    for i in range(bits-1, -1, -1):
        bit_sum = int(binary_a[i]) + int(binary_b[i]) + carry
        result = str(bit_sum % 2) + result
        carry = bit_sum // 2
    
    # Truncate result to specified bits (discard overflow)
    return result[-bits:]


def binary_subtraction(binary_a: str, binary_b: str, bits: int) -> str:
    """
    Subtract binary_b from binary_a using 2's complement.
    
    Args:
        binary_a: Binary number to subtract from (minuend)
        binary_b: Binary number to subtract (subtrahend)
        bits: Number of bits to use for the result
        
    Returns:
        Binary string representing the difference
    
    Example:
        >>> binary_subtraction('01010', '00011', 5)  # 10 - 3
        '00111'
    """
    # To subtract b from a, we add a + (-b)
    # First, calculate -b (2's complement of b)
    negative_b = twos_complement(binary_b, bits)
    
    # Now add a + (-b)
    return binary_addition(binary_a, negative_b, bits)
