#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


import threading
import time
from types import MethodType

from uds.uds_config_tool.SupportedServices.iContainer import iContainer


class TesterPresentContainer(object):

    __metaclass__ = iContainer

    tester_present_thread_ref = None
    tester_present_targets = set()

    def __init__(self):
        self.request_functions = {}
        self.check_functions = {}
        self.negative_response_functions = {}
        self.positive_response_functions = {}

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.testerPresentContainer() It does not operate
    # on this instance of the container class.
    @staticmethod
    def __tester_present(target, suppress_response=True, disable=False, **kwargs):

        # If the disable flag is set, we do nothing but remove any tester_present behaviour for the current session
        if disable:
            target.testerPresentDisable()  # ... see diagnostic session control container
            return

        # Note: testerPresentContainer has no DID required and only supports a zeroSubFunction in order to support response suppression.
        request_function = target.testerPresentContainer.request_functions[
            "TesterPresent"
        ]
        if "TesterPresent" in target.testerPresentContainer.check_functions:
            check_function = target.testerPresentContainer.check_functions[
                "TesterPresent"
            ]
        else:
            check_function = None
        negative_response_function = (
            target.testerPresentContainer.negative_response_functions["TesterPresent"]
        )
        if "TesterPresent" in target.testerPresentContainer.positive_response_functions:
            positive_response_function = (
                target.testerPresentContainer.positive_response_functions["TesterPresent"]
            )
        else:
            positive_response_function = None

        # Call the sequence of functions to execute the Tester Present request/response action ...
        # ==============================================================================

        if check_function is None or positive_response_function is None:
            suppress_response = True

        # Create the request ...
        request = request_function(suppress_response)

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

    ##
    # @brief this method is bound to an external Uds object, referenced by target, so that it can be called
    # as one of the in-built methods. uds.testerPresentThread() It does not operate
    # on this instance of the container class.
    # Important Note: we always keep a single thread running in the background monitoring the tester_present requirements.
    # As this is static, and we can have many ECU connections via different UDS instances, this means we need to check them all!
    @staticmethod
    def __tester_present_thread(target, **kwargs):
        def __tp_worker():
            # print("work thread started (should be once only)")
            while True:
                # print("inside worker loop")
                for tgt in TesterPresentContainer.tester_present_targets:
                    try:
                        transmitting = tgt.is_transmitting()
                    except:
                        continue  # ... there's a problem with the stored target - e.g. target no longer in use, so a dead reference - so skip it
                    # ... otherwise we continue outside of the try/except block to avoid trapping any exceptions that may need to be propagated upwards
                    # print("target found")
                    if not transmitting:
                        # print("target not transmitting")
                        tp_session_record = tgt.testerPresentSessionRecord()
                        if tp_session_record[
                            "reqd"
                        ]:  # ... testPresent behaviour is required for the current diagnostic session
                            # print("tp required for target")
                            if (
                                tgt.sessionTimeSinceLastSend()
                                >= tp_session_record["timeout"]
                            ):
                                # print("timed out! - sending test present")
                                tgt.tester_present()
                if not threading.main_thread().is_alive():
                    return
                time.sleep(
                    1.0
                )  # ... check if tester present is required every 1s (we are unlikely to require finer granularity).
                # Note: I'm avoiding direct wait mechanisms (of tester_present TO) to allow for radical difference in behaviour for changing diagnostic sessions.
                # This can of course be changed.

        TesterPresentContainer.tester_present_targets.add(
            target
        )  # ... track a list of all possible concurrent targets, as we process tester present for all targets via one thread
        if TesterPresentContainer.tester_present_thread_ref is None:
            TesterPresentContainer.tester_present_thread_ref = threading.Thread(
                name="tpWorker", target=__tp_worker
            )
            TesterPresentContainer.tester_present_thread_ref.start()

    def bind_function(self, bind_object):
        bind_object.tester_present = MethodType(self.__tester_present, bind_object)
        bind_object.testerPresentThread = MethodType(
            self.__tester_present_thread, bind_object
        )

    def add_request_function(self, aFunction, dictionary_entry):
        if aFunction is not None:  # ... allow for a send only version being processed
            self.request_functions["TesterPresent"] = aFunction

    def add_check_function(self, aFunction, dictionary_entry):
        if aFunction is not None:  # ... allow for a send only version being processed
            self.check_functions["TesterPresent"] = aFunction

    def add_negative_response_function(self, aFunction, dictionary_entry):
        if aFunction is not None:  # ... allow for a send only version being processed
            self.negative_response_functions["TesterPresent"] = aFunction

    def add_positive_response_function(self, aFunction, dictionary_entry):
        if aFunction is not None:  # ... allow for a send only version being processed
            self.positive_response_functions["TesterPresent"] = aFunction
