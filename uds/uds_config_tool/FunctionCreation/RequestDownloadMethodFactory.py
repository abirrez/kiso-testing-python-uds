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
    "def {0}(FormatIdentifier, MemoryAddress, MemorySize):\n"
    "    addrlenfid = [len(MemoryAddress) + (len(MemorySize)<<4)]\n"
    "    return {1} + FormatIdentifier + addrlenfid + MemoryAddress + MemorySize"
)

check_function_template = str(
    "def {0}(input):\n"
    "    serviceIdExpected = {1}\n"
    "    service_id = DecodeFunctions.build_int_from_list(input[{2}:{3}])\n"
    "    addrlenfid = DecodeFunctions.build_int_from_list(input[{3}:{3}+1]) # ... next byte\n"
    "    total_length = {4} + 1 + (addrlenfid>>4) # ... length of sid, length of addrlenfid, length of maxNumOfBlockLen extracted from addrlenfid\n"
    '    if(len(input) != total_length): raise Exception("Total length returned not as expected. Expected: total_length; Got {{0}}".format(len(input)))\n'
    '    if(service_id != serviceIdExpected): raise Exception("Service Id Received not expected. Expected {{0}}; Got {{1}} ".format(serviceIdExpected, service_id))'
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
    "def {0}(input):\n"
    "    result = {{}}\n"
    "    result['LengthFormatIdentifier'] = input[1:2]\n"
    "    lenMNOBL = (result['LengthFormatIdentifier'][0])>>4\n"
    "    result['MaxNumberOfBlockLength'] = input[2:2+lenMNOBL]\n"
    "    return result"
)


class RequestDownloadMethodFactory(IServiceMethodFactory):

    ##
    # @brief method to create the request function for the service element
    # The parameters for request download are fixed in format, so we can simply take fixed paramters and format the message accordingly
    # i.e. we're less reliant on what the odx file says in this case.
    @staticmethod
    def create_request_function(diag_service_element, xml_elements):
        service_id = 0

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
            elif semantic == "DATA":
                data_object_element = xml_elements[
                    (param.find("DOP-REF")).attrib["ID-REF"]
                ]
                break
                # ... if we've gotten this far, then we probably have enough from the ODX to ensure we have the service defined ... following the spec from here on.

        func_string = request_func_template.format(short_name, service_id)
        exec(func_string)
        return locals()[short_name]

    ##
    # @brief method to create the function to check the positive response for validity
    # The response for request download are fixed in format, so we can check the message accordingly
    # i.e. we're less reliant on what the odx file says in this case.
    @staticmethod
    def create_check_positive_response_function(diag_service_element, xml_elements):
        response_id = 0

        response_id_start = 0
        response_id_end = 0

        short_name = diag_service_element.find("SHORT-NAME").text
        check_function_name = "check_{0}".format(short_name)
        positive_response_element = xml_elements[
            (diag_service_element.find("POS-RESPONSE-REFS"))
            .find("POS-RESPONSE-REF")
            .attrib["ID-REF"]
        ]

        params_element = positive_response_element.find("PARAMS")

        response_length = 0

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
                    response_length += list_length

                elif semantic == "DATA":
                    data_object_element = xml_elements[
                        (param.find("DOP-REF")).attrib["ID-REF"]
                    ]
                    break
                # ... if we've gotten this far, then we probably have enough from the ODX to ensure we have the service defined ... following the spec from here on.

                else:
                    pass
            except:
                # print(sys.exc_info())
                pass

        check_function_string = check_function_template.format(
            check_function_name,  # 0
            response_id,  # 1
            response_id_start,  # 2
            response_id_end,  # 3
            response_length,
        )  # 4
        exec(check_function_string)
        return locals()[check_function_name]

    def create_encode_positive_response_function(diag_service_element, xml_elements):

        positive_response_element = xml_elements[
            (diag_service_element.find("POS-RESPONSE-REFS"))
            .find("POS-RESPONSE-REF")
            .attrib["ID-REF"]
        ]

        short_name = diag_service_element.find("SHORT-NAME").text
        encode_positive_response_function_name = "encode_{0}".format(short_name)

        params = positive_response_element.find("PARAMS")

        response_length = 0
        encode_functions = []

        for param in params:
            try:
                semantic = None
                try:
                    semantic = param.attrib["SEMANTIC"]
                except AttributeError:
                    pass

                if semantic == "SERVICE-ID":
                    response_id = int(param.find("CODED-VALUE").text)
                    bit_length = int(
                        (param.find("DIAG-CODED-TYPE")).find("BIT-LENGTH").text
                    )
                    list_length = int(bit_length / 8)
                    response_id_start = start_byte
                    response_id_end = start_byte + list_length
                    response_length += list_length

                if semantic == "DATA":
                    data_object_element = xml_elements[
                        (param.find("DOP-REF")).attrib["ID-REF"]
                    ]
                    break
            # ... if we've gotten this far, then we probably have enough from the ODX to ensure we have the service defined ... following the spec from here on.

            except:
                pass

        encode_function_string = encode_positive_response_func_template.format(
            encode_positive_response_function_name
        )
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
