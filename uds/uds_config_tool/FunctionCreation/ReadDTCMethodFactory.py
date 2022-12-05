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

# Note: the request is not the simplest to parse from the ODX, so paritally hardcoding this one again (for now at least)
request_func_template = str(
    "def {0}(DTC_status_mask=[],DTC_mask_record=[],DTC_snapshot_record_number=[],DTC_extended_record_number=[],DTC_severity_mask=[]):\n"
    "    encoded = []\n"
    "    {3}\n"
    "    return {1} + {2} + encoded # ... SID, sub-func, and params"
)

check_function_template = str(
    "def {0}(input):\n"
    "    serviceIdExpected = {1}\n"
    "    subFunctionExpected = {2}\n"
    "    service_id = DecodeFunctions.build_int_from_list(input[{3}:{4}])\n"
    "    subFunction = DecodeFunctions.build_int_from_list(input[{5}:{6}])\n"
    '    if(service_id != serviceIdExpected): raise Exception("Service Id Received not expected. Expected {{0}}; Got {{1}} ".format(serviceIdExpected, service_id))\n'
    '    if(subFunction != subFunctionExpected): raise Exception("Sub-function Received not expected. Expected {{0}}; Got {{1}} ".format(subFunctionExpected, subFunction))\n'
    "{7}"
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
    "    encoded = []\n"
    "    retval = None\n"
    "{1}\n"
    "    return retval"
)


