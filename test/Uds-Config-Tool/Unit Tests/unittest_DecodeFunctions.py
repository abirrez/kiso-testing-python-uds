#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


import unittest

from uds.uds_config_tool import DecodeFunctions


class CanTpMessageTestCase(unittest.TestCase):
    def test_bit_extract_from_byte_pos0_true(self):
        test_val = 0x01
        result = DecodeFunctions.extract_bit_from_position(test_val, 0)
        self.assertEqual(True, result)

    def test_bit_extract_from_byte_pos0_False(self):
        test_val = 0x00
        result = DecodeFunctions.extract_bit_from_position(test_val, 0)
        self.assertEqual(False, result)

    def test_bit_extract_from_byte_pos1_true(self):
        test_val = 0x02
        result = DecodeFunctions.extract_bit_from_position(test_val, 1)
        self.assertEqual(True, result)

    def test_bit_extract_from_byte_pos1_False(self):
        test_val = 0x00
        result = DecodeFunctions.extract_bit_from_position(test_val, 1)
        self.assertEqual(False, result)

    def test_multiple_bit_extract_from_byte(self):
        test_val = 0x5A
        result = DecodeFunctions.extract_bit_from_position(test_val, 0)
        self.assertEqual(False, result)
        result = DecodeFunctions.extract_bit_from_position(test_val, 1)
        self.assertEqual(True, result)
        result = DecodeFunctions.extract_bit_from_position(test_val, 2)
        self.assertEqual(False, result)
        result = DecodeFunctions.extract_bit_from_position(test_val, 3)
        self.assertEqual(True, result)
        result = DecodeFunctions.extract_bit_from_position(test_val, 4)
        self.assertEqual(True, result)
        result = DecodeFunctions.extract_bit_from_position(test_val, 5)
        self.assertEqual(False, result)
        result = DecodeFunctions.extract_bit_from_position(test_val, 6)
        self.assertEqual(True, result)
        result = DecodeFunctions.extract_bit_from_position(test_val, 7)
        self.assertEqual(False, result)

    def test_bit_extract_from_byte_pos8_True(self):
        test_val = 0x100
        result = DecodeFunctions.extract_bit_from_position(test_val, 8)
        self.assertEqual(True, result)

    def test_bit_extract_from_byte_pos8_False(self):
        test_val = 0x000
        result = DecodeFunctions.extract_bit_from_position(test_val, 8)
        self.assertEqual(False, result)

    def test4_bit_int_extract_from_pos0_of8_bit_int(self):
        test_val = 0xA5
        result = DecodeFunctions.extract_int_from_position(test_val, 4, 0)
        self.assertEqual(0x05, result)

    def test4_bit_int_extract_from_pos1_of8_bit_int(self):
        test_val = 0xA5
        result = DecodeFunctions.extract_int_from_position(test_val, 4, 1)
        self.assertEqual(0x2, result)

    def test4_bit_int_extract_from_pos2_of8_bit_int(self):
        test_val = 0xA5
        result = DecodeFunctions.extract_int_from_position(test_val, 4, 2)
        self.assertEqual(0x9, result)

    def test6_bit_int_extract_from_pos0_of8_bit_int(self):
        test_val = 0xA5
        result = DecodeFunctions.extract_int_from_position(test_val, 6, 2)
        self.assertEqual(0x29, result)

    def test_build_int_from_array1_byte_array(self):
        test_val = [0x5A]
        result = DecodeFunctions.build_int_from_list(test_val)
        self.assertEqual(0x5A, result)

    def test_build_int_from_array2_byte_array(self):
        test_val = [0x5A, 0xA5]
        result = DecodeFunctions.build_int_from_list(test_val)
        self.assertEqual(0x5AA5, result)

    def test_build_int_from_array3_byte_array(self):
        test_val = [0x5A, 0xA5, 0x5A]
        result = DecodeFunctions.build_int_from_list(test_val)
        self.assertEqual(0x5AA55A, result)

    def test_build_int_from_array4_byte_array(self):
        test_val = [0x5A, 0xA5, 0xA5, 0x5A]
        result = DecodeFunctions.build_int_from_list(test_val)
        self.assertEqual(0x5AA5A55A, result)

    def test_build_int_from_array8_byte_array(self):
        test_val = [0x5A, 0xA5, 0xA5, 0x5A, 0x5A, 0xA5, 0xA5, 0x5A]
        result = DecodeFunctions.build_int_from_list(test_val)
        self.assertEqual(0x5AA5A55A5AA5A55A, result)

    def test_string_to_byte_array_alpha_only_ascii(self):
        test_val = "abcdefghijklmn"
        result = DecodeFunctions.string_to_int_list(test_val, "ascii")
        self.assertEqual(
            [
                0x61,
                0x62,
                0x63,
                0x64,
                0x65,
                0x66,
                0x67,
                0x68,
                0x69,
                0x6A,
                0x6B,
                0x6C,
                0x6D,
                0x6E,
            ],
            result,
        )

    def test_string_to_byte_array_numeric_only_ascii(self):
        test_val = "abcdefg01234"
        result = DecodeFunctions.string_to_int_list(test_val, "ascii")
        self.assertEqual(
            [0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x30, 0x31, 0x32, 0x33, 0x34],
            result,
        )

    def test_string_to_byte_array_alpha_only_utf8(self):
        test_val = "abcdefg"
        result = DecodeFunctions.string_to_int_list(test_val, "utf-8")
        self.assertEqual([0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67], result)

    def test_byte_array_to_string_alpha_only_ascii(self):
        test_val = [
            0x61,
            0x62,
            0x63,
            0x64,
            0x65,
            0x66,
            0x67,
            0x68,
            0x69,
            0x6A,
            0x6B,
            0x6C,
            0x6D,
            0x6E,
        ]
        result = DecodeFunctions.int_list_to_string(test_val, "ascii")
        self.assertEqual("abcdefghijklmn", result)

    def test_uint16_array_to_uint8_array(self):
        test_val = [0x5AA5, 0xA55A]
        result = DecodeFunctions.int_array_to_uint8_array(test_val, "int16")
        self.assertEqual([0x5A, 0xA5, 0xA5, 0x5A], result)

    def test_uint8_array_to_uint16_array(self):
        test_val = [0x5AA55AA5, 0xA55AA55A]
        result = DecodeFunctions.int_array_to_uint8_array(test_val, "int32")
        self.assertEqual([0x5A, 0xA5, 0x5A, 0xA5, 0xA5, 0x5A, 0xA5, 0x5A], result)


if __name__ == "__main__":
    unittest.main()
