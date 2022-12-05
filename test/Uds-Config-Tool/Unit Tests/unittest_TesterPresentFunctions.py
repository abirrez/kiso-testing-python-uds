#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


import sys
import traceback
import unittest
from time import sleep
from unittest import mock

from uds import Uds
from uds.uds_config_tool.UdsConfigTool import createUdsConnection


class TesterPresentTestCase(unittest.TestCase):

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_tester_present_request_dflt_no_suppress(self, tp_send, tp_recv):

        tp_send.return_value = False
        # tp_recv.return_value = [0x7E, 0x00]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the tester_present info and attaches the __tester_present to tester_present in the uds object, so can now call below

        b = a.tester_present()  # ... calls __tester_present, which does the Uds.send

        tp_send.assert_called_with([0x3E, 0x80], False)
        self.assertEqual(None, b)  # ... tester_present should not return a value

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_tester_present_request_no_suppress(self, tp_send, tp_recv):

        tp_send.return_value = False
        tp_recv.return_value = [0x7E, 0x00]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the tester_present info and attaches the __tester_present to tester_present in the uds object, so can now call below

        b = a.tester_present(
            suppress_response = False
        )  # ... calls __tester_present, which does the Uds.send

        tp_send.assert_called_with([0x3E, 0x00], False)
        self.assertEqual({}, b)  # ... tester_present should not return a value

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.send")
    def test_tester_present_request_suppress(self, tp_send):

        tp_send.return_value = False

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the tester_present info and attaches the __tester_present to tester_present in the uds object, so can now call below

        b = a.tester_present(
            suppress_response = True
        )  # ... calls __tester_present, which does the Uds.send

        tp_send.assert_called_with([0x3E, 0x80], False)
        self.assertEqual(None, b)  # ... tester_present should not return a value

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_ecu_reset_neg_response_0x12(self, tp_send, tp_recv):

        tp_send.return_value = False
        tp_recv.return_value = [0x7F, 0x3E, 0x12]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the tester_present info and attaches the __tester_present to tester_present in the uds object, so can now call below

        try:
            b = a.tester_present(
                suppress_response = False
            )  # ... calls __tester_present, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        tp_send.assert_called_with([0x3E, 0x00], False)
        self.assertEqual(0x12, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_ecu_reset_neg_response_0x13(self, tp_send, tp_recv):

        tp_send.return_value = False
        tp_recv.return_value = [0x7F, 0x3E, 0x13]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the tester_present info and attaches the __tester_present to tester_present in the uds object, so can now call below

        try:
            b = a.tester_present(
                suppress_response = False
            )  # ... calls __tester_present, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        tp_send.assert_called_with([0x3E, 0x00], False)
        self.assertEqual(0x13, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_tester_present_not_reqd(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [
            0x50,
            0x01,
            0x00,
            0x05,
            0x00,
            0x0A,
        ]  # ... can return 1 to N bytes in the sessionParameterRecord - looking into this one

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the tester_present info and attaches the __diagnostic_session_control to diagnosticSessionControl in the uds object, so can now call below

        b = a.diagnosticSessionControl(
            "Default Session"
        )  # ... calls __diagnostic_session_control, which does the Uds.send
        canTp_send.assert_called_with([0x10, 0x01], False)
        self.assertEqual(
            {"Type": [0x01], "P3": [0x00, 0x05], "P3Ex": [0x00, 0x0A]}, b
        )  # ... diagnosticSessionControl should not return a value
        b = a.testerPresentSessionRecord()
        self.assertEqual(
            {"reqd": False, "timeout": None}, b
        )  # ... diagnosticSessionControl should not return a value

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_tester_present_reqd_dflt_TO(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [
            0x50,
            0x01,
            0x00,
            0x05,
            0x00,
            0x0A,
        ]  # ... can return 1 to N bytes in the sessionParameterRecord - looking into this one

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the tester_present info and attaches the __diagnostic_session_control to diagnosticSessionControl in the uds object, so can now call below

        b = a.diagnosticSessionControl(
            "Default Session", tester_present = True
        )  # ... calls __diagnostic_session_control, which does the Uds.send
        canTp_send.assert_called_with([0x10, 0x01], False)
        self.assertEqual(
            {"Type": [0x01], "P3": [0x00, 0x05], "P3Ex": [0x00, 0x0A]}, b
        )  # ... diagnosticSessionControl should not return a value
        b = a.testerPresentSessionRecord()
        self.assertEqual(
            {"reqd": True, "timeout": 10}, b
        )  # ... diagnosticSessionControl should not return a value

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_tester_present_reqd_updated_TO(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [
            0x50,
            0x01,
            0x00,
            0x05,
            0x00,
            0x0A,
        ]  # ... can return 1 to N bytes in the sessionParameterRecord - looking into this one

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the tester_present info and attaches the __diagnostic_session_control to diagnosticSessionControl in the uds object, so can now call below

        b = a.diagnosticSessionControl(
            "Default Session", tester_present = True, tp_timeout = 250
        )  # ... calls __diagnostic_session_control, which does the Uds.send
        canTp_send.assert_called_with([0x10, 0x01], False)
        self.assertEqual(
            {"Type": [0x01], "P3": [0x00, 0x05], "P3Ex": [0x00, 0x0A]}, b
        )  # ... diagnosticSessionControl should not return a value
        b = a.testerPresentSessionRecord()
        self.assertEqual(
            {"reqd": True, "timeout": 250}, b
        )  # ... diagnosticSessionControl should not return a value

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_tester_present_session_switching(self, canTp_send, canTp_recv):

        canTp_send.return_value = False

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the tester_present info and attaches the __diagnostic_session_control to diagnosticSessionControl in the uds object, so can now call below

        # Confirm initial default session with no tester present handling ...
        canTp_recv.return_value = [
            0x50,
            0x01,
            0x00,
            0x05,
            0x00,
            0x0A,
        ]  # ... can return 1 to N bytes in the sessionParameterRecord - looking into this one
        b = a.diagnosticSessionControl(
            "Default Session"
        )  # ... calls __diagnostic_session_control, which does the Uds.send
        canTp_send.assert_called_with([0x10, 0x01], False)
        self.assertEqual(
            {"Type": [0x01], "P3": [0x00, 0x05], "P3Ex": [0x00, 0x0A]}, b
        )  # ... diagnosticSessionControl should not return a value
        b = a.testerPresentSessionRecord()
        self.assertEqual(
            {"reqd": False, "timeout": None}, b
        )  # ... diagnosticSessionControl should not return a value

        # Create a non-default session with tester present, and confirm the case ...
        canTp_recv.return_value = [
            0x50,
            0x02,
            0x00,
            0x06,
            0x00,
            0x09,
        ]  # ... can return 1 to N bytes in the sessionParameterRecord - looking into this one
        b = a.diagnosticSessionControl(
            "Programming Session", tester_present=True
        )  # ... calls __diagnostic_session_control, which does the Uds.send
        canTp_send.assert_called_with([0x10, 0x02], False)
        self.assertEqual(
            {"Type": [0x02], "P3": [0x00, 0x06], "P3Ex": [0x00, 0x09]}, b
        )  # ... diagnosticSessionControl should not return a value
        # Check that session record for tester present is set up correctly ...
        b = a.testerPresentSessionRecord()
        self.assertEqual(
            {"reqd": True, "timeout": 10}, b
        )  # ... diagnosticSessionControl should not return a value

        # Check the time evaluation since the last message send is of the correct order ...
        t1 = a.sessionTimeSinceLastSend()
        # print(("time since last send (1)",b))
        sleep(1.0)
        t2 = a.sessionTimeSinceLastSend()
        # print(("time since last send (1)",b))
        self.assertEqual((t1 >= 0 and t1 < 0.1), True)
        self.assertEqual((t2 >= 1 and t1 < 1.1), True)
        # sleep(20.0)  # ... this was used for manual testing of "automated" tester_present sending (required the above two asserts to be commented out, and the other tests as well as they add unwanted targets to the threads target list)
        # Note: the manual test for automated repeat sending worked ok.

        # Confirm that tester present disablling operates correctly ...
        a.tester_present(disable=True)
        b = a.testerPresentSessionRecord()
        self.assertEqual(
            {"reqd": False, "timeout": None}, b
        )  # ... diagnosticSessionControl should not return a value

        # Return to the default session, and ensure that tester present handling is still off ...
        canTp_recv.return_value = [
            0x50,
            0x01,
            0x00,
            0x05,
            0x00,
            0x0A,
        ]  # ... can return 1 to N bytes in the sessionParameterRecord - looking into this one
        b = a.diagnosticSessionControl(
            "Default Session"
        )  # ... calls __diagnostic_session_control, which does the Uds.send
        canTp_send.assert_called_with([0x10, 0x01], False)
        self.assertEqual(
            {"Type": [0x01], "P3": [0x00, 0x05], "P3Ex": [0x00, 0x0A]}, b
        )  # ... diagnosticSessionControl should not return a value
        b = a.testerPresentSessionRecord()
        self.assertEqual(
            {"reqd": False, "timeout": None}, b
        )  # ... diagnosticSessionControl should not return a value


if __name__ == "__main__":
    unittest.main()
