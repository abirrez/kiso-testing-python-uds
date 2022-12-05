"""This file is an experiment and should not be used for any serious coding"""

import xml.etree.ElementTree as ET
from types import MethodType

from uds import DecodeFunctions, Uds


def get_diag_service_service_id(diag_service_element, requests):

    request_element_ref = diag_service_element.find("REQUEST-REF").attrib["ID-REF"]

    request_element = requests[request_element_ref]
    request_element_params_element = request_element.find("PARAMS")

    try:
        for i in request_element_params_element:
            if i.attrib["SEMANTIC"] == "SERVICE-ID":
                return int(i.find("CODED-VALUE").text)
    except AttributeError:
        return None

    return None


def create_sessionControlRequest_function(xml_element):

    service_id = None
    sub_function = None
    params = xml_element.find("PARAMS")
    for param in params:
        if param.attrib["SEMANTIC"] == "SERVICE-ID":
            service_id = int(param.find("CODED-VALUE").text)
        if param.attrib["SEMANTIC"] == "SUBFUNCTION":
            sub_function = int(param.find("CODED-VALUE").text)

    req = [service_id, sub_function]
    function_name = str("request_{0}").format((xml_element.find("SHORT-NAME")).text)

    func = str("def {0}():\n" "    return {1}").format(function_name, req)
    exec(func)
    return locals()[function_name]


def create_read_data_by_identifierRequest_function(xml_element):

    service_id = None
    diagnostic_id = None

    params = xml_element.find("PARAMS")

    for param in params:
        semantic = param.attrib["SEMANTIC"]
        if semantic == "SERVICE-ID":
            service_id = int(param.find("CODED-VALUE").text)
        if semantic == "ID":
            diagnostic_id = int(param.find("CODED-VALUE").text)

    req = [service_id] + DecodeFunctions.int_array_to_int_array(
        [diagnostic_id], "int16", "int8"
    )
    function_name = str("request_{0}").format(xml_element.find("SHORT-NAME").text)

    func = str("def {0}():\n" "    return {1}").format(function_name, req)
    exec(func)
    return locals()[function_name]


def create_writeDataByIdentifierRequest_function(xml_element, dataObjects):

    service_id = None
    diagnostic_id = None

    params = xml_element.find("PARAMS")

    check_function = ""
    encode_function = ""
    input_params = []
    index = 1

    for param in params:
        semantic = param.attrib["SEMANTIC"]
        if semantic == "SERVICE-ID":
            service_id = int(param.find("CODED-VALUE").text)
        if semantic == "ID":
            diagnostic_id = int(param.find("CODED-VALUE").text)
        if semantic == "DATA":
            dataObject = dataObjects[param.find("DOP-REF").attrib["ID-REF"]]
            diag_coded_type = dataObject.find("DIAG-CODED-TYPE")
            dataType = diag_coded_type.attrib["BASE-DATA-TYPE"]
            length = int(diag_coded_type.find("BIT-LENGTH").text)
            if dataType == "A_ASCIISTRING":
                inputParam = str("aString{0}").format(index)
                input_params.append(inputParam)
                index += 1
                check_function += str(
                    'if(len({1})) != {0}: raise Exception(str("incorrect length of input string. Got: {{0}}: Expected {0}").format(len({1})))'
                ).format(int(length / 8), inputParam)
                encode_function += str(
                    " + DecodeFunctions.string_to_int_list({0}, None)"
                ).format(inputParam)
            elif dataType == "A_UINT32":
                inputParam = str("aInt{0}").format(index)
                input_params.append(inputParam)
                index += 1
                numOfBytes = int(length / 8)
                if numOfBytes == 1:
                    input_type = "int8"
                elif numOfBytes == 2:
                    input_type = "int16"
                elif numOfBytes == 3:
                    input_type = "int24"
                elif numOfBytes == 4:
                    input_type = "int32"
                encode_function += str(
                    " + DecodeFunctions.int_array_to_uint8_array([{0}], '{1}')"
                ).format(inputParam, input_type)
            else:
                print("Unknown datatype")

    req = [service_id] + DecodeFunctions.int_array_to_int_array(
        [diagnostic_id], "int16", "int8"
    )
    function_name = str("request_{0}").format(xml_element.find("SHORT-NAME").text)

    try:
        func = str("def {0}({1}):\n" "    {2}\n" "    return {3}{4}").format(
            function_name, ", ".join(input_params), check_function, req, encode_function
        )
    except:
        pass
    exec(func)
    return locals()[function_name]


