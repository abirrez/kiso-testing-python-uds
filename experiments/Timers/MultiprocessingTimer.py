"""This file is an experiment and should not be used for any serious coding"""

from multiprocessing import Process, Value
from time import perf_counter, sleep

from .iTimer import ITimer


def timer_func(active_flag, expired_flag, timeout):
    start_time = 0
    active_flag_last = False
    while 1:
        if (active_flag_last != active_flag.value) & active_flag.value:
            start_time = perf_counter()
        if active_flag.value:
            curr_time = perf_counter()
            if (curr_time - start_time) > timeout.value:
                print(curr_time - start_time)
                active_flag.value = False
                expired_flag.value = True

        active_flag_last = active_flag.value


class MultiprocessingThread(ITimer):
    def __init__(self, timeout):

        self.__start_time = Value("d", 0.00)
        self.__expired_flag = Value("B", False)
        self.__active_flag = Value("B", True)
        self.__timeout = Value("d", timeout)

        timerProcess = Process(
            target=timer_func,
            args=(self.__active_flag, self.__expired_flag, self.__timeout),
        )

        timerProcess.start()

    def start(self):
        self.__expired_flag.value = False
        self.__active_flag.value = True
        pass

    def restart(self):
        self.start()

    def stop(self):
        self.__active_flag.value = False
        self.__expired_flag.value = False

    def is_expired(self):
        return self.__expired_flag.value

    def is_running(self):
        return self.__active_flag.value


if __name__ == "__main__":

    a = MultiprocessingThread(0.001)
    sleep(0.1)

    results = []

    for i in range(0, 10000):
        start_time = perf_counter()
        a.start()
        state = a.is_expired()
        while state == False:
            state = a.is_expired()
        end_time = perf_counter()
        diff = end_time - start_time
        results.append(diff)

    print("Min: {0}".format(min(results)))
    print("Max: {0}".format(max(results)))
    print("Avg: {0}".format(sum(results) / len(results)))

    for i in range(0, len(results)):
        if results[i] < 0.001:
            print(i, results[i])

    sleep(50)
