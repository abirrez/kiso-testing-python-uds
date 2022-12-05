#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


import cProfile
import sys
from functools import reduce


# ----------------------------------------------------------------
# Profiler Code
# ----------------------------------------------------------------
def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats()

    return profiled_func


# ----------------------------------------------------------------
# build_int_from_list Tests
# ----------------------------------------------------------------


@do_cprofile
def build_int_from_list_non_recursive_func(aList):
    def build_int_from_list(aList):
        result = 0
        for i in range(0, len(aList)):
            result += aList[i] << (8 * (len(aList) - (i + 1)))
        return result

    return build_int_from_list(aList)


@do_cprofile
def build_int_from_list_recursive_func(aList):
    def build_int_from_list(aList):
        if len(aList) == 1:
            return aList[0]
        else:
            return (aList[0] << (8 * (len(aList) - 1))) + build_int_from_list(aList[1:])

    return build_int_from_list(aList)


@do_cprofile
def build_int_from_list_reduce_func(aList):
    def build_int_from_list(aList):
        return reduce(lambda x, y: (x << 8) + y, aList)

    return build_int_from_list(aList)


# ----------------------------------------------------------------
# byte_list_to_string Tests
# ----------------------------------------------------------------


@do_cprofile
def byte_list_to_string_non_recursive_func(aList):
    def byte_list_to_string(aList):
        result = ""
        for i in aList:
            result += chr(i)
        return result

    return byte_list_to_string(aList)


@do_cprofile
def byte_list_to_string_recursive_func(aList):
    def byte_list_to_string(aList):
        if len(aList) == 1:
            return chr(aList[0])
        else:
            return chr(aList[0]) + byte_list_to_string(aList[1:])

    return byte_list_to_string(aList)


@do_cprofile
def byte_list_to_string_reduce_func(aList):
    def byte_list_to_string(aList):
        return reduce(lambda x, y: x + y, list(map(chr, aList)))

    return byte_list_to_string(aList)


if __name__ == "__main__":

    sys.setrecursionlimit(4000)

    test_listA = []
    for i in range(0, 2500):
        test_listA.append(0x5A)

    test_listB = []
    for i in range(0, 2500):
        test_listB.append(0x30)

    print("Testing the build_int_from_list methods")
    resultA = build_int_from_list_non_recursive_func(test_listA)
    resultB = build_int_from_list_recursive_func(test_listA)
    resultC = build_int_from_list_reduce_func(test_listA)

    assert resultA == resultB == resultC

    print("Testing the byte_list_to_string methods")
    resultA = byte_list_to_string_non_recursive_func(test_listB)
    resultB = byte_list_to_string_recursive_func(test_listB)
    resultC = byte_list_to_string_reduce_func(test_listB)

    assert resultA == resultB == resultC
    pass
