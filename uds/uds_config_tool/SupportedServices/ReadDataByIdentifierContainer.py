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


class read_data_by_identifierContainer(object):

    __metaclass__ = iContainer

    def __init__(self):

        # To cater for lists we may have to re-factor here - i.e. request_func can be split into requestSIDFunc and requestDIDFunc to allow building on the fly from a DID list
        # Also check_function into: checkSIDResonseFunction+SIDLengthFunction, checkResponseLengthFunction + responseLengthFunction, and an iterable checkDIDResponseFunction
        # Also positiveResponseFunc into: positiveResponseSIDFunction, and an iterable positiveResponseDIDFunction
        # Negative response function is ok as it it

        # self.request_functions = {}
        self.request_SID_functions = {}
        self.request_DID_functions = {}

        # self.check_functions = {}
        self.check_SID_response_functions = {}
        self.check_SID_length_functions = {}
        self.check_DID_response_functions = {}
        self.check_DID_length_functions = {}

        self.negative_response_functions = {}

        self.positive_response_functions = {}

    ##
    # @brief this method is bound to an external Uds object so that it call be called
    # as one of the in-built methods. uds.read_data_by_identifier("something") It does not operate
    # on this instance of the container class.
    @staticmethod
    def __read_data_by_identifier(target, parameter):
        # Some local functions to deal with use concatenation of a number of DIDs in RDBI operation ...

        # After an array of lengths has been constructed for the individual response elements, we need a simple function to check it against the response
        def check_total_response_length(input, expected_lengths_list):
            length_expected = sum(expected_lengths_list)
            if len(input) != length_expected:
                raise Exception(
                    "Total length returned not as expected. Expected: {0}; Got {1}".format(
                        length_expected, len(input)
                    )
                )

        # The check functions just want to know about the next bit of the response, so this just pops it of the front of the response
        def pop_response_element(input, expected_list):
            if expected_list == []:
                raise Exception(
                    "Total length returned not as expected. Missing elements."
                )
            return (
                input[0 : expected_list[0]],
                input[expected_list[0] :],
                expected_list[1:],
            )

        dids = parameter
        if type(dids) is not list:
            dids = [dids]

        # Adding acceptance of lists at this point, as the spec allows for multiple rdbi request to be concatenated ...
        request_SID_function = target.read_data_by_identifierContainer.request_SID_functions[
            dids[0]
        ]  # ... the SID should be the same for all DIDs, so just use the first
        request_DID_functions = [
            target.read_data_by_identifierContainer.request_DID_functions[did]
            for did in dids
        ]

        # Adding acceptance of lists at this point, as the spec allows for multiple rdbi request to be concatenated ...
        check_SID_response_function = (
            target.read_data_by_identifierContainer.check_SID_response_functions[dids[0]]
        )
        check_SID_length_function = (
            target.read_data_by_identifierContainer.check_SID_length_functions[dids[0]]
        )
        check_DID_response_functions = [
            target.read_data_by_identifierContainer.check_DID_response_functions[did]
            for did in dids
        ]
        check_DID_length_functions = [
            target.read_data_by_identifierContainer.check_DID_length_functions[did]
            for did in dids
        ]

        # This is the same for all RDBI responses, irrespective of list or single input
        negative_response_function = (
            target.read_data_by_identifierContainer.negative_response_functions[dids[0]]
        )  # ... single code irrespective of list use, so just use the first

        # Adding acceptance of lists at this point, as the spec allows for multiple rdbi request to be concatenated ...
        positive_response_functions = [
            target.read_data_by_identifierContainer.positive_response_functions[did]
            for did in dids
        ]

        # Call the sequence of functions to execute the RDBI request/response action ...
        # ==============================================================================

        # Create the request ...
        request = request_SID_function()
        for did_func in request_DID_functions:
            request += did_func()  # ... creates an array of integers

        # Send request and receive the response ...
        response = target.send(
            request
        )  # ... this returns a single response which may cover 1 or more DID response values
        negative_response = negative_response_function(
            response
        )  # ... return nrc value if a negative response is received
        if negative_response:
            return negative_response

        # We have a positive response so check that it makes sense to us ...
        sid_length = check_SID_length_function()
        expected_lengths = [sid_length]
        expected_lengths += [
            check_DID_length_functions[i]() for i in range(len(check_DID_length_functions))
        ]
        check_total_response_length(response, expected_lengths)

        # We've passed the length check, so check each element (which has to be present if the length is ok) ...
        SID_response_component, responseRemaining, lengthsRemaining = pop_response_element(
            response, expected_lengths
        )
        check_SID_response_function(SID_response_component)
        DID_responses = []
        for i in range(len(expected_lengths) - 1):
            (
                DIDResponseComponent,
                responseRemaining,
                lengthsRemaining,
            ) = pop_response_element(responseRemaining, lengthsRemaining)
            DID_responses.append(DIDResponseComponent)
            check_DID_response_functions[i](DIDResponseComponent)

        # All is still good, so return the response ...
        return_value = tuple(
            [
                positive_response_functions[i](DID_responses[i], sid_length)
                for i in range(len(DID_responses))
            ]
        )
        if len(return_value) == 1:
            return_value = return_value[
                0
            ]  # ...we only send back a tuple if there were multiple DIDs
        return return_value

    def bind_function(self, bind_object):
        bind_object.read_data_by_identifier = MethodType(
            self.__read_data_by_identifier, bind_object
        )

    ##
    # @brief method to add function to container - request_SID_function handles the SID component of the request message
    # def add_request_function(self, aFunction, dictionary_entry):
    def add_request_SID_function(self, aFunction, dictionary_entry):
        self.request_SID_functions[dictionary_entry] = aFunction

    ##
    # @brief method to add function to container - requestDIDFunction handles the 1 to N DID components of the request message
    def add_request_DID_function(self, aFunction, dictionary_entry):
        self.request_DID_functions[dictionary_entry] = aFunction

    ##
    # @brief method to add function to container - check_SID_response_function handles the checking of the returning SID details in the response message
    def add_check_SID_response_function(self, aFunction, dictionary_entry):
        self.check_SID_response_functions[dictionary_entry] = aFunction

    ##
    # @brief method to add function to container - check_SID_length_function handles return of the expected SID details length
    def add_check_SID_length_function(self, aFunction, dictionary_entry):
        self.check_SID_length_functions[dictionary_entry] = aFunction

    ##
    # @brief method to add function to container - checkDIDResponseFunction handles the checking of the returning DID details in the response message
    def add_check_DID_response_function(self, aFunction, dictionary_entry):
        self.check_DID_response_functions[dictionary_entry] = aFunction

    ##
    # @brief method to add function to container - checkDIDLengthFunction handles return of the expected DID details length
    def add_check_DID_length_function(self, aFunction, dictionary_entry):
        self.check_DID_length_functions[dictionary_entry] = aFunction

    ##
    # @brief method to add function to container - negative_response_function handles the checking of all possible negative response codes in the response message, raising the required exception
    def add_negative_response_function(self, aFunction, dictionary_entry):
        self.negative_response_functions[dictionary_entry] = aFunction

    ##
    # @brief method to add function to container - positive_response_function handles the extraction of any DID details in the response message fragment forthe DID that require return
    def add_positive_response_function(self, aFunction, dictionary_entry):
        self.positive_response_functions[dictionary_entry] = aFunction


if __name__ == "__main__":

    pass
