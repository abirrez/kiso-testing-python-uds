#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from time import perf_counter

from uds.uds_communications.Utilities.iResettableTimer import iResettableTimer


class ResettableTimer(iResettableTimer):
    def __init__(self, timeout_time=0):

        self.__timeout_time = timeout_time
        self.__active_flag = False
        self.__expired_flag = False
        self.__start_time = None

    @property
    def timeout_time(self):
        return self.__timeout_time

    @timeout_time.setter
    def timeout_time(self, val):
        self.__timeout_time = val

    def start(self):
        self.__start_time = perf_counter()
        self.__active_flag = True
        self.__expired_flag = False

    def restart(self):
        self.start()

    def stop(self):
        self.__active_flag = False
        self.__expired_flag = False

    def is_running(self):
        self.__timer_check()
        return self.__active_flag

    def is_expired(self):
        self.__timer_check()
        return self.__expired_flag

    def __timer_check(self):
        if self.__active_flag:
            curr_time = perf_counter()
            if (curr_time - self.__start_time) > self.__timeout_time:
                self.__expired_flag = True
                self.__active_flag = False


if __name__ == "__main__":

    pass
