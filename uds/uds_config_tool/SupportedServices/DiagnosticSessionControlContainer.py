#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


defaultTPTimeout = 10  # ... (s): default to sending tester present 10s after last request (if required) - note: this includes after previous TesterPresent for repeating operation

import time
from types import MethodType

from uds.uds_config_tool.SupportedServices.iContainer import iContainer


class DiagnosticSessionControlContainer(object):
    __metaclass__ = iContainer

    def __init__(self):
        self.request_functions = {}
        self.check_functions = {}
        self.negative_response_functions = {}
        self.positive_response_functions = {}

        self.tester_present = {}
        self.current_session = None
        self.last_send = None

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.diagnosticSessionControl("session type") It does not operate
    # on this instance of the container class.
    @staticmethod
    def __diagnostic_session_control(
        target,
        parameter,
        suppress_response=False,
        tester_present=False,
        tp_timeout=defaultTPTimeout,
        **kwargs
    ):

        # Note: diagnosticSessionControl does not show support for multiple DIDs in the spec, so this is handling only a single DID with data record.
        request_function = target.diagnosticSessionControlContainer.request_functions[
            parameter
        ]
        if parameter in target.diagnosticSessionControlContainer.check_functions:
            check_function = target.diagnosticSessionControlContainer.check_functions[
                parameter
            ]
        else:
            check_function = None
        negative_response_function = (
            target.diagnosticSessionControlContainer.negative_response_functions[
                parameter
            ]
        )
        positive_response_function = (
            target.diagnosticSessionControlContainer.positive_response_functions[
                parameter
            ]
        )
        if (
            parameter
            in target.diagnosticSessionControlContainer.positive_response_functions
        ):
            positive_response_function = (
                target.diagnosticSessionControlContainer.positive_response_functions[
                    parameter
                ]
            )
        else:
            positive_response_function = None

        # Call the sequence of functions to execute the Diagnostic Session Control request/response action ...
        # ==============================================================================

        # Code additions to support interaction with tester present for a given diagnostic session ...
        target.diagnosticSessionControlContainer.current_session = parameter
        # Note: if tester_present is set, then timeout is checked every second, so timeout values less than second will always be equivalent to one second.
        target.diagnosticSessionControlContainer.tester_present[parameter] = (
            {"reqd": True, "timeout": tp_timeout}
            if tester_present
            else {"reqd": False, "timeout": None}
        )
        # Note: last_send is initialised via a call to __session_set_last_send() when send is called
        if tester_present:
            target.testerPresentThread()

        if (
            check_function is None or positive_response_function is None
        ):  # ... i.e. we only have a send_only service specified in the ODX
            suppress_response = True

        # Create the request. Note: we do not have to pre-check the dataRecord as this action is performed by
        # the recipient (the response codes 0x?? and 0x?? provide the necessary cover of errors in the request) ...
        request = request_function(suppress_response)

        if suppress_response == False:  # Send request and receive the response ...
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

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.testerPresentSessionRecord() It does not operate
    # on this instance of the container class.
    # The purpose of this method is to inform the caller of requirement for tester present messages, and if required, at what frequency (in ms)
    @staticmethod
    def __tester_present_session_record(target, **kwargs):
        session_type = target.diagnosticSessionControlContainer.current_session
        if session_type is None:
            session_type = "Default Session"
        return (
            target.diagnosticSessionControlContainer.tester_present[session_type]
            if session_type in target.diagnosticSessionControlContainer.tester_present
            else {"reqd": False, "timeout": None}
        )

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.testerPresentSessionRecord() It does not operate
    # on this instance of the container class.
    # The purpose of this method is to record the last send time (any message) for the current diagnostic session.
    @staticmethod
    def __session_set_last_send(target, **kwargs):
        target.diagnosticSessionControlContainer.last_send = int(
            round(time.time())
        )  # ... in seconds

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.testerPresentSessionRecord() It does not operate
    # on this instance of the container class.
    # The purpose of this method is to record the last send time (any message) for the current diagnostic session.
    @staticmethod
    def __tester_present_disable(target, **kwargs):
        session_type = target.diagnosticSessionControlContainer.current_session
        if session_type is None:
            session_type = "Default Session"
        target.diagnosticSessionControlContainer.tester_present[session_type] = {
            "reqd": False,
            "timeout": None,
        }
        target.diagnosticSessionControlContainer.last_send = None

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.testerPresentSessionRecord() It does not operate
    # on this instance of the container class.
    # The purpose of this method is to inform the caller of the time (in seconds) since the last message was sent for the current diagnostic session.
    @staticmethod
    def __session_time_since_last_send(target, **kwargs):
        now = int(round(time.time()))  # ... in seconds
        try:
            return now - target.diagnosticSessionControlContainer.last_send
        except:
            return 0

    def bind_function(self, bind_object):
        bind_object.diagnosticSessionControl = MethodType(
            self.__diagnostic_session_control, bind_object
        )
        # Adding an additional functions to allow internal requests to process tester_present behaviour required for the diagnostic session ...
        bind_object.testerPresentSessionRecord = MethodType(
            self.__tester_present_session_record, bind_object
        )
        bind_object.sessionSetLastSend = MethodType(
            self.__session_set_last_send, bind_object
        )
        bind_object.testerPresentDisable = MethodType(
            self.__tester_present_disable, bind_object
        )
        bind_object.sessionTimeSinceLastSend = MethodType(
            self.__session_time_since_last_send, bind_object
        )

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
