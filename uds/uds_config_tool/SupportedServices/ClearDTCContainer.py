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


class ClearDTCContainer(object):

    __metaclass__ = iContainer

    def __init__(self):
        self.request_functions = {}
        self.check_functions = {}
        self.negative_response_functions = {}
        self.positive_response_functions = {}

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.clearDTC("something") It does not operate
    # on this instance of the container class.
    @staticmethod
    def __clear_DTC(target, groupOfDTC, **kwargs):

        # Note: clear DTC does not show support for multiple DIDs in the spec, so this is handling only a single DID with data record.
        request_function = target.clearDTCContainer.request_functions["FaultMemoryClear"]
        check_function = target.clearDTCContainer.check_functions["FaultMemoryClear"]
        negative_response_function = target.clearDTCContainer.negative_response_functions[
            "FaultMemoryClear"
        ]
        positive_response_function = target.clearDTCContainer.positive_response_functions[
            "FaultMemoryClear"
        ]

        # Call the sequence of functions to execute the RDBI request/response action ...
        # ==============================================================================

        # Create the request. Note: we do not have to pre-check groupOfDTC as this action is performed by
        # the recipient (the response codes 0x13 and 0x31 provide the necessary cover of errors in the request) ...
        request = request_function(groupOfDTC)

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
        bind_object.clearDTC = MethodType(self.__clear_DTC, bind_object)

    def add_request_function(self, aFunction, dictionary_entry):
        self.request_functions["FaultMemoryClear"] = aFunction

    def add_check_function(self, aFunction, dictionary_entry):
        self.check_functions["FaultMemoryClear"] = aFunction

    def add_negative_response_function(self, aFunction, dictionary_entry):
        self.negative_response_functions["FaultMemoryClear"] = aFunction

    def add_positive_response_function(self, aFunction, dictionary_entry):
        self.positive_response_functions["FaultMemoryClear"] = aFunction
