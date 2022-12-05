#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


import unittest
from time import perf_counter, sleep

from uds import ResettableTimer


class CanTpMessageTestCase(unittest.TestCase):

    ##
    # @brief tests the initialisation transition
    def test_state_when_initialised(self):
        a = ResettableTimer(0.6)
        self.assertEqual(False, a.is_running())
        self.assertEqual(False, a.is_expired())

    ##
    # @brief tests the state after starting
    def test_state_after_start(self):
        a = ResettableTimer(0.2)
        a.start()
        self.assertEqual(True, a.is_running())
        self.assertEqual(False, a.is_expired())

    ##
    # @brief tests state after timeout
    def test_state_after_timeout_time(self):
        a = ResettableTimer(0.2)
        a.start()
        sleep(0.25)
        self.assertEqual(False, a.is_running())
        self.assertEqual(True, a.is_expired())

    ##
    # @brief tests state after reset
    def test_state_after_restart(self):
        a = ResettableTimer(0.4)
        a.start()
        sleep(0.3)
        a.restart()
        sleep(0.2)
        self.assertEqual(True, a.is_running())
        self.assertEqual(False, a.is_expired())

    ##
    # @brief tests state for restart while running
    def test_state_after_restart_and_expiry(self):
        a = ResettableTimer(0.4)
        a.start()
        sleep(0.3)
        self.assertEqual(False, a.is_expired())
        self.assertEqual(True, a.is_running())
        a.restart()
        sleep(0.45)
        self.assertEqual(True, a.is_expired())
        self.assertEqual(False, a.is_running())

    ##
    # @brief tests state for restart after expiry
    def test_state_after_expired_then_restart(self):
        a = ResettableTimer(0.4)
        a.start()
        sleep(0.45)
        self.assertEqual(False, a.is_running())
        self.assertEqual(True, a.is_expired())
        a.restart()
        self.assertEqual(True, a.is_running())
        self.assertEqual(False, a.is_expired())

    ##
    # @brief tests state after a stop
    def test_stop_after_start(self):
        a = ResettableTimer(0.4)
        a.start()
        self.assertEqual(True, a.is_running())
        self.assertEqual(False, a.is_expired())
        a.stop()
        self.assertEqual(False, a.is_running())
        self.assertEqual(False, a.is_expired())

    ##
    # @brief tests state with a 0 timeout
    def test_is_expired_with0_time(self):
        a = ResettableTimer(0)
        a.start()
        self.assertEqual(False, a.is_running())
        self.assertEqual(True, a.is_expired())

    ##
    # @brief tests the accuracy of the timer
    def test_timer_accuracy(self):
        testTimes = [1, 0.3, 0.2, 0.1, 0.01, 0.01]
        for i in testTimes:
            a = ResettableTimer(i)
            start_time = perf_counter()
            a.start()
            while a.is_running():
                pass
            end_time = perf_counter()
            delta = end_time - start_time
            self.assertAlmostEqual(delta, i, delta = 0.001)


if __name__ == "__main__":
    unittest.main()
