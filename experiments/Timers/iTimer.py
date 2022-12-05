"""This file is an experiment and should not be used for any serious coding"""

import abc


class ITimer(abc.ABC):
    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def restart(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def is_expired(self):
        pass

    @abc.abstractmethod
    def is_running(self):
        pass
