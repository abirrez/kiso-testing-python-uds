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


class WriteDataByIdentifierContainer(object):

    __metaclass__ = iContainer

    def __init__(self):
        self.request_functions = {}
        self.check_functions = {}
        self.negative_response_functions = {}
        self.positive_response_functions = {}

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.writeDataByIdentifier("something","data record") It does not operate
    # on this instance of the container class.
    @staticmethod
    def __write_data_by_identifier(target, parameter, dataRecord, **kwargs):

        # Note: WDBI does not show support for multiple DIDs in the spec, so this is handling only a single DID with data record.
        request_function = target.writeDataByIdentifierContainer.request_functions[
            parameter
        ]
        check_function = target.writeDataByIdentifierContainer.check_functions[parameter]
        negative_response_function = (
            target.writeDataByIdentifierContainer.negative_response_functions[parameter]
        )
        positive_response_function = (
            target.writeDataByIdentifierContainer.positive_response_functions[parameter]
        )

        # Call the sequence of functions to execute the RDBI request/response action ...
        # ==============================================================================

        # Create the request. Note: we do not have to pre-check the dataRecord as this action is performed by
        # the recipient (the response codes 0x13 and 0x31 provide the necessary cover of errors in the request) ...
        request = request_function(dataRecord)

        # Send request and receive the response ...
        response = target.send(request)  # ... this returns a single response
        negative_response = negative_response_function(
            response
        )  # ... return nrc value if a negative response is received
        if negative_response:
            return negative_response

        # We have a positive response so check that it makes sense to us ...
        check_function(response)

        # All is still good, so return the response (currently this function does nothing, but including it here as a hook in case that changes) ...
        return positive_response_function(response)

    def bind_function(self, bind_object):
        bind_object.writeDataByIdentifier = MethodType(
            self.__write_data_by_identifier, bind_object
        )

    def add_request_function(self, aFunction, dictionary_entry):
        self.request_functions[dictionary_entry] = aFunction

    def add_check_function(self, aFunction, dictionary_entry):
        self.check_functions[dictionary_entry] = aFunction

    def add_negative_response_function(self, aFunction, dictionary_entry):
        self.negative_response_functions[dictionary_entry] = aFunction

    def add_positive_response_function(self, aFunction, dictionary_entry):
        self.positive_response_functions[dictionary_entry] = aFunction
