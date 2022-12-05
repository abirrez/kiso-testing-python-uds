#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from abc import ABCMeta, abstractmethod


class iResettableTimer:
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def timeout_time(self):
        raise NotImplementedError("class has not implemented this method")

    @timeout_time.setter
    @abstractmethod
    def timeout_time(self, val):
        raise NotImplementedError("class has not implemented this method")

    @abstractmethod
    def start(self):
        raise NotImplementedError("class has not implemented this method")

    @abstractmethod
    def restart(self):
        raise NotImplementedError("class has not implemented this method")

    @abstractmethod
    def stop(self):
        raise NotImplementedError("class has not implemented this method")

    @abstractmethod
    def is_running(self):
        raise NotImplementedError("class has not implemented this method")

    @abstractmethod
    def is_expired(self):
        raise NotImplementedError("class has not implemented this method")
