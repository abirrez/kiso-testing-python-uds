#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from math import ceil

from uds.uds_config_tool.FunctionCreation.iServiceMethodFactory import (
    IServiceMethodFactory,
)
from uds.uds_config_tool.UtilityFunctions import (
    get_bit_length_from_dop,
    get_diag_object_prop,
    get_long_name,
    get_param_with_semantic,
    get_positive_response,
    get_sdgs_data,
    get_sdgs_data_item,
    get_service_id_from_diag_service,
    get_short_name,
)

##
# Inputs
# Function name
# expected security response
requestFuncTemplate_getSeed = str(
    "def {0}(suppress_response=False):\n"
    "    securityRequest = {2}\n"
    "    if suppress_response: securityRequest |= 0x80\n"
    "    return [{1}, securityRequest]"
)

requestFuncTemplate_sendKey = str(
    "def {0}(key, suppress_response=False):\n"
    "    service_id = {1}\n"
    "    subFunction = {2}\n"
    "    if suppress_response: subFunction |= 0x80\n"
    "    return [service_id, subFunction] + key"
)

checkSidTemplate = str(
    "def {0}(sid):\n"
    "    expectedSid = {1}\n"
    '    if expectedSid != sid: raise Exception("SID do not match")'
)

checkSecurityAccessTemplate = str(
    "def {0}(securityAccess):\n"
    "    expectedSecurityAccess = {1}\n"
    '    if expectedSecurityAccess != securityAccess: raise Exception("Security Mode does not match")'
)

checkReturnedDataTemplate = str(
    "def {0}(data):\n"
    "    expectedDataLength = {1}\n"
    '    if expectedDataLength != len(data): raise Exception("Returned data length not expected")'
)

checkNegativeResponseTemplate = str(
    "def {0}(input):\n"
    "    result = {{}}\n"
    "    nrc_list = {1}\n"
    "    if input[0] == 0x7F:\n"
    "        result['NRC'] = input[2]\n"
    "        result['NRC_Label'] = nrc_list.get(result['NRC'])\n"
    "    return result"
)
##
# inputs:
# Length
checkInputDataTemplate = str(
    "def {0}(data):\n"
    "    expectedLength = {1}\n"
    "    if isinstance(data, list):\n"
    '        if len(data) != expectedLength: raise Exception("Input data does not match expected length")\n'
    "    else:"
    "        pass"
)