class ReadDTCMethodFactory(IServiceMethodFactory):

    ##
    # @brief method to create the request function for the service element
    @staticmethod
    def create_request_function(diag_service_element, xml_elements):
        # Note: due to the compleixty of the call, this one is partially hardcoded - we do at least check the ODX file far enough to ensure that the request and subfunction are accurate.
        service_id = 0
        diagnostic_id = 0

        short_name = "request_{0}".format(diag_service_element.find("SHORT-NAME").text)
        request_element = xml_elements[
            diag_service_element.find("REQUEST-REF").attrib["ID-REF"]
        ]
        params_element = request_element.find("PARAMS")
        encode_string = ""

        for param in params_element:
            semantic = None
            try:
                semantic = param.attrib["SEMANTIC"]
            except AttributeError:
                pass
            except KeyError:
                pass

            if semantic == "SERVICE-ID":
                service_id = [int(param.find("CODED-VALUE").text)]
            elif semantic == "SUBFUNCTION":
                short_name += param.find("SHORT-NAME").text
                subfunction = DecodeFunctions.int_array_to_int_array(
                    [int(param.find("CODED-VALUE").text)], "int8", "int8"
                )
                if subfunction[0] in [
                    0x01,
                    0x02,
                    0x0F,
                    0x11,
                    0x12,
                    0x13,
                ]:  # ... DTC_status_mask required for these subfunctions
                    encode_string = "encoded += DTC_status_mask"
                elif subfunction[0] in [
                    0x03,
                    0x04,
                    0x06,
                    0x09,
                    0x10,
                ]:  # ... DTC_mask_record required for these subfunctions
                    encode_string = (
                        "encoded += DTC_mask_record # ... format is [0xNN,0xNN,0xNN]"
                    )
                elif subfunction[0] in [
                    0x03,
                    0x04,
                    0x05,
                ]:  # ... DTC_snapshot_record_number required for these subfunctions
                    encode_string = "encoded += DTC_snapshot_record_number"
                elif subfunction[0] in [
                    0x06,
                    0x10,
                ]:  # ... DTC_extended_record_number required for these subfunctions
                    encode_string = "encoded += DTC_extended_record_number"
                elif subfunction[0] in [
                    0x07,
                    0x08,
                ]:  # ... DTCSeverityMaskRecord required for these subfunctions
                    encode_string = "encoded += DTC_severity_mask+DTC_status_mask"

        func_string = request_func_template.format(
            short_name, service_id, subfunction, encode_string
        )
        exec(func_string)
        return (locals()[short_name], str(subfunction))

    ##
    # @brief method to create the function to check the positive response for validity
    @staticmethod
    def create_check_positive_response_function(diag_service_element, xml_elements):
        response_id = 0
        subfunction = 0

        response_id_start = 0
        response_id_end = 0
        subfunction_start = 0
        subfunction_end = 0

        short_name = diag_service_element.find("SHORT-NAME").text
        check_function_name = "check_{0}".format(short_name)
        positive_response_element = xml_elements[
            (diag_service_element.find("POS-RESPONSE-REFS"))
            .find("POS-RESPONSE-REF")
            .attrib["ID-REF"]
        ]

        params_element = positive_response_element.find("PARAMS")

        total_length = 0
        subfunction_checks = ""

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
                    subfunction = int(param.find("CODED-VALUE").text)
                    bit_length = int(
                        (param.find("DIAG-CODED-TYPE")).find("BIT-LENGTH").text
                    )
                    list_length = int(bit_length / 8)
                    subfunction_start = start_byte
                    subfunction_end = start_byte + list_length
                    total_length += list_length

                    if subfunction in [
                        0x02,
                        0x0A,
                        0x0B,
                        0x0C,
                        0x0D,
                        0x0E,
                        0x0F,
                        0x13,
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_checks += '    if len(input) < 3: raise Exception("Total length returned not as expected. Expected: greater than or equal to 3; Got {{0}}".format(len(input)))\n'
                        subfunction_checks += '    if (len(input)-3)%4 != 0: raise Exception("Total length returned not as expected. Received a partial DTC and Status Record; Got {{0}} total length".format(len(input)))\n'
                    elif subfunction in [
                        0x01,
                        0x07,
                        0x11,
                        0x12,
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_checks += '    if len(input) != 6: raise Exception("Total length returned not as expected. Expected: 6; Got {{0}}".format(len(input)))\n'
                    elif subfunction in [
                        0x03
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_checks += '    if len(input) < 2: raise Exception("Total length returned not as expected. Expected: greater than or equal to 2; Got {{0}}".format(len(input)))\n'
                        subfunction_checks += '    if (len(input)-2)%4 != 0: raise Exception("Total length returned not as expected. Received a partial DTC and Snapshot Record Number; Got {{0}} total length".format(len(input)))\n'
                    elif subfunction in [
                        0x04
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_checks += "    pass #??? ... we need to parse the ODX for DTC length detials or this one, so leaving till spoken to Richard ???\n"
                    elif subfunction in [
                        0x05
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_checks += "    pass #??? ... we need to parse the ODX for DTC length detials or this one, so leaving till spoken to Richard ???\n"
                    elif subfunction in [
                        0x06,
                        0x10,
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_checks += "    pass #??? ... we need to parse the ODX for DTC length detials or this one, so leaving till spoken to Richard ???\n"
                    elif subfunction in [
                        0x08,
                        0x09,
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_checks += '    if len(input) < 3: raise Exception("Total length returned not as expected. Expected: greater than or equal to 3; Got {{0}}".format(len(input)))\n'
                        subfunction_checks += '    if (len(input)-3)%6 != 0: raise Exception("Total length returned not as expected. Received a partial DTC and Severity Record; Got {{0}} total length".format(len(input)))\n'

                else:
                    pass
            except:
                # print(sys.exc_info())
                pass

        check_function_string = check_function_template.format(
            check_function_name,  # 0
            response_id,  # 1
            subfunction,  # 2
            response_id_start,  # 3
            response_id_end,  # 4
            subfunction_start,  # 5
            subfunction_end,  # 6
            subfunction_checks,
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
        positive_response_element = xml_elements[
            (diag_service_element.find("POS-RESPONSE-REFS"))
            .find("POS-RESPONSE-REF")
            .attrib["ID-REF"]
        ]

        params_element = positive_response_element.find("PARAMS")
        subfunction_response = ""

        for param in params_element:
            try:
                semantic = None
                try:
                    semantic = param.attrib["SEMANTIC"]
                except AttributeError:
                    pass

                if semantic == "SUBFUNCTION":
                    subfunction = int(param.find("CODED-VALUE").text)
                    if subfunction in [
                        0x02,
                        0x0A,
                        0x0B,
                        0x0C,
                        0x0D,
                        0x0E,
                        0x0F,
                        0x13,
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_response += "    retval = {'DTCStatusAvailabilityMask':input[2:3], 'DTCAndStatusRecord':[]}\n"
                        subfunction_response += "    records = input[3:]\n"
                        subfunction_response += (
                            "    for i in range(int(len(records)/4)):\n"
                        )
                        subfunction_response += "        recStart = i*4\n"
                        subfunction_response += "        retval['DTCAndStatusRecord'].append({'DTC':records[recStart:recStart+3],'statusOfDTC':records[recStart+3:recStart+4]})\n"
                    elif subfunction in [
                        0x01,
                        0x07,
                        0x11,
                        0x12,
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_response += "    retval = {'DTCStatusAvailabilityMask':input[2:3], 'DTCFormatIdentifier':input[3:4], 'DTCCount':[(input[4]<<8)+input[5]]}  # ... DTCCount decoded as int16\n"
                    elif subfunction in [
                        0x03
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_response += "    retval = []\n"
                        subfunction_response += "    records = input[3:]\n"
                        subfunction_response += (
                            "    for i in range(int(len(records)/4)):\n"
                        )
                        subfunction_response += "        recStart = i*4\n"
                        subfunction_response += "        retval.append({'DTC':records[recStart:recStart+3],'DTC_snapshot_record_number':records[recStart+3:recStart+4]})\n"
                    elif subfunction in [
                        0x04
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_response += "    pass #??? ... we need to parse the ODX for DTC length detials or this one, so leaving till spoken to Richard ???\n"
                    elif subfunction in [
                        0x05
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_response += "    pass #??? ... we need to parse the ODX for DTC length detials or this one, so leaving till spoken to Richard ???\n"
                    elif subfunction in [
                        0x06,
                        0x10,
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_response += "    pass #??? ... we need to parse the ODX for DTC length detials or this one, so leaving till spoken to Richard ???\n"
                    elif subfunction in [
                        0x08,
                        0x09,
                    ]:  # ... DTC_status_mask required for these subfunctions
                        subfunction_response += "    retval = {'DTCStatusAvailabilityMask':input[2:3], 'DTCAndSeverityRecord':[]}\n"
                        subfunction_response += "    records = input[3:]\n"
                        subfunction_response += (
                            "    for i in range(int(len(records)/6)):\n"
                        )
                        subfunction_response += "        recStart = i*6\n"
                        subfunction_response += "        retval['DTCAndSeverityRecord'].append({'DTCSeverity':records[recStart:recStart+1],'DTCFunctionalUnit':records[recStart+1:recStart+2],'DTC':records[recStart+2:recStart+5],'statusOfDTC':records[recStart+5:recStart+6]})\n"
            except:
                pass

        encode_function_string = encode_positive_response_func_template.format(
            encode_positive_response_function_name, subfunction_response  # 0
        )  # 1
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
