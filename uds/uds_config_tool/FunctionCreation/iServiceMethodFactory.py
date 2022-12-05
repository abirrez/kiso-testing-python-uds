#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from abc import ABCMeta, abstractmethod


##
# @brief this should be static
class IServiceMethodFactory(ABCMeta):

    ##
    # @brief method to create the request function for the service element
    @staticmethod
    @abstractmethod
    def create_request_function(diag_service_element, xml_elements):
        raise NotImplementedError("create_request_function not yet implemented")

    ##
    # @brief method to create the function to check the positive response for validity
    @staticmethod
    @abstractmethod
    def create_check_positive_response_function(diag_service_element, xml_elements):
        raise NotImplementedError(
            "create_check_positive_response_function not yet implemented"
        )

    ##
    # @brief method to encode the positive response from the raw type to it physical representation
    @staticmethod
    @abstractmethod
    def create_encode_positive_response_function(diag_service_element, xml_elements):
        raise NotImplementedError(
            "create_encode_positive_response_function not yet implemented"
        )

    ##
    # @brief method to create the negative response function for the service element
    @staticmethod
    @abstractmethod
    def create_check_negative_response_function(diag_service_element, xml_elements):
        raise NotImplementedError(
            "create_check_negative_response_function not yet implemented"
        )
