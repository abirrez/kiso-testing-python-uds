#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


import sys

from uds.uds_config_tool import DecodeFunctions
from uds.uds_config_tool.FunctionCreation.iServiceMethodFactory import (
    IServiceMethodFactory,
)

request_func_template = str(
    "def {0}(suppress_response=False):\n"
    "    zeroSubFunction = [0x80] if suppress_response else [0x00]\n"
    "    return {1} + zeroSubFunction"
)

# Note: we do not need to cater for response suppression checking as nothing to check if response is suppressed - always unsuppressed
check_function_template = str(
    "def {0}(input):\n"
    "    # The tester present response is simple and fixed, so hardcoding here for simplicity.\n"
    "    service_id = DecodeFunctions.build_int_from_list(input[0:1])\n"
    "    zeroSubFunction = DecodeFunctions.build_int_from_list(input[1:2])\n"
    '    if(len(input) != 2): raise Exception("Total length returned not as expected. Expected: 2; Got {{0}}".format(len(input)))\n'
    '    if(service_id != 0x7E): raise Exception("Service Id Received not expected. Expected {{0}}; Got {{1}} ".format(0x7E,service_id))\n'
    '    if(zeroSubFunction != 0x00): raise Exception("Zero Sub Function Received not as expected. Expected {{0}}; Got {{1}}".format(0x00,zeroSubFunction))'
)

negative_response_func_template = str(
    "def {0}(input):\n"
    "    result = {{}}\n"
    "    nrc_list = {5}\n"
    "    if input[{1}:{2}] == [{3}]:\n"
    "        result['NRC'] = input[{4}]\n"
    "        result['NRC_Label'] = nrc_list.get(result['NRC'])\n"
    "    return result"
)

# Note: we do not need to cater for response suppression checking as nothing to check if response is suppressed - always unsuppressed.
# For tester present there is no response data to return, so hardcoding an empty response.
encode_positive_response_func_template = str("def {0}(input):\n" "    return {{}}")


