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

# When encode the dataRecord for transmission we have to allow for multiple elements in the data record
# i.e. 'value1' - for a single value, or [('param1','value1'),('param2','value2')]  for more complex data records
request_func_template = str(
    "def {0}(dataRecord):\n"
    "    encoded = []\n"
    "    if type(dataRecord) == list and type(dataRecord[0]) == tuple:\n"
    "        drDict = dict(dataRecord)\n"
    "        {3}\n"
    "{4}\n"
    "    return {1} + {2} + encoded"
)


check_function_template = str(
    "def {0}(input):\n"
    "    serviceIdExpected = {1}\n"
    "    diagnosticIdExpected = {2}\n"
    "    service_id = DecodeFunctions.build_int_from_list(input[{3}:{4}])\n"
    "    diagnostic_id = DecodeFunctions.build_int_from_list(input[{5}:{6}])\n"
    '    if(len(input) != {7}): raise Exception("Total length returned not as expected. Expected: {7}; Got {{0}}".format(len(input)))\n'
    '    if(service_id != serviceIdExpected): raise Exception("Service Id Received not expected. Expected {{0}}; Got {{1}} ".format(serviceIdExpected, service_id))\n'
    '    if(diagnostic_id != diagnosticIdExpected): raise Exception("Diagnostic Id Received not as expected. Expected: {{0}}; Got {{1}}".format(diagnosticIdExpected, diagnostic_id))'
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

encode_positive_response_func_template = str("def {0}(input):\n" "    return")


class WriteDataByIdentifierMethodFactory(IServiceMethodFactory):

    ##
    # @brief method to create the request function for the service element
    @staticmethod
    def create_request_function(diag_service_element, xml_elements):
        service_id = 0
        diagnostic_id = 0

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
            elif semantic == "ID":
                diagnostic_id = DecodeFunctions.int_array_to_int_array(
                    [int(param.find("CODED-VALUE").text)], "int16", "int8"
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
                    encoding_type = "unknown"  # ... for now just drop into the "else" catch-all ??????????????????????????????????????????????
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

                """
The following encoding types may be required at some stage, but are not currently supported by any functions in the DecodeFunctions.py module ...

    A_VOID: pseudo type for non-existing elements
    A_BIT: one bit
    A_INT64: signed integer 64-bit, two's complement
    A_FLOAT32: IEEE 754 single precision
    A_FLOAT64: IEEE 754 double precision
    A_ASCIISTRING: string, ISO-8859-1 encoded
    A_UTF8STRING: string, UTF-8 encoded
    A_UNICODE2STRING: string, UCS-2 encoded
    A_BYTEFIELD: Field of bytes
	
Also, we will most need to handle scaling at some stage within DecodeFunctions.py (for RDBI at the very least)
                """

                #
                encode_functions.append(
                    "encoded += {1}".format(long_name, function_string_list)
                )
                encode_function = "    else:\n        encoded = {1}".format(
                    long_name, function_string_single
                )

        # If we have only a single value for the dataRecord to send, then we can simply suppress the single value sending option.
        # Note: in the reverse case, we do not suppress the dictionary method of sending, as this allows extra flexibility, allowing
        # a user to use a consistent list format in all situations if desired.
        if len(encode_functions) > 1:
            encode_function = ""

        func_string = request_func_template.format(
            short_name,
            service_id,
            diagnostic_id,
            "\n        ".join(encode_functions),  # ... handles input via list
            encode_function,
        )  # ... handles input via single value
        exec(func_string)
        return locals()[short_name]

    ##
    # @brief method to create the function to check the positive response for validity
    @staticmethod
    def create_check_positive_response_function(diag_service_element, xml_elements):
        response_id = 0
        diagnostic_id = 0

        response_id_start = 0
        response_id_end = 0
        diagnostic_id_start = 0
        diagnostic_id_end = 0

        short_name = diag_service_element.find("SHORT-NAME").text
        check_function_name = "check_{0}".format(short_name)
        positive_response_element = xml_elements[
            (diag_service_element.find("POS-RESPONSE-REFS"))
            .find("POS-RESPONSE-REF")
            .attrib["ID-REF"]
        ]

        params_element = positive_response_element.find("PARAMS")

        total_length = 0

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
                else:
                    pass
            except:
                # print(sys.exc_info())
                pass

        check_function_string = check_function_template.format(
            check_function_name,  # 0
            response_id,  # 1
            diagnostic_id,  # 2
            response_id_start,  # 3
            response_id_end,  # 4
            diagnostic_id_start,  # 5
            diagnostic_id_end,  # 6
            total_length,
        )  # 7
        exec(check_function_string)
        return locals()[check_function_name]

    ##
    # @brief method to encode the positive response from the raw type to it physical representation
    @staticmethod
    def create_encode_positive_response_function(diag_service_element, xml_elements):
        # There's nothing to extract here! The only value in the response is the DID, checking of which is handled in the check function,
        # so must be present and ok. This function is only required to return the default None response.

        short_name = diag_service_element.find("SHORT-NAME").text
        encode_positive_response_function_name = "encode_{0}".format(short_name)

        encode_function_string = encode_positive_response_func_template.format(
            encode_positive_response_function_name
        )  # 0
        exec(encode_function_string)
        return locals()[encode_positive_response_function_name]

    ##
    # @brief method to create the negative response function for the service element
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
