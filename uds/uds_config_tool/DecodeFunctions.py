#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from functools import reduce


def extract_bit_from_position(aInt, position):
    return (aInt & (2**position)) >> position


def extract_int_from_position(aInt, size, position):
    return (aInt >> position) & ((2**size) - 1)


##
# @brief uses the reduce pattern to concatenate the list into a single integer
# tests were performed the assess the benefit of using functional methods
# and the reduce and for loops gave similar times. Using a recursive function
# was almost 10 times slower.
def build_int_from_list(aList):
    return reduce(lambda x, y: (x << 8) + y, aList)


##
# @brief uses list comprehension to deal with the input string
# todo: implement the encoding type
def string_to_int_list(aString, encoding_type):
    result = []
    [result.append(ord(i)) for i in aString]
    return result


##
# @brief uses the map, reduce pattern to deal with the input list functionally
# todo: implement the encoding type
def int_list_to_string(aList, encoding_type):
    return reduce(lambda x, y: x + y, list(map(chr, aList)))


def int_array_to_uint8_array(aArray, input_type):
    return int_array_to_int_array(aArray, input_type, "int8")


def int_array_to_int_array(aArray, input_type, output_type):
    if input_type == "uint32":
        input_func = lambda x: [
            extract_int_from_position(x, 8, 24),
            extract_int_from_position(x, 8, 16),
            extract_int_from_position(x, 8, 8),
            extract_int_from_position(x, 8, 0),
        ]
    elif input_type == "uint16":
        input_func = lambda x: [
            extract_int_from_position(x, 8, 8),
            extract_int_from_position(x, 8, 0),
        ]
    elif input_type == "uint8":
        input_func = lambda x: [x]
    elif input_type == "int32":
        input_func = lambda x: [
            extract_int_from_position(x, 8, 24),
            extract_int_from_position(x, 8, 16),
            extract_int_from_position(x, 8, 8),
            extract_int_from_position(x, 8, 0),
        ]
    elif input_type == "int16":
        input_func = lambda x: [
            extract_int_from_position(x, 8, 8),
            extract_int_from_position(x, 8, 0),
        ]
    elif input_type == "int8":
        input_func = lambda x: [x]
    else:
        raise TypeError("input_type not currently supported")

    result = reduce(lambda x, y: x + y, list(map(input_func, aArray)))

    if output_type == "int8":
        return result
    if output_type == "int32":
        size = 4
        number_of_entries = int(len(result) / size)
    elif output_type == "int16":
        size = 2
        number_of_entries = int(len(result) / size)

    output = list(
        map(
            build_int_from_list,
            [result[(i * size) : (i * size + size)] for i in range(number_of_entries)],
        )
    )
    return output


##
# @brief convert an data input of integer type to a list of bytes.
def int_value_to_byte_array(int_input, bit_length):
    if not isinstance(int_input, int):
        return int_input

    if bit_length <= 8:
        input_func = lambda x: [x]
    elif bit_length <= 16:
        input_func = lambda x: [
            extract_int_from_position(x, 8, 8),
            extract_int_from_position(x, 8, 0),
        ]
    elif bit_length <= 24:
        input_func = lambda x: [
            extract_int_from_position(x, 8, 16),
            extract_int_from_position(x, 8, 8),
            extract_int_from_position(x, 8, 0),
        ]
    elif bit_length <= 32:
        input_func = lambda x: [
            extract_int_from_position(x, 8, 24),
            extract_int_from_position(x, 8, 16),
            extract_int_from_position(x, 8, 8),
            extract_int_from_position(x, 8, 0),
        ]
    else:
        raise TypeError("input length of integer type is too long!")

    return input_func(int_input)


if __name__ == "__main__":
    a = int_array_to_int_array([0x5AA55AA5, 0xA55AA55A], "int32", "int32")
    print(a)
    assert [0x5AA55AA5, 0xA55AA55A] == a
    a = int_array_to_int_array([0x5AA55AA5, 0xA55AA55A], "int32", "int16")
    print(a)
    assert [0x5AA5, 0x5AA5, 0xA55A, 0xA55A] == a
    a = int_array_to_int_array([0x5AA55AA5, 0xA55AA55A], "int32", "int8")
    print(a)
    assert [0x5A, 0xA5, 0x5A, 0xA5, 0xA5, 0x5A, 0xA5, 0x5A] == a
    a = int_array_to_int_array([0x5AA5, 0xA55A], "int16", "int16")
    print(a)
    assert [0x5AA5, 0xA55A] == a
    a = int_array_to_int_array([0x5AA5, 0xA55A], "int16", "int32")
    print(a)
    assert [0x5AA5A55A] == a
    a = int_array_to_int_array([0x5AA5, 0xA55A], "int16", "int8")
    print(a)
    assert [0x5A, 0xA5, 0xA5, 0x5A] == a
    a = int_array_to_int_array([0x5A, 0xA5, 0xA5, 0x5A], "int8", "int8")
    print(a)
    assert [0x5A, 0xA5, 0xA5, 0x5A] == a
    a = int_array_to_int_array([0x5A, 0xA5, 0xA5, 0x5A], "int8", "int16")
    print(a)
    assert [0x5AA5, 0xA55A] == a
    a = int_array_to_int_array([0x5A, 0xA5, 0xA5, 0x5A], "int8", "int32")
    print(a)
    assert [0x5AA5A55A] == a
    a = int_array_to_int_array(
        [0x5A, 0xA5, 0xA5, 0x5A, 0xA5, 0x5A, 0xA5, 0x5A], "int8", "int32"
    )
    print(a)
    assert [0x5AA5A55A, 0xA55AA55A] == a

    a = int_array_to_int_array([0x01], "int8", "int8")
    print(a)

    a = int_array_to_uint8_array([0x01], "int8")
    print(a)

    a = int_value_to_byte_array([0x00, 0xB1], 16)
    print(a)
    assert [0x00, 0xB1] == a

    a = int_value_to_byte_array([0x00, 0xB1], 32)
    print(a)
    assert [0x00, 0xB1] == a

    a = int_value_to_byte_array(0xB1, 16)
    print(a)
    assert [0x00, 0xB1] == a

    a = int_value_to_byte_array(0xB1, 32)
    print(a)
    assert [0x00, 0x00, 0x00, 0xB1] == a