class TesterPresentMethodFactory(IServiceMethodFactory):

    ##
    # @brief method to create the request function for the service element
    @staticmethod
    def create_request_function(diag_service_element, xml_elements):
        # Some services are present in the ODX in both response and send only versions (with the same short name, so one will overwrite the other).
        # Avoiding the overwrite by ignoring the send-only versions, i.e. these are identical other than postivie response details being missing.
        try:
            if diag_service_element.attrib["TRANSMISSION-MODE"] == "SEND-ONLY":
                return None
        except:
            pass

        service_id = 0
        reset_type = 0

        short_name = "request_{0}".format(diag_service_element.find("SHORT-NAME").text)
        request_element = xml_elements[
            diag_service_element.find("REQUEST-REF").attrib["ID-REF"]
        ]
        params_element = request_element.find("PARAMS")

        encode_functions = []
        encode_function = "None"

        for param in params_element:
            semantic = None
            try:
                semantic = param.attrib["SEMANTIC"]
            except AttributeError:
                pass

            if semantic == "SERVICE-ID":
                service_id = [int(param.find("CODED-VALUE").text)]

        func_string = request_func_template.format(short_name, service_id)
        exec(func_string)
        return locals()[short_name]

    ##
    # @brief method to create the function to check the positive response for validity
    # Note: the response for tester present is simplistic, so the details have been hardcoded;
    # this function is really just checking that the service is supported before creating the
    # the hardcoded check function.
    @staticmethod
    def create_check_positive_response_function(diag_service_element, xml_elements):
        # Some services are present in the ODX in both response and send only versions (with the same short name, so one will overwrite the other).
        # Avoiding the overwrite by ignoring the send-only versions, i.e. these are identical other than positive response details being missing.
        try:
            if diag_service_element.attrib["TRANSMISSION-MODE"] == "SEND-ONLY":
                return None
        except:
            pass

        response_id = 0

        short_name = diag_service_element.find("SHORT-NAME").text
        check_function_name = "check_{0}".format(short_name)
        positive_response_element = xml_elements[
            (diag_service_element.find("POS-RESPONSE-REFS"))
            .find("POS-RESPONSE-REF")
            .attrib["ID-REF"]
        ]

        check_function_string = check_function_template.format(check_function_name)  # 0
        exec(check_function_string)
        return locals()[check_function_name]

    ##
    # @brief method to encode the positive response from the raw type to it physical representation
    @staticmethod
    def create_encode_positive_response_function(diag_service_element, xml_elements):
        # Some services are present in the ODX in both response and send only versions (with the same short name, so one will overwrite the other).
        # Avoiding the overwrite by ignoring the send-only versions, i.e. these are identical other than postivie response details being missing.
        try:
            if diag_service_element.attrib["TRANSMISSION-MODE"] == "SEND-ONLY":
                return None
        except:
            pass

        # The values in the response are SID, reset_type, and optionally the powerDownTime (only for reset_type 0x04). Checking is handled in the check function,
        # so must be present and ok. This function is only required to return the reset_type and powerDownTime (if present).

        positive_response_element = xml_elements[
            (diag_service_element.find("POS-RESPONSE-REFS"))
            .find("POS-RESPONSE-REF")
            .attrib["ID-REF"]
        ]

        short_name = diag_service_element.find("SHORT-NAME").text
        encode_positive_response_function_name = "encode_{0}".format(short_name)

        encode_function_string = encode_positive_response_func_template.format(
            encode_positive_response_function_name
        )
        exec(encode_function_string)
        return locals()[encode_positive_response_function_name]

    ##
    # @brief method to create the negative response function for the service element
    @staticmethod
    def create_check_negative_response_function(diag_service_element, xml_elements):
        # Some services are present in the ODX in both response and send only versions (with the same short name, so one will overwrite the other).
        # Avoiding the overwrite by ignoring the send-only versions, i.e. these are identical other than postivie response details being missing.
        try:
            if diag_service_element.attrib["TRANSMISSION-MODE"] == "SEND-ONLY":
                return None
        except:
            pass

        short_name = diag_service_element.find("SHORT-NAME").text
        check_negative_response_function_name = "check_negResponse_{0}".format(short_name)

        negative_responses_element = diag_service_element.find("NEG-RESPONSE-REFS")

        negative_response_checks = []

        for negative_response in negative_responses_element:
            negative_response_ref = xml_elements[negative_response.attrib["ID-REF"]]

            negative_response_params = negative_response_ref.find("PARAMS")

            for param in negative_response_params:

                semantic = None
                try:
                    semantic = param.attrib["SEMANTIC"]
                except:
                    semantic = None

                byte_position = int(param.find("BYTE-POSITION").text)

                if semantic == "SERVICE-ID":
                    service_id = param.find("CODED-VALUE").text
                    start = int(param.find("BYTE-POSITION").text)
                    diag_coded_type = param.find("DIAG-CODED-TYPE")
                    bit_length = int(
                        (param.find("DIAG-CODED-TYPE")).find("BIT-LENGTH").text
                    )
                    list_length = int(bit_length / 8)
                    end = start + list_length
                elif byte_position == 2:
                    nrc_pos = byte_position
                    expected_nrc_dict = {}
                    try:
                        data_object_element = xml_elements[
                            (param.find("DOP-REF")).attrib["ID-REF"]
                        ]
                        nrc_list = (
                            data_object_element.find("COMPU-METHOD")
                            .find("COMPU-INTERNAL-TO-PHYS")
                            .find("COMPU-SCALES")
                        )
                        for nrc_elem in nrc_list:
                            expected_nrc_dict[int(nrc_elem.find("UPPER-LIMIT").text)] = (
                                nrc_elem.find("COMPU-CONST").find("VT").text
                            )
                    except:
                        pass
                pass

        negative_response_function_string = negative_response_func_template.format(
            check_negative_response_function_name,
            start,
            end,
            service_id,
            nrc_pos,
            expected_nrc_dict,
        )
        exec(negative_response_function_string)
        return locals()[check_negative_response_function_name]
