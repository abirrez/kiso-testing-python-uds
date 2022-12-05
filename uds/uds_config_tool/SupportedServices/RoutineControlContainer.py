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


class RoutineControlContainer(object):

    __metaclass__ = iContainer

    def __init__(self):
        self.request_functions = {}
        self.check_functions = {}
        self.negative_response_functions = {}
        self.positive_response_functions = {}

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.routineControl("something","something else") It does not operate
    # on this instance of the container class.
    @staticmethod
    def __routine_control(
        target,
        parameter,
        control_type,
        option_record=None,
        suppress_response=False,
        **kwargs
    ):

        # Note: routineControl does not show support for multiple DIDs in the spec, so this is handling only a single DID with data record.
        request_function = target.routineControlContainer.request_functions[
            "{0}[{1}]".format(parameter, control_type)
        ]
        if (
            "{0}[{1}]".format(parameter, control_type)
            in target.routineControlContainer.check_functions
        ):
            check_function = target.routineControlContainer.check_functions[
                "{0}[{1}]".format(parameter, control_type)
            ]
        else:
            check_function = None
        negative_response_function = (
            target.routineControlContainer.negative_response_functions[
                "{0}[{1}]".format(parameter, control_type)
            ]
        )
        if (
            "{0}[{1}]".format(parameter, control_type)
            in target.routineControlContainer.positive_response_functions
        ):
            positive_response_function = (
                target.routineControlContainer.positive_response_functions[
                    "{0}[{1}]".format(parameter, control_type)
                ]
            )
        else:
            positive_response_function = None

        # Call the sequence of functions to execute the ECU Reset request/response action ...
        # ==============================================================================
        if check_function is None or positive_response_function is None:
            suppress_response = True

        # Create the request. Note: we do not have to pre-check the dataRecord as this action is performed by
        # the recipient (the response codes 0x?? and 0x?? provide the necessary cover of errors in the request) ...
        request = request_function(option_record, suppress_response)

        if suppress_response == False:
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

        # ... else ...
        # Send request and receive the response ...
        response = target.send(
            request, response_required=False
        )  # ... this suppresses any response handling (not expected)
        return

    def bind_function(self, bind_object):
        bind_object.routineControl = MethodType(self.__routine_control, bind_object)

    def add_request_function(self, aFunction, dictionary_entry):
        if aFunction is not None:  # ... allow for a send only version being processed
            self.request_functions[dictionary_entry] = aFunction

    def add_check_function(self, aFunction, dictionary_entry):
        if aFunction is not None:  # ... allow for a send only version being processed
            self.check_functions[dictionary_entry] = aFunction

    def add_negative_response_function(self, aFunction, dictionary_entry):
        if aFunction is not None:  # ... allow for a send only version being processed
            self.negative_response_functions[dictionary_entry] = aFunction

    def add_positive_response_function(self, aFunction, dictionary_entry):
        if aFunction is not None:  # ... allow for a send only version being processed
            self.positive_response_functions[dictionary_entry] = aFunction
