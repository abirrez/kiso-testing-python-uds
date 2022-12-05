#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"

import sys
import xml.etree.ElementTree as ET

from uds.uds_config_tool import DecodeFunctions
from uds.uds_config_tool.FunctionCreation.iServiceMethodFactory import (
    IServiceMethodFactory,
)

SUPPRESS_RESPONSE_BIT = 0x80

request_func_template = str(
    "def {0}(suppress_response=False):\n"
    "    session_type = {2}\n"
    "    suppressBit = {3} if suppress_response else 0x00\n"
    "    session_type[0] += suppressBit\n"
    "    return {1} + session_type"
)

# Note: we do not need to cater for response suppression checking as nothing to check if response is suppressed - always unsuppressed
check_function_template = str(
    "def {0}(input):\n"
    "    serviceIdExpected = {1}\n"
    "    sessionTypeExpected = {2}\n"
    "    service_id = DecodeFunctions.build_int_from_list(input[{3}:{4}])\n"
    "    session_type = DecodeFunctions.build_int_from_list(input[{5}:{6}])\n"
    '    if(len(input) != {7}): raise Exception("Total length returned not as expected. Expected: {7}; Got {{0}}".format(len(input)))\n'
    '    if(service_id != serviceIdExpected): raise Exception("Service Id Received not expected. Expected {{0}}; Got {{1}} ".format(serviceIdExpected, service_id))\n'
    '    if(session_type != sessionTypeExpected): raise Exception("Session Type Received not as expected. Expected: {{0}}; Got {{1}}".format(sessionTypeExpected, session_type))'
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

# Note: we do not need to cater for response suppression checking as nothing to check if response is suppressed - always unsuppressed
encode_positive_response_func_template = str(
    "def {0}(input):\n" "    result = {{}}\n" "    {1}\n" "    return result"
)


class DiagnosticSessionControlMethodFactory(IServiceMethodFactory):

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
        session_type = 0

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
            elif semantic == "SUBFUNCTION":
                session_type = [int(param.find("CODED-VALUE").text)]
                if session_type[0] >= SUPPRESS_RESPONSE_BIT:
                    pass
                    # raise ValueError("Diagnostic Session Control:session type exceeds maximum value (received {0})".format(session_type[0]))

        func_string = request_func_template.format(
            short_name, service_id, session_type, SUPPRESS_RESPONSE_BIT
        )
        exec(func_string)
        return locals()[short_name]

    ##
    # @brief method to create the function to check the positive response for validity
    @staticmethod
    def create_check_positive_response_function(diag_service_element, xml_elements):

        # Some services are present in the ODX in both response and send only versions (with the same short name, so one will overwrite the other).
        # Avoiding the overwrite by ignoring the send-only versions, i.e. these are identical other than postivie response details being missing.
        try:
            if diag_service_element.attrib["TRANSMISSION-MODE"] == "SEND-ONLY":
                return None
        except:
            pass

        response_id = 0
        session_type = 0

        response_id_start = 0
        response_id_end = 0
        session_type_start = 0
        session_type_end = 0

        short_name = "request_{0}".format(diag_service_element.find("SHORT-NAME").text)
        check_function_name = "check_{0}".format(short_name)
        positive_response_element = xml_elements[
            (diag_service_element.find("POS-RESPONSE-REFS"))
            .find("POS-RESPONSE-REF")
            .attrib["ID-REF"]
        ]

        params_element = positive_response_element.find("PARAMS")

        total_length = 0
        param_cnt = 0

        for param in params_element:
            try:
                semantic = None
                try:
                    semantic = param.attrib["SEMANTIC"]
                except AttributeError:
                    pass

                start_byte = int(param.find("BYTE-POSITION").text)

                if semantic == "SERVICE-ID":
                    response_id = int(param.find("CODED-VALUE").text)
                    bit_length = int(
                        (param.find("DIAG-CODED-TYPE")).find("BIT-LENGTH").text
                    )
                    list_length = int(bit_length / 8)
                    response_id_start = start_byte
                    response_id_end = start_byte + list_length
                    total_length += list_length
                elif semantic == "SUBFUNCTION":
                    session_type = int(param.find("CODED-VALUE").text)
                    bit_length = int(
                        (param.find("DIAG-CODED-TYPE")).find("BIT-LENGTH").text
                    )
                    list_length = int(bit_length / 8)
                    session_type_start = start_byte
                    session_type_end = start_byte + list_length
                    total_length += list_length
                elif semantic == "DATA":
                    data_object_element = xml_elements[
                        (param.find("DOP-REF")).attrib["ID-REF"]
                    ]
                    if data_object_element.tag == "DATA-OBJECT-PROP":
                        start = int(param.find("BYTE-POSITION").text)
                        bit_length = int(
                            data_object_element.find("DIAG-CODED-TYPE")
                            .find("BIT-LENGTH")
                            .text
                        )
                        list_length = int(bit_length / 8)
                        total_length += list_length
                    elif data_object_element.tag == "STRUCTURE":
                        start = int(param.find("BYTE-POSITION").text)
                        list_length = int(data_object_element.find("BYTE-SIZE").text)
                        total_length += list_length
                    else:
                        pass
                else:
                    pass
            except:
                # print(sys.exc_info())
                pass

        check_function_string = check_function_template.format(
            check_function_name,  # 0
            response_id,  # 1
            session_type,  # 2
            response_id_start,  # 3
            response_id_end,  # 4
            session_type_start,  # 5
            session_type_end,  # 6
            total_length,
        )  # 7
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

        # The values in the response are SID, diagnosticSessionType, and session parameters. Checking is handled in the check function,
        # so must be present and ok. This function is only required to return the diagnosticSessionType, and session parameters.
        positive_response_element = xml_elements[
            (diag_service_element.find("POS-RESPONSE-REFS"))
            .find("POS-RESPONSE-REF")
            .attrib["ID-REF"]
        ]

        short_name = diag_service_element.find("SHORT-NAME").text
        encode_positive_response_function_name = "encode_{0}".format(short_name)

        params = positive_response_element.find("PARAMS")

        encode_functions = []

        for param in params:
            try:
                semantic = None
                try:
                    semantic = param.attrib["SEMANTIC"]
                except AttributeError:
                    pass

                if semantic == "SUBFUNCTION":
                    long_name = param.find("LONG-NAME").text
                    byte_position = int(param.find("BYTE-POSITION").text)
                    bit_length = int(
                        param.find("DIAG-CODED-TYPE").find("BIT-LENGTH").text
                    )
                    list_length = int(bit_length / 8)
                    end_position = byte_position + list_length
                    encoding_type = param.find("DIAG-CODED-TYPE").attrib[
                        "BASE-DATA-TYPE"
                    ]
                    if (encoding_type) == "A_ASCIISTRING":
                        function_string = "DecodeFunctions.int_list_to_string(input[{0}:{1}], None)".format(
                            byte_position, end_position
                        )
                    else:
                        function_string = "input[{1}:{2}]".format(
                            long_name, byte_position, end_position
                        )
                    encode_functions.append(
                        "result['{0}'] = {1}".format(long_name, function_string)
                    )
                if semantic == "DATA":
                    data_object_element = xml_elements[
                        (param.find("DOP-REF")).attrib["ID-REF"]
                    ]
                    long_name = param.find("LONG-NAME").text
                    byte_position = int(param.find("BYTE-POSITION").text)
                    bit_length = int(
                        data_object_element.find("DIAG-CODED-TYPE")
                        .find("BIT-LENGTH")
                        .text
                    )
                    list_length = int(bit_length / 8)
                    end_position = byte_position + list_length
                    encoding_type = data_object_element.find("DIAG-CODED-TYPE").attrib[
                        "BASE-DATA-TYPE"
                    ]
                    if (encoding_type) == "A_ASCIISTRING":
                        function_string = "DecodeFunctions.int_list_to_string(input[{0}:{1}], None)".format(
                            byte_position, end_position
                        )
                    elif encoding_type == "A_UINT32":
                        function_string = "input[{1}:{2}]".format(
                            long_name, byte_position, end_position
                        )
                    else:
                        function_string = "input[{1}:{2}]".format(
                            long_name, byte_position, end_position
                        )
                    encode_functions.append(
                        "result['{0}'] = {1}".format(long_name, function_string)
                    )

            except:
                pass

        encode_function_string = encode_positive_response_func_template.format(
            encode_positive_response_function_name, "\n    ".join(encode_functions)
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
