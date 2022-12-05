from uds.uds_config_tool.FunctionCreation.SecurityAccessMethodFactory import (
    SecurityAccessMethodFactory,
)
from uds.uds_config_tool.UtilityFunctions import get_sdgs_data_item

if __name__ == "__main__":

    import inspect
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
            if value.attrib["SEMANTIC"] == "SECURITY":

                suppress_response = get_sdgs_data_item(value, "PositiveResponseSuppressed")
                if suppress_response == "no":
                    a = SecurityAccessMethodFactory.create_request_function(
                        value, xml_elements
                    )
                    b = SecurityAccessMethodFactory.create_check_positive_response_function(
                        value, xml_elements
                    )
                    c = SecurityAccessMethodFactory.create_check_negative_response_function(
                        value, xml_elements
                    )
                pass
