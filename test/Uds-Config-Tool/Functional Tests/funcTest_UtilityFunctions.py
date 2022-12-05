from uds.uds_config_tool.UtilityFunctions import (
    get_long_name,
    get_param_with_semantic,
    get_positive_response,
    get_sdgs_data,
    get_sdgs_data_item,
    get_service_id_from_diag_service,
    get_short_name,
)

if __name__ == "__main__":
    import xml.etree.ElementTree as ET

    filename = "Bootloader.odx"

    root = ET.parse(filename)

    xml_elements = {}

    for child in root.iter():
        curr_tag = child.tag
        try:
            xml_elements[child.attrib["ID"]] = child
        except KeyError:
            pass

    for key, value in xml_elements.items():
        if value.tag == "DIAG-SERVICE":
            print(value)
            short_name = get_short_name(value)
            long_name = get_long_name(value)
            sdgs_params = get_sdgs_data(value)
            print("Short Name: {0}".format(short_name))
            print("Long Name: {0}".format(long_name))
            for i, j in sdgs_params.items():
                print("{0}: {1}".format(i, j))
            print(
                "Service Id: {0:#x}".format(
                    get_service_id_from_diag_service(value, xml_elements)
                )
            )
            print(
                "DiagInstanceName: {0}".format(
                    get_sdgs_data_item(value, "DiagInstanceName")
                )
            )
            request_element = xml_elements[value.find("REQUEST-REF").attrib["ID-REF"]]
            positive_responses = get_positive_response(value, xml_elements)
            print(positive_responses)
            print("")

    pass
