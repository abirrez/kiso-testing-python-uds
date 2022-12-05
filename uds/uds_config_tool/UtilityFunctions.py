##
# param: a diag service element
# return: a dictionary with the sdgs data elements
def get_sdgs_data(diag_service_element):

    output = {}

    sdgs = diag_service_element.find("SDGS")
    sdg = sdgs.find("SDG")
    for i in sdg:
        try:
            output[i.attrib["SI"]] = i.text
        except:
            pass
    return output


##
# param: a diag_service_element, an string representing the si attribute
# return: a specific entry from the sdgs params, or none if it does not exist
def get_sdgs_data_item(diag_service_element, itemName):

    output_dict = get_sdgs_data(diag_service_element)

    try:
        output = output_dict[itemName]
    except:
        output = None

    return output


##
# param: an xml element
# return: a string with the short name, or None if no short name exists
def get_short_name(xml_element):

    try:
        output = xml_element.find("SHORT-NAME").text
    except:
        output = None

    return output


##
# param: an xml element
# return: a string with the long name, or None if no long name exists
def get_long_name(xml_element):
    try:
        output = xml_element.find("LONG-NAME").text
    except:
        output = None

    return output


##
# param: a diag service element, a list of other xml_elements
# return: an integer
def get_service_id_from_diag_service(diag_service_element, xml_elements):

    request_key = diag_service_element.find("REQUEST-REF").attrib["ID-REF"]
    request_element = xml_elements[request_key]
    params = request_element.find("PARAMS")
    for i in params:
        try:
            if i.attrib["SEMANTIC"] == "SERVICE-ID":
                return int(i.find("CODED-VALUE").text)
        except:
            pass

    return None


##
# param: a diag service element, a list of other xml_elements
# return: an integer
def get_response_id_from_diag_service(diag_service_element, xml_elements):

    request_key = diag_service_element.find("REQUEST-REF").attrib["ID-REF"]
    request_element = xml_elements[request_key]
    params = request_element.find("PARAMS")
    for i in params:
        try:
            if i.attrib["SEMANTIC"] == "SERVICE-ID":
                return int(i.find("CODED-VALUE").text)
        except:
            pass

    return None


##
# params: an xml_element, the name of a semantic to match
# return: a single parameter matching the semantic, or a list of parameters which match the semantic
def get_param_with_semantic(xml_element, semanticName):

    output = None

    try:
        params = xml_element.find("PARAMS")
    except AttributeError:
        return output

    params_list = []

    for i in params:
        param_semantic = i.attrib["SEMANTIC"]
        if param_semantic == semanticName:
            params_list.append(i)

    if len(params_list) == 0:
        output = None
    elif len(params_list) == 1:
        output = params_list[0]
    else:
        output = params_list
    return output


##
# params: a diagnostic service element xml entry, and the dictionary of all possible xml elements
# return: if only 1 element, then a single xml element, else a list of xml elements, or none if no positive responses
def get_positive_response(diag_service_element, xml_elements):

    positive_response_list = []
    try:
        positive_response_references = diag_service_element.find("POS-RESPONSE-REFS")
    except:
        return None

    if positive_response_references is None:
        return None
    else:
        for i in positive_response_references:
            try:
                positive_response_list.append(xml_elements[i.attrib["ID-REF"]])
            except:
                pass

    positive_response_list_length = len(positive_response_list)
    if positive_response_list_length == 0:
        return None
    if positive_response_list_length:
        return positive_response_list[0]
    else:
        return positive_response_list


def get_diag_object_prop(param_element, xml_elements):

    try:
        dop_element = xml_elements[param_element.find("DOP-REF").attrib["ID-REF"]]
    except:
        dop_element = None

    return dop_element


def get_bit_length_from_dop(diag_object_prop_element):

    try:
        bit_length = int(
            diag_object_prop_element.find("DIAG-CODED-TYPE").find("BIT-LENGTH").text
        )
    except:
        bit_length = None

    return bit_length


def is_diag_service_transmission_only(diag_service_element):

    output = get_sdgs_data_item(diag_service_element, "PositiveResponseSuppressed")

    if output is not None:
        if output == "yes":
            return True

    return False


if __name__ == "__main__":

    pass
