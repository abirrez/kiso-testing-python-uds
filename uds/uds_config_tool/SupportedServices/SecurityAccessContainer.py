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


class SecurityAccessContainer(object):

    __metaclass__ = iContainer

    def __init__(self):
        self.request_functions = {}
        self.check_functions = {}
        self.negative_response_functions = {}
        self.positive_response_functions = {}

    @staticmethod
    def __security_access(target, parameter, key=None, suppress_response=False):

        request_function = target.securityAccessContainer.request_functions[parameter]
        check_negative_response_function = (
            target.securityAccessContainer.negative_response_functions[parameter]
        )
        check_positive_response_functions = (
            target.securityAccessContainer.positive_response_functions[parameter]
        )
        check_sid_function = check_positive_response_functions[0]
        check_security_access_function = check_positive_response_functions[1]
        check_data_function = check_positive_response_functions[2]

        # if the key is not none then we are sending a key back to the ECU check the key type
        if key is not None:
            # check key format
            # send request for key response
            response = target.send(
                request_function(key, suppress_response),
                response_required=not (suppress_response),
            )
        else:
            response = target.send(request_function(suppress_response))

        if suppress_response is False:
            nrc = check_negative_response_function(
                response
            )  # ... return nrc value if a negative response is received
            if nrc:
                return nrc

        if check_data_function is None:
            output = None
        else:
            check_data_function(response[2:])
            output = response[2:]

        return output

    def bind_function(self, bind_object):
        bind_object.securityAccess = MethodType(self.__security_access, bind_object)

    def add_request_function(self, aFunction, dictionary_entry):
        self.request_functions[dictionary_entry] = aFunction

    def add_check_function(self, aFunction, dictionary_entry):
        self.check_functions[dictionary_entry] = aFunction

    def add_negative_response_function(self, aFunction, dictionary_entry):
        self.negative_response_functions[dictionary_entry] = aFunction

    def add_positive_response_function(self, aFunction, dictionary_entry):
        self.positive_response_functions[dictionary_entry] = aFunction
