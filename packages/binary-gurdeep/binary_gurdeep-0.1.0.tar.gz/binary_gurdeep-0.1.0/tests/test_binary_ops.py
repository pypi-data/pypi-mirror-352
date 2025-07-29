import unittest
from binary_gurdeep import binary_addition, binary_subtraction, decimal_to_binary, binary_to_decimal


class TestBinaryGurdeep(unittest.TestCase):
    def test_decimal_to_binary(self):
        self.assertEqual(decimal_to_binary(8, 5), "01000")
        self.assertEqual(decimal_to_binary(-8, 5), "11000")
        self.assertEqual(decimal_to_binary(0, 4), "0000")
        self.assertEqual(decimal_to_binary(15, 5), "01111")
        self.assertEqual(decimal_to_binary(-1, 4), "1111")

    def test_binary_to_decimal(self):
        self.assertEqual(binary_to_decimal("01000"), 8)
        self.assertEqual(binary_to_decimal("11000"), -8)
        self.assertEqual(binary_to_decimal("0000"), 0)
        self.assertEqual(binary_to_decimal("01111"), 15)
        self.assertEqual(binary_to_decimal("1111"), -1)
        
    def test_binary_addition(self):
        # Positive + Positive
        self.assertEqual(binary_addition("00101", "00011", 5), "01000")  # 5 + 3 = 8
        # Positive + Negative
        self.assertEqual(binary_addition("00101", "11101", 5), "00010")  # 5 + (-3) = 2
        # Negative + Positive
        self.assertEqual(binary_addition("11101", "00101", 5), "00010")  # -3 + 5 = 2
        # Negative + Negative
        self.assertEqual(binary_addition("11011", "11101", 5), "11000")  # -5 + (-3) = -8
        # Zero cases
        self.assertEqual(binary_addition("00000", "00101", 5), "00101")  # 0 + 5 = 5
        self.assertEqual(binary_addition("00101", "00000", 5), "00101")  # 5 + 0 = 5

    def test_binary_subtraction(self):
        # Positive - Positive (result positive)
        self.assertEqual(binary_subtraction("00101", "00011", 5), "00010")  # 5 - 3 = 2
        # Positive - Positive (result negative)
        self.assertEqual(binary_subtraction("00011", "00101", 5), "11110")  # 3 - 5 = -2
        # Positive - Negative
        self.assertEqual(binary_subtraction("00101", "11101", 5), "01000")  # 5 - (-3) = 8
        # Negative - Positive
        self.assertEqual(binary_subtraction("11101", "00101", 5), "11000")  # -3 - 5 = -8
        # Negative - Negative
        self.assertEqual(binary_subtraction("11011", "11101", 5), "11110")  # -5 - (-3) = -2
        # Zero cases
        self.assertEqual(binary_subtraction("00000", "00101", 5), "11011")  # 0 - 5 = -5
        self.assertEqual(binary_subtraction("00101", "00000", 5), "00101")  # 5 - 0 = 5

    def test_consistency(self):
        # Test that binary operations are consistent with their decimal counterparts
        for a in range(-16, 16):
            for b in range(-16, 16):
                binary_a = decimal_to_binary(a, 6)
                binary_b = decimal_to_binary(b, 6)
                
                # Addition
                binary_sum = binary_addition(binary_a, binary_b, 6)
                decimal_sum = binary_to_decimal(binary_sum)
                expected_sum = (a + b) % 64  # Modulo 2^bits for overflow handling
                if expected_sum >= 32:  # Handle negative numbers in 6-bit 2's complement
                    expected_sum -= 64
                self.assertEqual(decimal_sum, expected_sum, f"{a} + {b} = {decimal_sum}, expected {expected_sum}")
                
                # Subtraction
                binary_diff = binary_subtraction(binary_a, binary_b, 6)
                decimal_diff = binary_to_decimal(binary_diff)
                expected_diff = (a - b) % 64  # Modulo 2^bits for overflow handling
                if expected_diff >= 32:  # Handle negative numbers in 6-bit 2's complement
                    expected_diff -= 64
                self.assertEqual(decimal_diff, expected_diff, f"{a} - {b} = {decimal_diff}, expected {expected_diff}")


if __name__ == "__main__":
    unittest.main()
