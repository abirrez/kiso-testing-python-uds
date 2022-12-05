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

# When encode the dataRecord for transmission we allow for multiple elements in the data record,
# i.e. IO Ctrl always has the option and mask records in the request
request_func_template = str(
    "def {0}(dataRecord):\n"
    "    encoded = []\n"
    "    if type(dataRecord) == list and type(dataRecord[0]) == tuple:\n"
    "        drDict = dict(dataRecord)\n"
    "        {4}\n"
    "{5}\n"
    "    return {1} + {2} + {3} + encoded"
)

check_function_template = str(
    "def {0}(input):\n"
    "    serviceIdExpected = {1}\n"
    "    diagnosticIdExpected = {2}\n"
    "    optionRecordExpected = {3}\n"
    "    service_id = DecodeFunctions.build_int_from_list(input[{4}:{5}])\n"
    "    diagnostic_id = DecodeFunctions.build_int_from_list(input[{6}:{7}])\n"
    "    option_record = DecodeFunctions.build_int_from_list(input[{8}:{9}])\n"
    '    if(len(input) != {10}): raise Exception("Total length returned not as expected. Expected: {10}; Got {{0}}".format(len(input)))\n'
    '    if(service_id != serviceIdExpected): raise Exception("Service Id Received not expected. Expected {{0}}; Got {{1}} ".format(serviceIdExpected, service_id))\n'
    '    if(diagnostic_id != diagnosticIdExpected): raise Exception("Diagnostic Id Received not as expected. Expected: {{0}}; Got {{1}}".format(diagnosticIdExpected, diagnostic_id))\n'
    '    if(option_record != optionRecordExpected): raise Exception("Option Record Received not as expected. Expected: {{0}}; Got {{1}}".format(optionRecordExpected, option_record))'
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

encode_positive_response_func_template = str(
    "def {0}(input):\n" "    result = {{}}\n" "    {1}\n" "    return result"
)


class InputOutputControlMethodFactory(IServiceMethodFactory):

    ##
    # @brief method to create the request function for the service element
    @staticmethod
    def create_request_function(diag_service_element, xml_elements):
        service_id = 0
        diagnostic_id = 0
        option_record = 0

        short_name = "request_{0}".format(diag_service_element.find("SHORT-NAME").text)
        request_element = xml_elements[
            diag_service_element.find("REQUEST-REF").attrib["ID-REF"]
        ]
        params_element = request_element.find("PARAMS")

        encode_functions = []
        encode_function = ""

        for param in params_element:
            semantic = None
            try:
                semantic = param.attrib["SEMANTIC"]
            except AttributeError:
                pass

            if semantic == "SERVICE-ID":
                service_id = [int(param.find("CODED-VALUE").text)]
            elif semantic == "ID":
                diagnostic_id = DecodeFunctions.int_array_to_int_array(
                    [int(param.find("CODED-VALUE").text)], "int16", "int8"
                )
            elif semantic == "SUBFUNCTION":
                option_record = DecodeFunctions.int_array_to_int_array(
                    [int(param.find("CODED-VALUE").text)], "int8", "int8"
                )
            elif semantic == "DATA":
                data_object_element = xml_elements[
                    (param.find("DOP-REF")).attrib["ID-REF"]
                ]
                long_name = param.find("LONG-NAME").text
                byte_position = int(param.find("BYTE-POSITION").text)
                # Catching any exceptions where we don't know the type - these will fail elsewhere, but at least we can test what does work.
                try:
                    encoding_type = data_object_element.find("DIAG-CODED-TYPE").attrib[
                        "BASE-DATA-TYPE"
                    ]
                    bit_length = (
                        data_object_element.find("DIAG-CODED-TYPE")
                        .find("BIT-LENGTH")
                        .text
                    )
                except:
                    encoding_type = (
                        "unknown"  # ... for now just drop into the "else" catch-all
                    )
                if (encoding_type) == "A_ASCIISTRING":
                    function_string_list = (
                        "DecodeFunctions.string_to_int_list(drDict['{0}'], None)".format(
                            long_name
                        )
                    )
                    function_string_single = (
                        "DecodeFunctions.string_to_int_list(dataRecord, None)"
                    )
                elif encoding_type in (
                    "A_INT8",
                    "A_INT16",
                    "A_INT32",
                    "A_UINT8",
                    "A_UINT16",
                    "A_UINT32",
                ):
                    function_string_list = "DecodeFunctions.int_value_to_byte_array(drDict['{0}'], {1})".format(
                        long_name, bit_length
                    )
                    function_string_single = (
                        "DecodeFunctions.int_value_to_byte_array(dataRecord, {0})".format(
                            bit_length
                        )
                    )
                else:
                    function_string_list = "drDict['{0}']".format(long_name)
                    function_string_single = "dataRecord"

                #
                encode_functions.append(
                    "encoded += {1}".format(long_name, function_string_list)
                )
                encode_function = "    else:\n        encoded = {1}".format(
                    long_name, function_string_single
                )

        func_string = request_func_template.format(
            short_name,
            service_id,
            diagnostic_id,
            option_record,
            "\n        ".join(encode_functions),  # ... handles input via list
            encode_function,
        )  # ... handles input via single value

        exec(func_string)
        return (locals()[short_name], str(option_record))

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
        diagnostic_id = 0
        option_record = 0

        response_id_start = 0
        response_id_end = 0
        diagnostic_id_start = 0
        diagnostic_id_end = 0
        option_record_start = 0
        option_record_end = 0

        short_name = diag_service_element.find("SHORT-NAME").text
        check_function_name = "check_{0}".format(short_name)
        positive_response_element = xml_elements[
            (diag_service_element.find("POS-RESPONSE-REFS"))
            .find("POS-RESPONSE-REF")
            .attrib["ID-REF"]
        ]

        params_element = positive_response_element.find("PARAMS")

        total_length = 0
        power_down_time_len = 0

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
                elif semantic == "ID":
                    diagnostic_id = int(param.find("CODED-VALUE").text)
                    bit_length = int(
                        (param.find("DIAG-CODED-TYPE")).find("BIT-LENGTH").text
                    )
                    list_length = int(bit_length / 8)
                    diagnostic_id_start = start_byte
                    diagnostic_id_end = start_byte + list_length
                    total_length += list_length
                elif semantic == "SUBFUNCTION":
                    option_record = int(param.find("CODED-VALUE").text)
                    bit_length = int(
                        (param.find("DIAG-CODED-TYPE")).find("BIT-LENGTH").text
                    )
                    list_length = int(bit_length / 8)
                    option_record_start = start_byte
                    option_record_end = start_byte + list_length
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
            diagnostic_id,  # 2
            option_record,  # 3
            response_id_start,  # 4
            response_id_end,  # 5
            diagnostic_id_start,  # 6
            diagnostic_id_end,  # 7
            option_record_start,  # 8
            option_record_end,  # 9
            total_length,
        )  # 10
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

        # The values in the response include SID and DID, but these do not need to be returned (and already checked in the check function).

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
                if semantic == "ID":
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