class SecurityAccessMethodFactory(object):

    __metaclass__ = IServiceMethodFactory

    ##
    # @brief method to create the request function for the service element
    @staticmethod
    def create_request_function(diag_service_element, xml_elements):
        service_id = 0x00
        securityRequest = 0x00

        # have to dig out the sgds name for this one
        request_element = xml_elements[
            diag_service_element.find("REQUEST-REF").attrib["ID-REF"]
        ]

        sdgsName = get_sdgs_data_item(diag_service_element, "DiagInstanceQualifier")

        service_id = get_service_id_from_diag_service(diag_service_element, xml_elements)
        accessMode = get_param_with_semantic(request_element, "ACCESSMODE")
        subfunction = get_param_with_semantic(request_element, "SUBFUNCTION")

        # if accessMode is not none then this is a seed request
        if accessMode is not None:
            securityRequest = int(
                get_param_with_semantic(request_element, "ACCESSMODE")
                .find("CODED-VALUE")
                .text
            )
            requestFuncString = requestFuncTemplate_getSeed.format(
                sdgsName, service_id, securityRequest
            )
        elif subfunction is not None:
            securityRequest = int(
                get_param_with_semantic(request_element, "SUBFUNCTION")
                .find("CODED-VALUE")
                .text
            )
            requestFuncString = requestFuncTemplate_sendKey.format(
                sdgsName, service_id, securityRequest
            )
        else:
            requestFuncString = None

        if requestFuncString is not None:
            exec(requestFuncString)
            return locals()[sdgsName]
        else:
            return None

    ##
    # @brief method to create the function to check the positive response for validity
    @staticmethod
    def create_check_positive_response_function(diag_service_element, xml_elements):
        response_id = 0
        securityRequest = 0

        response_id = get_service_id_from_diag_service(diag_service_element, xml_elements) + 0x40
        positive_response_element = get_positive_response(diag_service_element, xml_elements)

        diagInstanceQualifier = get_sdgs_data_item(
            diag_service_element, "DiagInstanceQualifier"
        )

        checkSidFunctionName = "check_{0}_sid".format(diagInstanceQualifier)
        checkSecurityAccessFunctionName = "check_{0}_securityAccess".format(
            diagInstanceQualifier
        )
        checkReturnedDataFunctionName = "check_{0}_returnedData".format(
            diagInstanceQualifier
        )

        accessmode = get_param_with_semantic(positive_response_element, "ACCESSMODE")
        subfunction = get_param_with_semantic(positive_response_element, "SUBFUNCTION")

        if accessmode is not None:
            securityRequest = int(accessmode.find("CODED-VALUE").text)
        elif subfunction is not None:
            securityRequest = int(subfunction.find("CODED-VALUE").text)
        else:
            raise Exception("Format not known")

        dataParams = get_param_with_semantic(positive_response_element, "DATA")

        if dataParams is not None:
            if isinstance(dataParams, list):
                raise Exception("Currently can not deal with lists of data")
            else:
                dop = get_diag_object_prop(dataParams, xml_elements)
                bit_length = get_bit_length_from_dop(dop)
                payload_length = int(ceil(bit_length / 8))
        else:
            payload_length = 0

        checkSidFunctionString = checkSidTemplate.format(
            checkSidFunctionName, response_id
        )

        checkSecurityAccessFunctionString = checkSecurityAccessTemplate.format(
            checkSecurityAccessFunctionName, securityRequest
        )

        if payload_length == 0:
            checkReturnedDataString = None
        else:
            checkReturnedDataString = checkReturnedDataTemplate.format(
                checkReturnedDataFunctionName, payload_length
            )
            exec(checkReturnedDataString)

        exec(checkSidFunctionString)
        exec(checkSecurityAccessFunctionString)

        check_sid_function = locals()[checkSidFunctionName]
        check_security_access_function = locals()[checkSecurityAccessFunctionName]

        checkReturnedDataFunction = None
        try:
            checkReturnedDataFunction = locals()[checkReturnedDataFunctionName]
        except:
            pass

        return check_sid_function, check_security_access_function, checkReturnedDataFunction

    ##
    # @brief method to encode the positive response from the raw type to it physical representation
    @staticmethod
    def create_encode_positive_response_function(diag_service_element, xml_elements):

        raise Exception("Not implemented")

    ##
    # @brief method to create the negative response function for the service element
    @staticmethod
    def create_check_negative_response_function(diag_service_element, xml_elements):

        diagInstanceQualifier = get_sdgs_data_item(
            diag_service_element, "DiagInstanceQualifier"
        )

        checkNegativeResponseFunctionName = "check_{0}_negResponse".format(
            diagInstanceQualifier
        )

        negative_responses_element = diag_service_element.find("NEG-RESPONSE-REFS")

        negative_response_checks = []

        for negative_response in negative_responses_element:
            negative_response_ref = xml_elements[negative_response.attrib["ID-REF"]]

            negative_response_params = negative_response_ref.find("PARAMS")

            for param in negative_response_params:
                byte_position = int(param.find("BYTE-POSITION").text)

                if byte_position == 2:
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

        checkNegativeResponseFunctionString = checkNegativeResponseTemplate.format(
            checkNegativeResponseFunctionName, expected_nrc_dict
        )
        exec(checkNegativeResponseFunctionString)

        return locals()[checkNegativeResponseFunctionName]

    @staticmethod
    def check_inputDataFunction(diag_service_element, xml_elements):

        diagInstanceQualifier = get_sdgs_data_item(
            diag_service_element, "DiagInstanceQualifier"
        )


if __name__ == "__main__":

    pass
