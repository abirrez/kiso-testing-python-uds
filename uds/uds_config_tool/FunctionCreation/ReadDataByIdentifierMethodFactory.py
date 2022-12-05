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

# Extended to cater for multiple DIDs in a request - typically rather than processing
# a whole response in one go, we break it down and process each part separately.
# We can cater for multiple DIDs by then combining whatever calls we need to.

request_sid_func_template = str("def {0}():\n" "    return {1}")
request_did_func_template = str("def {0}():\n" "    return {1}")

check_sid_resp_func_template = str(
    "def {0}(input):\n"
    "    serviceIdExpected = {1}\n"
    "    service_id = DecodeFunctions.build_int_from_list(input[{2}:{3}])\n"
    '    if(service_id != serviceIdExpected): raise Exception("Service Id Received not expected. Expected {{0}}; Got {{1}} ".format(serviceIdExpected, service_id))'
)

check_sid_len_func_template = str("def {0}():\n" "    return {1}")

check_did_resp_func_template = str(
    "def {0}(input):\n"
    "    diagnosticIdExpected = {1}\n"
    "    diagnostic_id = DecodeFunctions.build_int_from_list(input[{2}:{3}])\n"
    '    if(diagnostic_id != diagnosticIdExpected): raise Exception("Diagnostic Id Received not as expected. Expected: {{0}}; Got {{1}}".format(diagnosticIdExpected, diagnostic_id))'
)

check_did_len_func_template = str("def {0}():\n" "    return {1}")

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
    "def {0}(input,offset):\n" "    result = {{}}\n" "    {1}\n" "    return result"
)


##
# @brief this should be static
class read_data_by_identifierMethodFactory(IServiceMethodFactory):
    @staticmethod
    def create_requestFunctions(diag_service_element, xml_elements):

        service_id = 0
        diagnostic_id = 0

        short_name = "request_{0}".format(diag_service_element.find("SHORT-NAME").text)
        request_sid_func_name = "requestSID_{0}".format(short_name)
        request_did_func_name = "requestDID_{0}".format(short_name)
        request_element = xml_elements[
            diag_service_element.find("REQUEST-REF").attrib["ID-REF"]
        ]
        params_element = request_element.find("PARAMS")
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

        func_string = request_sid_func_template.format(
            request_sid_func_name, service_id  # 0
        )  # 1
        exec(func_string)

        func_string = request_did_func_template.format(
            request_did_func_name, diagnostic_id  # 0
        )  # 1
        exec(func_string)

        return (locals()[request_sid_func_name], locals()[request_did_func_name])

    @staticmethod
    def create_checkPositiveResponseFunctions(diag_service_element, xml_elements):

        response_id = 0
        diagnostic_id = 0

        response_id_start = 0
        response_id_end = 0
        diagnostic_id_start = 0
        diagnostic_id_end = 0

        short_name = diag_service_element.find("SHORT-NAME").text
        check_sid_resp_func_name = "checkSIDResp_{0}".format(short_name)
        check_sid_len_func_name = "checkSIDLen_{0}".format(short_name)
        check_did_resp_func_name = "checkDIDResp_{0}".format(short_name)
        check_did_len_func_name = "checkDIDLen_{0}".format(short_name)
        positive_response_element = xml_elements[
            (diag_service_element.find("POS-RESPONSE-REFS"))
            .find("POS-RESPONSE-REF")
            .attrib["ID-REF"]
        ]

        params_element = positive_response_element.find("PARAMS")

        total_length = 0
        sid_length = 0

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
                    sid_length = list_length
                elif semantic == "ID":
                    diagnostic_id = int(param.find("CODED-VALUE").text)
                    bit_length = int(
                        (param.find("DIAG-CODED-TYPE")).find("BIT-LENGTH").text
                    )
                    list_length = int(bit_length / 8)
                    diagnostic_id_start = start_byte
                    diagnostic_id_end = start_byte + list_length
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

        check_sid_resp_func_string = check_sid_resp_func_template.format(
            check_sid_resp_func_name,  # 0
            response_id,  # 1
            response_id_start,  # 2
            response_id_end,
        )  # 3
        exec(check_sid_resp_func_string)
        check_sid_len_func_string = check_sid_len_func_template.format(
            check_sid_len_func_name, sid_length  # 0
        )  # 1
        exec(check_sid_len_func_string)
        check_did_resp_func_string = check_did_len_func_template.format(
            check_did_resp_func_name,  # 0
            diagnostic_id,  # 1
            diagnostic_id_start
            - sid_length,  # 2... note: we no longer look at absolute pos in the response,
            diagnostic_id_end - sid_length,
        )  # 3      but look at the DID response as an isolated extracted element.
        exec(check_did_resp_func_string)
        check_did_len_func_string = check_did_len_func_template.format(
            check_did_len_func_name, total_length - sid_length  # 0
        )  # 1
        exec(check_did_len_func_string)

        return (
            locals()[check_sid_resp_func_name],
            locals()[check_sid_len_func_name],
            locals()[check_did_resp_func_name],
            locals()[check_did_len_func_name],
        )

    ##
    # @brief may need refactoring to deal with multiple positive-responses (WIP)
    @staticmethod
    def create_encode_positive_response_function(diag_service_element, xml_elements):

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
                        function_string = "DecodeFunctions.int_list_to_string(input[{0}-offset:{1}-offset], None)".format(
                            byte_position, end_position
                        )
                    elif encoding_type == "A_UINT32":
                        function_string = "input[{1}-offset:{2}-offset]".format(
                            long_name, byte_position, end_position
                        )
                    else:
                        function_string = "input[{1}-offset:{2}-offset]".format(
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

    @staticmethod
    def create_check_negative_response_function(diag_service_element, xml_elements):

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
                            expected_nrc_dict[int(nrc_elem.find("LOWER-LIMIT").text)] = (
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
