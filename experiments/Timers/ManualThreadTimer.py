"""This file is an experiment and should not be used for any serious coding"""

from threading import Thread
from time import perf_counter

from .iTimer import ITimer


class ManualThreadTimer(ITimer):
    def __init__(self, timeout = 0):

        self.__timeout = timeout

        self.__active_flag = False
        self.__expired_flag = False

        self.__thread = None

        self.__start_time = 0

    def start(self):
        self.__thread = Thread(target = self.thread_func)
        self.__start_time = perf_counter()
        self.__thread.start()

    def restart(self):
        self.start()

    def stop(self):
        pass

    def is_expired(self):
        return self.__expired_flag

    def is_running(self):
        return self.__active_flag

    def thread_func(self):
        self.__active_flag = True
        self.__expired_flag = False
        while (perf_counter() - self.__start_time) < self.__timeout:
            pass
        self.__expired_flag = True
        self.__active_flag = False


if __name__ == "__main__":

    a = ManualThreadTimer(0.001)

    results = []
    for i in range(0, 10000):
        start_time = perf_counter()
        a.start()
        while a.is_expired() == False:
            pass
        end_time = perf_counter()
        delta = end_time - start_time
        results.append(delta)

    print("Min: {0}".format(min(results)))
    print("Max: {0}".format(max(results)))
    print("Avg: {0}".format(sum(results) / len(results)))
