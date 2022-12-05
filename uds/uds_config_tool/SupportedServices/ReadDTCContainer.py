#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from types import MethodType

from uds.uds_config_tool.SupportedServices.iContainer import iContainer


class ReadDTCContainer(object):

    __metaclass__ = iContainer

    def __init__(self):
        self.request_functions = {}
        self.check_functions = {}
        self.negative_response_functions = {}
        self.positive_response_functions = {}

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.readDTC("something") It does not operate
    # on this instance of the container class.
    @staticmethod
    def __read_dtc(
        target,
        subfunction,
        DTC_status_mask=None,
        DTC_mask_record=None,
        DTC_snapshot_record_number=None,
        DTC_extended_record_number=None,
        DTC_severity_mask=None,
        **kwargs
    ):
        # Note: readDTC does not show support for DIDs or multiple subfunctions in the spec, so this is handling only a single subfunction with data record.
        request_function = target.readDTCContainer.request_functions[
            "FaultMemoryRead[{0}]".format(subfunction)
        ]
        check_function = target.readDTCContainer.check_functions[
            "FaultMemoryRead[{0}]".format(subfunction)
        ]
        negative_response_function = target.readDTCContainer.negative_response_functions[
            "FaultMemoryRead[{0}]".format(subfunction)
        ]
        positive_response_function = target.readDTCContainer.positive_response_functions[
            "FaultMemoryRead[{0}]".format(subfunction)
        ]

        # Call the sequence of functions to execute the RDBI request/response action ...
        # ==============================================================================

        # Create the request ...
        DTC_status_mask = [DTC_status_mask] if DTC_status_mask is not None else []
        DTC_mask_record = DTC_mask_record if DTC_mask_record is not None else []
        DTC_snapshot_record_number = (
            [DTC_snapshot_record_number] if DTC_snapshot_record_number is not None else []
        )
        DTC_extended_record_number = (
            [DTC_extended_record_number] if DTC_extended_record_number is not None else []
        )
        DTC_severity_mask = [DTC_severity_mask] if DTC_severity_mask is not None else []
        request = request_function(
            DTC_status_mask=DTC_status_mask,
            DTC_mask_record=DTC_mask_record,
            DTC_snapshot_record_number=[],
            DTC_extended_record_number=[],
            DTC_severity_mask=[],
        )

        # Send request and receive the response ...
        response = target.send(request)  # ... this returns a single response
        nrc = negative_response_function(
            response
        )  # ... return nrc value if a negative response is received
        if nrc:
            return nrc

        # We have a positive response so check that it makes sense to us ...
        check_function(response)

        # All is still good, so return the response (currently this function does nothing, but including it here as a hook in case that changes) ...
        return positive_response_function(response)

    def bind_function(self, bind_object):
        bind_object.readDTC = MethodType(self.__read_dtc, bind_object)

    def add_request_function(self, aFunction, dictionary_entry):
        self.request_functions[dictionary_entry] = aFunction

    def add_check_function(self, aFunction, dictionary_entry):
        self.check_functions[dictionary_entry] = aFunction

    def add_negative_response_function(self, aFunction, dictionary_entry):
        self.negative_response_functions[dictionary_entry] = aFunction

    def add_positive_response_function(self, aFunction, dictionary_entry):
        self.positive_response_functions[dictionary_entry] = aFunction
