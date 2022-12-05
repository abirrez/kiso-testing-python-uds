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
from unittest import mock

from uds import Uds
from uds.uds_config_tool.UdsConfigTool import createUdsConnection


class ECUResetTestCase(unittest.TestCase):

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_ecu_reset_requestDflt_no_suppress(self, tp_send, tp_recv):

        tp_send.return_value = False
        tp_recv.return_value = [0x51, 0x01]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "\.\./Functional Tests/Bootloader\.odx", 
            "bootloader", 
            transport_protocol = "TEST"        
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __read_data_by_identifier to read_data_by_identifier in the uds object, so can now call below

        b = a.ecuReset("Hard Reset")  # ... calls __ecu_reset, which does the Uds.send

        tp_send.assert_called_with([0x11, 0x01], False)
        self.assertEqual({"Type": [0x01]}, b)  # ... wdbi should not return a value

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_ecu_reset_request_no_suppress(self, tp_send, tp_recv):

        tp_send.return_value = False
        tp_recv.return_value = [0x51, 0x01]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "\.\./Functional Tests/Bootloader\.odx", 
            "bootloader", 
            transport_protocol = "TEST"        
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __read_data_by_identifier to read_data_by_identifier in the uds object, so can now call below

        b = a.ecuReset(
            "Hard Reset", suppress_response=False
        )  # ... calls __ecu_reset, which does the Uds.send

        tp_send.assert_called_with([0x11, 0x01], False)
        self.assertEqual({"Type": [0x01]}, b)  # ... wdbi should not return a value

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.send")
    def test_ecuResetRequestSuppress(self, tp_send):

        tp_send.return_value = False

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "\.\./Functional Tests/Bootloader\.odx", 
            "bootloader", 
            transport_protocol = "TEST"        
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __read_data_by_identifier to read_data_by_identifier in the uds object, so can now call below

        b = a.ecuReset(
            "Hard Reset", suppress_response=True
        )  # ... calls __ecu_reset, which does the Uds.send

        tp_send.assert_called_with([0x11, 0x81], False)
        self.assertEqual(None, b)  # ... wdbi should not return a value

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_ecu_reset_neg_response_0x12(self, tp_send, tp_recv):

        tp_send.return_value = False
        tp_recv.return_value = [0x7F, 0x11, 0x12]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "\.\./Functional Tests/Bootloader\.odx", 
            "bootloader", 
            transport_protocol = "TEST"        
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __read_data_by_identifier to read_data_by_identifier in the uds object, so can now call below

        try:
            b = a.ecuReset(
                "Hard Reset"
            )  # ... calls __ecu_reset, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        tp_send.assert_called_with([0x11, 0x01], False)
        self.assertEqual(0x12, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_ecu_reset_neg_response_0x13(self, tp_send, tp_recv):

        tp_send.return_value = False
        tp_recv.return_value = [0x7F, 0x11, 0x13]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "\.\./Functional Tests/Bootloader\.odx", 
            "bootloader", 
            transport_protocol = "TEST"        
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __read_data_by_identifier to read_data_by_identifier in the uds object, so can now call below

        try:
            b = a.ecuReset(
                "Hard Reset"
            )  # ... calls __ecu_reset, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        tp_send.assert_called_with([0x11, 0x01], False)
        self.assertEqual(0x13, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_ecu_reset_neg_response_0x22(self, tp_send, tp_recv):

        tp_send.return_value = False
        tp_recv.return_value = [0x7F, 0x11, 0x22]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "\.\./Functional Tests/Bootloader\.odx", 
            "bootloader", 
            transport_protocol = "TEST"        
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __read_data_by_identifier to read_data_by_identifier in the uds object, so can now call below

        try:
            b = a.ecuReset(
                "Hard Reset"
            )  # ... calls __ecu_reset, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        tp_send.assert_called_with([0x11, 0x01], False)
        self.assertEqual(0x22, b["NRC"])


if __name__ == "__main__":
    unittest.main()
