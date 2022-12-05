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


class TransferExitContainer(object):

    __metaclass__ = iContainer

    def __init__(self):
        self.request_functions = {}
        self.check_functions = {}
        self.negative_response_functions = {}
        self.positive_response_functions = {}

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.transferExit("something") It does not operate
    # on this instance of the container class.
    @staticmethod
    def __transfer_exit(target, transfer_request_parameter_record=None, **kwargs):

        # Note: TransferExit does not show support for multiple DIDs in the spec, so this is handling only a single DID with data record.
        request_function = target.transferExitContainer.request_functions["TransferExit"]
        check_function = target.transferExitContainer.check_functions["TransferExit"]
        negative_response_function = (
            target.transferExitContainer.negative_response_functions["TransferExit"]
        )
        positive_response_function = (
            target.transferExitContainer.positive_response_functions["TransferExit"]
        )

        # Call the sequence of functions to execute the ECU Reset request/response action ...
        # ==============================================================================

        # Create the request. Note: we do not have to pre-check the dataRecord as this action is performed by
        # the recipient (the response codes 0x?? and 0x?? provide the necessary cover of errors in the request) ...
        request = request_function(transfer_request_parameter_record)

        # Send request and receive the response ...
        response = target.send(
            request, response_required=True
        )  # ... this returns a single response
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
        bind_object.transferExit = MethodType(self.__transfer_exit, bind_object)

    def add_request_function(
        self, aFunction, dictionary_entry
    ):  # ... dictionary_entry is not used (just there for consistency in UdsConfigTool.py) - i.e. this service is effectively hardcoded
        self.request_functions["TransferExit"] = aFunction

    def add_check_function(
        self, aFunction, dictionary_entry
    ):  # ... dictionary_entry is not used (just there for consistency in UdsConfigTool.py) - i.e. this service is effectively hardcoded
        self.check_functions["TransferExit"] = aFunction

    def add_negative_response_function(
        self, aFunction, dictionary_entry
    ):  # ... dictionary_entry is not used (just there for consistency in UdsConfigTool.py) - i.e. this service is effectively hardcoded
        self.negative_response_functions["TransferExit"] = aFunction

    def add_positive_response_function(
        self, aFunction, dictionary_entry
    ):  # ... dictionary_entry is not used (just there for consistency in UdsConfigTool.py) - i.e. this service is effectively hardcoded
        self.positive_response_functions["TransferExit"] = aFunction
