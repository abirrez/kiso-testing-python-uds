#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from abc import ABCMeta, abstractmethod


class iContainer(ABCMeta):
    @abstractmethod
    def add_request_function(self, aFunction, dictionary_entry):
        raise NotImplementedError("add_requestFucntion not implemented")

    @abstractmethod
    def add_check_function(self, aFunction, dictionary_entry):
        raise NotImplementedError("add_check_function not implemented")

    @abstractmethod
    def add_negative_response_function(self, aFunction, dictionary_entry):
        raise NotImplementedError("add_negative_response_function not implemented")

    @abstractmethod
    def add_positive_response_function(self, aFunction, dictionary_entry):
        raise NotImplementedError("add_positive_response_function not implemented")
