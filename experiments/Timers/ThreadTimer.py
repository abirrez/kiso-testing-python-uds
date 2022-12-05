"""This file is an experiment and should not be used for any serious coding"""

import gc
from threading import Timer
from time import perf_counter

from .iTimer import ITimer


class ThreadTimer(ITimer):
    def __init__(self, timeout=0):

        self.__timeout = timeout

        self.__active_flag = False
        self.__expired_flag = False

        self.__timer = None

    def start(self):
        self.__active_flag = True
        self.__expired_flag = False
        self.__timer = Timer(self.__timeout, self.__timerFunc)
        self.__timer.start()

    def restart(self):
        self.start()

    def stop(self):
        if self.__timer is not None:
            if self.__timer.is_alive():
                self.__timer.cancel()

    def is_expired(self):
        return self.__expired_flag

    def is_running(self):
        return self.__active_flag

    def __timerFunc(self):
        self.__expired_flag = True
        self.__active_flag = False


if __name__ == "__main__":

    a = ThreadTimer(0.001)

    gc.disable()
    results = []

    for i in range(0, 10000):
        start_time = perf_counter()
        a.start()
        while a.is_expired() == False:
            pass
        end_time = perf_counter()
        delta = end_time - start_time
        results.append(delta)

    gc.enable()
    print("Min: {0}".format(min(results)))
    print("Max: {0}".format(max(results)))
    print("Avg: {0}".format(sum(results) / len(results)))
