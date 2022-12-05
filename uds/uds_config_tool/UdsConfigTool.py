#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


import xml.etree.ElementTree as ET

#from uds.uds_communications.Uds.Uds import Uds
from uds.uds_config_tool.FunctionCreation.ClearDTCMethodFactory import (
    ClearDTCMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.DiagnosticSessionControlMethodFactory import (
    DiagnosticSessionControlMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.ECUResetMethodFactory import (
    ECUResetMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.InputOutputControlMethodFactory import (
    InputOutputControlMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.read_data_by_identifierMethodFactory import (
    read_data_by_identifierMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.ReadDTCMethodFactory import (
    ReadDTCMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.RequestDownloadMethodFactory import (
    RequestDownloadMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.RequestUploadMethodFactory import (
    RequestUploadMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.RoutineControlMethodFactory import (
    RoutineControlMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.SecurityAccessMethodFactory import (
    SecurityAccessMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.TesterPresentMethodFactory import (
    TesterPresentMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.TransferDataMethodFactory import (
    TransferDataMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.TransferExitMethodFactory import (
    TransferExitMethodFactory,
)
from uds.uds_config_tool.FunctionCreation.WriteDataByIdentifierMethodFactory import (
    WriteDataByIdentifierMethodFactory,
)
from uds.uds_config_tool.ISOStandard.ISOStandard import (
    IsoInputOutputControlOptionRecord,
)
from uds.uds_config_tool.ISOStandard.ISOStandard import (
    IsoReadDTCStatusMask as Mask,
)
from uds.uds_config_tool.ISOStandard.ISOStandard import (
    IsoReadDTCSubfunction,
    IsoRoutineControlType,
    IsoServices,
)
from uds.uds_config_tool.SupportedServices.ClearDTCContainer import (
    ClearDTCContainer,
)
from uds.uds_config_tool.SupportedServices.DiagnosticSessionControlContainer import (
    DiagnosticSessionControlContainer,
)
from uds.uds_config_tool.SupportedServices.ECUResetContainer import (
    ECUResetContainer,
)
from uds.uds_config_tool.SupportedServices.InputOutputControlContainer import (
    InputOutputControlContainer,
)
from uds.uds_config_tool.SupportedServices.read_data_by_identifierContainer import (
    read_data_by_identifierContainer,
)
from uds.uds_config_tool.SupportedServices.ReadDTCContainer import (
    ReadDTCContainer,
)
from uds.uds_config_tool.SupportedServices.RequestDownloadContainer import (
    RequestDownloadContainer,
)
from uds.uds_config_tool.SupportedServices.RequestUploadContainer import (
    RequestUploadContainer,
)
from uds.uds_config_tool.SupportedServices.RoutineControlContainer import (
    RoutineControlContainer,
)
from uds.uds_config_tool.SupportedServices.SecurityAccessContainer import (
    SecurityAccessContainer,
)
from uds.uds_config_tool.SupportedServices.TesterPresentContainer import (
    TesterPresentContainer,
)
from uds.uds_config_tool.SupportedServices.TransferDataContainer import (
    TransferDataContainer,
)
from uds.uds_config_tool.SupportedServices.TransferExitContainer import (
    TransferExitContainer,
)
from uds.uds_config_tool.SupportedServices.WriteDataByIdentifierContainer import (
    WriteDataByIdentifierContainer,
)
from uds.uds_config_tool.UtilityFunctions import is_diag_service_transmission_only


class UdsContainerAccess:
    containers: list = []


def get_service_id_from_xml_element(diag_service_element, xml_elements):

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


def fill_dictionary(xml_element):
    temp_dictionary = {}
    for i in xml_element:
        temp_dictionary[i.attrib["ID"]] = i

    return temp_dictionary

class UdsTool:

    diagnosticSessionControlContainer = DiagnosticSessionControlContainer()
    ecuResetContainer = ECUResetContainer()
    rdbiContainer = read_data_by_identifierContainer()
    wdbiContainer = WriteDataByIdentifierContainer()
    clearDTCContainer = ClearDTCContainer()
    readDTCContainer = ReadDTCContainer()
    inputOutputControlContainer = InputOutputControlContainer()
    routineControlContainer = RoutineControlContainer()
    requestDownloadContainer = RequestDownloadContainer()
    securityAccessContainer = SecurityAccessContainer()
    requestUploadContainer = RequestUploadContainer()
    transferDataContainer = TransferDataContainer()
    transferExitContainer = TransferExitContainer()
    testerPresentContainer = TesterPresentContainer()
    sessionService_flag = False
    ecuResetService_flag = False
    rdbiService_flag = False
    wdbiService_flag = False
    securityAccess_flag = False
    clearDTCService_flag = False
    readDTCService_flag = False
    ioCtrlService_flag = False
    routineCtrlService_flag = False
    reqDownloadService_flag = False
    reqUploadService_flag = False
    transDataService_flag = False
    transExitService_flag = False
    testerPresentService_flag = False

    @classmethod
    def create_service_containers(cls, xml_file):
        root = ET.parse(xml_file)

        xml_elements = {}

        for child in root.iter():
            curr_tag = child.tag
            try:
                xml_elements[child.attrib["ID"]] = child
            except KeyError:
                pass

        for key, value in xml_elements.items():
            if value.tag == "DIAG-SERVICE":
                service_id = get_service_id_from_xml_element(value, xml_elements)
                sdg = value.find("SDGS").find("SDG")
                human_name = ""
                for sd in sdg:
                    try:
                        if sd.attrib["SI"] == "DiagInstanceName":
                            human_name = sd.text
                    except KeyError:
                        pass

                if service_id == IsoServices.DIAGNOSTIC_SESSION_CONTROL:
                    cls.sessionService_flag = True

                    request_func = (
                        DiagnosticSessionControlMethodFactory.create_request_function(
                            value, xml_elements
                        )
                    )
                    cls.diagnosticSessionControlContainer.add_request_function(
                        request_func, human_name
                    )

                    negative_response_function = DiagnosticSessionControlMethodFactory.create_check_negative_response_function(
                        value, xml_elements
                    )
                    cls.diagnosticSessionControlContainer.add_negative_response_function(
                        negative_response_function, human_name
                    )

                    check_func = DiagnosticSessionControlMethodFactory.create_check_positive_response_function(
                        value, xml_elements
                    )
                    cls.diagnosticSessionControlContainer.add_check_function(
                        check_func, human_name
                    )

                    positive_response_function = DiagnosticSessionControlMethodFactory.create_encode_positive_response_function(
                        value, xml_elements
                    )
                    cls.diagnosticSessionControlContainer.add_positive_response_function(
                        positive_response_function, human_name
                    )
                    if (
                        cls.diagnosticSessionControlContainer
                        not in UdsContainerAccess.containers
                    ):
                        UdsContainerAccess.containers.append(
                            cls.diagnosticSessionControlContainer
                        )

                elif service_id == IsoServices.ECU_RESET:
                    cls.ecuResetService_flag = True

                    request_func = ECUResetMethodFactory.create_request_function(
                        value, xml_elements
                    )
                    cls.ecuResetContainer.add_request_function(request_func, human_name)

                    negative_response_function = (
                        ECUResetMethodFactory.create_check_negative_response_function(
                            value, xml_elements
                        )
                    )
                    cls.ecuResetContainer.add_negative_response_function(
                        negative_response_function, human_name
                    )

                    try:
                        transmission_mode = value.attrib["TRANSMISSION-MODE"]
                        if transmission_mode == "SEND-ONLY":
                            sendOnly_flag = True
                    except:
                        sendOnly_flag = False

                    if sendOnly_flag:
                        check_func = None
                        positive_response_function = None
                    else:
                        check_func = (
                            ECUResetMethodFactory.create_check_positive_response_function(
                                value, xml_elements
                            )
                        )
                        positive_response_function = (
                            ECUResetMethodFactory.create_encode_positive_response_function(
                                value, xml_elements
                            )
                        )

                    cls.ecuResetContainer.add_check_function(check_func, human_name)
                    cls.ecuResetContainer.add_positive_response_function(
                        positive_response_function, human_name
                    )
                    if cls.ecuResetContainer not in UdsContainerAccess.containers:
                        UdsContainerAccess.containers.append(cls.ecuResetContainer)
                    pass

                elif service_id == IsoServices.READ_DATA_BY_IDENTIFIER:
                    cls.rdbiService_flag = True

                    # The new code extends the range of functions required, in order to handle RDBI working for concatenated lists of DIDs ...
                    request_functions = (
                        read_data_by_identifierMethodFactory.create_requestFunctions(
                            value, xml_elements
                        )
                    )
                    cls.rdbiContainer.add_request_SID_function(
                        request_functions[0], human_name
                    )  # ... note: this will now need to handle replication of this one!!!!
                    cls.rdbiContainer.add_request_DID_function(request_functions[1], human_name)

                    negative_response_function = read_data_by_identifierMethodFactory.create_check_negative_response_function(
                        value, xml_elements
                    )
                    cls.rdbiContainer.add_negative_response_function(
                        negative_response_function, human_name
                    )

                    check_functions = read_data_by_identifierMethodFactory.create_checkPositiveResponseFunctions(
                        value, xml_elements
                    )
                    cls.rdbiContainer.add_check_SID_response_function(check_functions[0], human_name)
                    cls.rdbiContainer.add_check_SID_length_function(check_functions[1], human_name)
                    cls.rdbiContainer.add_check_DID_response_function(check_functions[2], human_name)
                    cls.rdbiContainer.add_check_DID_length_function(check_functions[3], human_name)

                    positive_response_function = read_data_by_identifierMethodFactory.create_encode_positive_response_function(
                        value, xml_elements
                    )
                    cls.rdbiContainer.add_positive_response_function(
                        positive_response_function, human_name
                    )

                    if cls.rdbiContainer not in UdsContainerAccess.containers:
                        UdsContainerAccess.containers.append(cls.rdbiContainer)

                elif service_id == IsoServices.SECURITY_ACCESS:
                    if is_diag_service_transmission_only(value) == False:
                        request_function = (
                            SecurityAccessMethodFactory.create_request_function(
                                value, xml_elements
                            )
                        )
                        cls.securityAccessContainer.add_request_function(
                            request_function, human_name
                        )

                        negative_response_function = SecurityAccessMethodFactory.create_check_negative_response_function(
                            value, xml_elements
                        )
                        cls.securityAccessContainer.add_negative_response_function(
                            negative_response_function, human_name
                        )

                        check_function = SecurityAccessMethodFactory.create_check_positive_response_function(
                            value, xml_elements
                        )
                        cls.securityAccessContainer.add_positive_response_function(
                            check_function, human_name
                        )

                        cls.securityAccess_flag = True

                        if cls.securityAccessContainer not in UdsContainerAccess.containers:
                            UdsContainerAccess.containers.append(cls.securityAccessContainer)

                elif service_id == IsoServices.WRITE_DATA_BY_IDENTIFIER:

                    cls.wdbiService_flag = True
                    request_func = WriteDataByIdentifierMethodFactory.create_request_function(
                        value, xml_elements
                    )
                    cls.wdbiContainer.add_request_function(request_func, human_name)

                    negative_response_function = WriteDataByIdentifierMethodFactory.create_check_negative_response_function(
                        value, xml_elements
                    )
                    cls.wdbiContainer.add_negative_response_function(
                        negative_response_function, human_name
                    )

                    check_func = WriteDataByIdentifierMethodFactory.create_check_positive_response_function(
                        value, xml_elements
                    )
                    cls.wdbiContainer.add_check_function(check_func, human_name)

                    positive_response_function = WriteDataByIdentifierMethodFactory.create_encode_positive_response_function(
                        value, xml_elements
                    )
                    cls.wdbiContainer.add_positive_response_function(
                        positive_response_function, human_name
                    )

                    if cls.wdbiContainer not in UdsContainerAccess.containers:
                        UdsContainerAccess.containers.append(cls.wdbiContainer)

                elif service_id == IsoServices.CLEAR_DIAGNOSTIC_INFORMATION:
                    cls.clearDTCService_flag = True
                    request_func = ClearDTCMethodFactory.create_request_function(
                        value, xml_elements
                    )
                    cls.clearDTCContainer.add_request_function(request_func, human_name)

                    negative_response_function = (
                        ClearDTCMethodFactory.create_check_negative_response_function(
                            value, xml_elements
                        )
                    )
                    cls.clearDTCContainer.add_negative_response_function(
                        negative_response_function, human_name
                    )

                    check_func = ClearDTCMethodFactory.create_check_positive_response_function(
                        value, xml_elements
                    )
                    cls.clearDTCContainer.add_check_function(check_func, human_name)

                    positive_response_function = (
                        ClearDTCMethodFactory.create_encode_positive_response_function(
                            value, xml_elements
                        )
                    )
                    cls.clearDTCContainer.add_positive_response_function(
                        positive_response_function, human_name
                    )

                    if cls.clearDTCContainer not in UdsContainerAccess.containers:
                        UdsContainerAccess.containers.append(cls.clearDTCContainer)

                elif service_id == IsoServices.READ_DTC_INFORMATION:
                    cls.readDTCService_flag = True
                    (
                        request_function,
                        qualifier,
                    ) = ReadDTCMethodFactory.create_request_function(value, xml_elements)
                    if qualifier != "":
                        cls.readDTCContainer.add_request_function(
                            request_function, "FaultMemoryRead" + qualifier
                        )

                        negative_response_function = (
                            ReadDTCMethodFactory.create_check_negative_response_function(
                                value, xml_elements
                            )
                        )
                        cls.readDTCContainer.add_negative_response_function(
                            negative_response_function, "FaultMemoryRead" + qualifier
                        )

                        check_function = (
                            ReadDTCMethodFactory.create_check_positive_response_function(
                                value, xml_elements
                            )
                        )
                        cls.readDTCContainer.add_check_function(
                            check_function, "FaultMemoryRead" + qualifier
                        )

                        positive_response_function = (
                            ReadDTCMethodFactory.create_encode_positive_response_function(
                                value, xml_elements
                            )
                        )
                        cls.readDTCContainer.add_positive_response_function(
                            positive_response_function, "FaultMemoryRead" + qualifier
                        )

                        if cls.readDTCContainer not in UdsContainerAccess.containers:
                            UdsContainerAccess.containers.append(cls.readDTCContainer)

                elif service_id == IsoServices.INPUT_OUTPUT_CONTROL_BY_IDENTIFIER:
                    cls.ioCtrlService_flag = True
                    (
                        request_func,
                        qualifier,
                    ) = InputOutputControlMethodFactory.create_request_function(
                        value, xml_elements
                    )
                    if qualifier != "":
                        cls.inputOutputControlContainer.add_request_function(
                            request_func, human_name + qualifier
                        )

                        negative_response_function = InputOutputControlMethodFactory.create_check_negative_response_function(
                            value, xml_elements
                        )
                        cls.inputOutputControlContainer.add_negative_response_function(
                            negative_response_function, human_name + qualifier
                        )

                        check_func = InputOutputControlMethodFactory.create_check_positive_response_function(
                            value, xml_elements
                        )
                        cls.inputOutputControlContainer.add_check_function(
                            check_func, human_name + qualifier
                        )

                        positive_response_function = InputOutputControlMethodFactory.create_encode_positive_response_function(
                            value, xml_elements
                        )
                        cls.inputOutputControlContainer.add_positive_response_function(
                            positive_response_function, human_name + qualifier
                        )

                        if cls.inputOutputControlContainer not in UdsContainerAccess.containers:
                            UdsContainerAccess.containers.append(
                                cls.inputOutputControlContainer
                            )

                elif service_id == IsoServices.ROUTINE_CONTROL:
                    cls.routineCtrlService_flag = True
                    # We need a qualifier, as the human name for the start stop, and results calls are all the same, so they otherwise overwrite each other
                    (
                        request_func,
                        qualifier,
                    ) = RoutineControlMethodFactory.create_request_function(
                        value, xml_elements
                    )
                    if qualifier != "":
                        cls.routineControlContainer.add_request_function(
                            request_func, human_name + qualifier
                        )

                        negative_response_function = RoutineControlMethodFactory.create_check_negative_response_function(
                            value, xml_elements
                        )
                        cls.routineControlContainer.add_negative_response_function(
                            negative_response_function, human_name + qualifier
                        )

                        check_func = RoutineControlMethodFactory.create_check_positive_response_function(
                            value, xml_elements
                        )
                        cls.routineControlContainer.add_check_function(
                            check_func, human_name + qualifier
                        )

                        positive_response_function = RoutineControlMethodFactory.create_encode_positive_response_function(
                            value, xml_elements
                        )
                        cls.routineControlContainer.add_positive_response_function(
                            positive_response_function, human_name + qualifier
                        )

                        if cls.routineControlContainer not in UdsContainerAccess.containers:
                            UdsContainerAccess.containers.append(cls.routineControlContainer)

                elif service_id == IsoServices.REQUEST_DOWNLOAD:
                    cls.reqDownloadService_flag = True
                    request_func = RequestDownloadMethodFactory.create_request_function(
                        value, xml_elements
                    )
                    cls.requestDownloadContainer.add_request_function(request_func, human_name)

                    negative_response_function = (
                        RequestDownloadMethodFactory.create_check_negative_response_function(
                            value, xml_elements
                        )
                    )
                    cls.requestDownloadContainer.add_negative_response_function(
                        negative_response_function, human_name
                    )

                    check_func = (
                        RequestDownloadMethodFactory.create_check_positive_response_function(
                            value, xml_elements
                        )
                    )
                    cls.requestDownloadContainer.add_check_function(check_func, human_name)

                    positive_response_function = (
                        RequestDownloadMethodFactory.create_encode_positive_response_function(
                            value, xml_elements
                        )
                    )
                    cls.requestDownloadContainer.add_positive_response_function(
                        positive_response_function, human_name
                    )

                    if cls.requestDownloadContainer not in UdsContainerAccess.containers:
                        UdsContainerAccess.containers.append(cls.requestDownloadContainer)

                elif service_id == IsoServices.REQUEST_UPLOAD:
                    cls.reqUploadService_flag = True
                    request_func = RequestUploadMethodFactory.create_request_function(
                        value, xml_elements
                    )
                    cls.requestUploadContainer.add_request_function(request_func, human_name)

                    negative_response_function = (
                        RequestUploadMethodFactory.create_check_negative_response_function(
                            value, xml_elements
                        )
                    )
                    cls.requestUploadContainer.add_negative_response_function(
                        negative_response_function, human_name
                    )

                    check_func = (
                        RequestUploadMethodFactory.create_check_positive_response_function(
                            value, xml_elements
                        )
                    )
                    cls.requestUploadContainer.add_check_function(check_func, human_name)

                    positive_response_function = (
                        RequestUploadMethodFactory.create_encode_positive_response_function(
                            value, xml_elements
                        )
                    )
                    cls.requestUploadContainer.add_positive_response_function(
                        positive_response_function, human_name
                    )

                    if cls.requestUploadContainer not in UdsContainerAccess.containers:
                        UdsContainerAccess.containers.append(cls.requestUploadContainer)

                elif service_id == IsoServices.TRANSFER_DATA:
                    cls.transDataService_flag = True
                    request_func = TransferDataMethodFactory.create_request_function(
                        value, xml_elements
                    )
                    cls.transferDataContainer.add_request_function(request_func, human_name)

                    negative_response_function = (
                        TransferDataMethodFactory.create_check_negative_response_function(
                            value, xml_elements
                        )
                    )
                    cls.transferDataContainer.add_negative_response_function(
                        negative_response_function, human_name
                    )

                    check_func = (
                        TransferDataMethodFactory.create_check_positive_response_function(
                            value, xml_elements
                        )
                    )
                    cls.transferDataContainer.add_check_function(check_func, human_name)

                    positive_response_function = (
                        TransferDataMethodFactory.create_encode_positive_response_function(
                            value, xml_elements
                        )
                    )
                    cls.transferDataContainer.add_positive_response_function(
                        positive_response_function, human_name
                    )

                    if cls.transferDataContainer not in UdsContainerAccess.containers:
                        UdsContainerAccess.containers.append(cls.transferDataContainer)

                elif service_id == IsoServices.REQUEST_TRANSFER_EXIT:
                    cls.transExitService_flag = True
                    request_func = TransferExitMethodFactory.create_request_function(
                        value, xml_elements
                    )
                    cls.transferExitContainer.add_request_function(request_func, human_name)

                    negative_response_function = (
                        TransferExitMethodFactory.create_check_negative_response_function(
                            value, xml_elements
                        )
                    )
                    cls.transferExitContainer.add_negative_response_function(
                        negative_response_function, human_name
                    )

                    check_func = (
                        TransferExitMethodFactory.create_check_positive_response_function(
                            value, xml_elements
                        )
                    )
                    cls.transferExitContainer.add_check_function(check_func, human_name)

                    positive_response_function = (
                        TransferExitMethodFactory.create_encode_positive_response_function(
                            value, xml_elements
                        )
                    )
                    cls.transferExitContainer.add_positive_response_function(
                        positive_response_function, human_name
                    )

                    if cls.transferExitContainer not in UdsContainerAccess.containers:
                        UdsContainerAccess.containers.append(cls.transferExitContainer)

                elif service_id == IsoServices.TESTER_PRESENT:
                    # Note: Tester Present is presented here as an exposed service, but it will typically not be called directly, as we'll hook it
                    # in to keep the session alive automatically if requested (details to come, but this is just getting the comms into place).
                    cls.testerPresentService_flag = True
                    request_func = TesterPresentMethodFactory.create_request_function(
                        value, xml_elements
                    )
                    cls.testerPresentContainer.add_request_function(request_func, "TesterPresent")

                    negative_response_function = (
                        TesterPresentMethodFactory.create_check_negative_response_function(
                            value, xml_elements
                        )
                    )
                    cls.testerPresentContainer.add_negative_response_function(
                        negative_response_function, "TesterPresent"
                    )

                    check_func = (
                        TesterPresentMethodFactory.create_check_positive_response_function(
                            value, xml_elements
                        )
                    )
                    cls.testerPresentContainer.add_check_function(check_func, "TesterPresent")

                    positive_response_function = (
                        TesterPresentMethodFactory.create_encode_positive_response_function(
                            value, xml_elements
                        )
                    )
                    cls.testerPresentContainer.add_positive_response_function(
                        positive_response_function, "TesterPresent"
                    )

                    if cls.testerPresentContainer not in UdsContainerAccess.containers:
                        UdsContainerAccess.containers.append(cls.testerPresentContainer)



    @classmethod
    def bind_containers(cls, uds_instance)-> None:
        # Bind any ECU Reset services that have been found
        if cls.sessionService_flag:
            setattr(
                uds_instance,
                "diagnosticSessionControlContainer",
                cls.diagnosticSessionControlContainer,
            )
            cls.diagnosticSessionControlContainer.bind_function(uds_instance)

        # Bind any ECU Reset services that have been found
        if cls.ecuResetService_flag:
            setattr(uds_instance, "ecuResetContainer", cls.ecuResetContainer)
            cls.ecuResetContainer.bind_function(uds_instance)

        # Bind any rdbi services that have been found
        if cls.rdbiService_flag:
            setattr(uds_instance, "read_data_by_identifierContainer", cls.rdbiContainer)
            cls.rdbiContainer.bind_function(uds_instance)

        # Bind any security access services have been found
        if cls.securityAccess_flag:
            setattr(uds_instance, "securityAccessContainer", cls.securityAccessContainer)
            cls.securityAccessContainer.bind_function(uds_instance)

        # Bind any wdbi services have been found
        if cls.wdbiService_flag:
            setattr(uds_instance, "writeDataByIdentifierContainer", cls.wdbiContainer)
            cls.wdbiContainer.bind_function(uds_instance)

        # Bind any clear DTC services that have been found
        if cls.clearDTCService_flag:
            setattr(uds_instance, "clearDTCContainer", cls.clearDTCContainer)
            cls.clearDTCContainer.bind_function(uds_instance)

        # Bind any read DTC services that have been found
        if cls.readDTCService_flag:
            setattr(uds_instance, "readDTCContainer", cls.readDTCContainer)
            cls.readDTCContainer.bind_function(uds_instance)

        # Bind any input output control services that have been found
        if cls.ioCtrlService_flag:
            setattr(uds_instance, "inputOutputControlContainer", cls.inputOutputControlContainer)
            cls.inputOutputControlContainer.bind_function(uds_instance)

        # Bind any routine control services that have been found
        if cls.routineCtrlService_flag:
            setattr(uds_instance, "routineControlContainer", cls.routineControlContainer)
            cls.routineControlContainer.bind_function(uds_instance)

        # Bind any request download services that have been found
        if cls.reqDownloadService_flag:
            setattr(uds_instance, "requestDownloadContainer", cls.requestDownloadContainer)
            cls.requestDownloadContainer.bind_function(uds_instance)

        # Bind any request upload services that have been found
        if cls.reqUploadService_flag:
            setattr(uds_instance, "requestUploadContainer", cls.requestUploadContainer)
            cls.requestUploadContainer.bind_function(uds_instance)

        # Bind any transfer data services that have been found
        if cls.transDataService_flag:
            setattr(uds_instance, "transferDataContainer", cls.transferDataContainer)
            cls.transferDataContainer.bind_function(uds_instance)

        # Bind any transfer exit data services that have been found
        if cls.transExitService_flag:
            setattr(uds_instance, "transferExitContainer", cls.transferExitContainer)
            cls.transferExitContainer.bind_function(uds_instance)

        # Bind any tester present services that have been found
        if cls.testerPresentService_flag:
            setattr(uds_instance, "testerPresentContainer", cls.testerPresentContainer)
            cls.testerPresentContainer.bind_function(uds_instance)
