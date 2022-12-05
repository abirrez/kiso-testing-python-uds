#!/usr/bin/env python

"""
This file provides an example of the different stages of the uds communication flow.
Its intention is to describe how the auto-coder would produce the code for the system

It is not intended as a piece of usable code
"""


__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from uds import DecodeFunctions


def check_Boot_Software_Identification_Read(payload):

    EXPECTEDLENGTH = 28

    if len(payload) != EXPECTEDLENGTH:
        raise Exception(
            "Unexpected length of response: Received length: "
            + str(len(payload))
            + " Payload: "
            + str(payload)
        )

    POSITIVE_RESPONSE = 0x62
    NEGATIVE_RESPONSE = 0x7F

    response_received = payload[0]

    if response_received == POSITIVE_RESPONSE:
        diagnostic_identifier_expected = 0xF180
        diagnostic_identifier_received = DecodeFunctions.build_int_from_list(payload[1:3])

        if diagnostic_identifier_expected != diagnostic_identifier_received:
            raise Exception(
                "Diagnostic identifier does not match expected response: Payload: "
                + str(payload)
            )

        return None
    elif response_received == NEGATIVE_RESPONSE:
        # needs improvement to define the exact negative response received
        raise Exception("Negative response received: Payload: " + str(payload))
    else:
        raise Exception("Unexpected response: Payload: " + str(payload))


def decode_Boot_Software_Identification_Read(payload):

    # check the response
    check_Boot_Software_Identification_Read(payload)

    # dynamic
    number_of_modules = payload[3:4]
    boot_Software_Identification = payload[4:28]

    result = {}
    result["numberOfModules"] = number_of_modules[0]
    result["Boot Software Identification"] = DecodeFunctions.int_list_to_string(
        boot_Software_Identification, "ISO-8859-1"
    )

    return result


if __name__ == "__main__":

    testVal_correct = [
        0x62,
        0xF1,
        0x80,
        0x03,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x30,
        0x37,
    ]

    response = decode_Boot_Software_Identification_Read(testVal_correct)

    [print(i, response[i]) for i in response]