class RequestMethodFactory(object):
    def createRequestMethod(xml_element, dataObjects):
        function = None

        # extract the service ID to find out how this needs to be decoded
        params_element = xml_element.find("PARAMS")
        params = {}
        short_name = xml_element.find("SHORT-NAME").text
        id = xml_element.attrib["ID"]
        for param in params_element:
            try:
                params[param.attrib["SEMANTIC"]] = param
            except:
                print("Found param with no semantic field")
                pass

        service_id = int(params["SERVICE-ID"].find("CODED-VALUE").text)

        a = None
        # call the relevant method to create the dynamic function
        if service_id == 0x10:
            a = create_sessionControlRequest_function(xml_element)
        if service_id == 0x22:
            a = create_read_data_by_identifierRequest_function(xml_element)
        elif service_id == 0x2E:
            try:
                a = create_writeDataByIdentifierRequest_function(
                    xml_element, dataObjects
                )
            except:
                print("Failed to create WDBI function")

        if a is not None:
            if service_id != 0x2E:
                print(a())
            else:
                try:
                    print(a("0000000000000009"))
                except:
                    pass
                try:
                    print(a(0x01, "000000000000000000000000"))
                except:
                    pass
                pass
        pass

        return a


class PositiveResponseFactory(object):
    def __init__(self, xml_element, dataObjectElements):
        pass


class NegativeResponse(object):

    pass


def fillDictionary(xml_element):
    dict = {}

    for i in xml_element:
        dict[i.attrib["ID"]] = i

    return dict


def create_udsConnection(xml_element, ecuName):

    data_object_props_element = None
    diag_comms_element = None
    requests_element = None
    pos_responses_element = None
    neg_responses_element = None

    for child in xml_element.iter():
        if child.tag == "DATA-OBJECT-PROPS":
            data_object_props_element = child
        elif child.tag == "DIAG-COMMS":
            diag_comms_element = child
        elif child.tag == "REQUESTS":
            requests_element = child
        elif child.tag == "POS-RESPONSES":
            pos_responses_element = child
        elif child.tag == "NEG-RESPONSES":
            neg_responses_element = child

    data_object_props = fillDictionary(data_object_props_element)
    requests = fillDictionary(requests_element)
    pos_responses = fillDictionary(pos_responses_element)
    neg_responses = fillDictionary(neg_responses_element)

    request_functions = {}
    check_functions = {}
    positive_response_functions = {}
    negative_response_functions = {}

    for i in diag_comms_element:
        request_ref = None
        pos_response_ref = None
        neg_response_ref = None
        short_name = i.find("SHORT-NAME").text

        test = get_diag_service_service_id(i, requests)

        dictEntry = ""
        sdgs = i.find("SDGS")
        sdg = sdgs.find("SDG")
        for j in sdg:
            if j.tag == "SD":
                if j.attrib["SI"] == "DiagInstanceName":
                    dictEntry = j.text

        print(dictEntry)
        request_ref = i.find("REQUEST-REF")
        try:
            pos_response_ref = (i.find("POS-RESPONSE-REFS")).find("POS-RESPONSE-REF")
            neg_response_ref = (i.find("NEG-RESPONSE-REFS")).find("NEG-RESPONSE-REF")
        except (KeyError, AttributeError):
            pos_response_ref = None
            neg_response_ref = None

        request_element = requests[request_ref.attrib["ID-REF"]]
        request_function = RequestMethodFactory.createRequestMethod(
            request_element, data_object_props
        )

        if pos_response_ref != None:
            posResponseElement = pos_responses[pos_response_ref.attrib["ID-REF"]]
            posResponse = PositiveResponseFactory(posResponseElement, data_object_props)
        if neg_response_ref != None:
            negResponseElement = neg_responses[neg_response_ref.attrib["ID-REF"]]

        request_functions[short_name] = request_function

    temp_ecu = Uds()

    setattr(temp_ecu, "__request_functions", request_functions)

    print(request_functions)

    temp_ecu.read_data_by_identifier = MethodType(read_data_by_identifier, temp_ecu)

    print("successfully created ECU")

    return temp_ecu


def read_data_by_identifier(self, diagnosticIdentifier):

    request_function = self.__request_functions[diagnosticIdentifier]
    # check_function = self.__checkFunctions[diagnosticIdentifier]
    # negative_response_function = self.__negativeResponseFunctions[diagnosticIdentifier]
    # positive_response_function = self.__positiveResponseFunctions[diagnosticIdentifier]

    print(request_function())


if __name__ == "__main__":

    tree = ET.parse("Bootloader.odx")

    bootloader = create_udsConnection(tree, "bootloader")

    print(bootloader.read_data_by_identifier("ECU_Serial_Number_Read"))

    pass
