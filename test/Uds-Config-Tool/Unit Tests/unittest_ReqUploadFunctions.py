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


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# NOTE: these tests cannot currently be run with the exsiting ODX, as it does not contain an upload service
# For now, I've simply run a regression of the download and transfer tests to ensure I've not broken anything.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class RequestUploadTestCase(unittest.TestCase):

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_req_upload_request(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x74, 0x20, 0x05, 0x00]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __request_upload to requestUpload in the uds object, so can now call below

        b = a.requestUpload(
            FormatIdentifier=[0x00],
            MemoryAddress=[0x40, 0x03, 0xE0, 0x00],
            MemorySize=[0x00, 0x00, 0x0E, 0x56],
        )  # ... calls __request_upload, which does the Uds.send

        canTp_send.assert_called_with(
            [0x34, 0x00, 0x44, 0x40, 0x03, 0xE0, 0x00, 0x00, 0x00, 0x0E, 0x56], False
        )
        self.assertEqual(
            {"LengthFormatIdentifier": [0x20], "MaxNumberOfBlockLength": [0x05, 0x00]},
            b,
        )  # ... (returns a dict)

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_req_upload_request02(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x74, 0x40, 0x01, 0x00, 0x05, 0x08]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"        
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __request_upload to requestUpload in the uds object, so can now call below

        b = a.requestUpload(
            FormatIdentifier=[0x00],
            MemoryAddress=[0x01, 0xFF, 0x0A, 0x80],
            MemorySize=[0x03, 0xFF],
        )  # ... calls __request_upload, which does the Uds.send

        canTp_send.assert_called_with(
            [
                0x34,
                0x00,
                0x24,
                0x01,
                0xFF,
                0x0A,
                0x80,
                0x03,
                0xFF,
            ],
            False,
        )
        self.assertEqual(
            {
                "LengthFormatIdentifier": [0x40],
                "MaxNumberOfBlockLength": [0x01, 0x00, 0x05, 0x08],
            },
            b,
        )  # ... (returns a dict)

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_req_upload_request_0x13(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x34, 0x13]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"        
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __request_upload to requestUpload in the uds object, so can now call below

        try:
            b = a.requestUpload(
                FormatIdentifier = [0x00],
                MemoryAddress = [0x40, 0x03, 0xE0, 0x00],
                MemorySize = [0x00, 0x00, 0x0E, 0x56],
            )  # ... calls __request_upload, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [0x34, 0x00, 0x44, 0x40, 0x03, 0xE0, 0x00, 0x00, 0x00, 0x0E, 0x56], False
        )
        self.assertEqual(0x13, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_wdbi_neg_response_0x31(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x34, 0x31]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"        
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __read_data_by_identifier to read_data_by_identifier in the uds object, so can now call below

        try:
            b = a.requestUpload(
                FormatIdentifier = [0x00],
                MemoryAddress = [0x40, 0x03, 0xE0, 0x00],
                MemorySize = [0x00, 0x00, 0x0E, 0x56],
            )  # ... calls __request_upload, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [0x34, 0x00, 0x44, 0x40, 0x03, 0xE0, 0x00, 0x00, 0x00, 0x0E, 0x56], False
        )
        self.assertEqual(0x31, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_wdbi_neg_response_0x33(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x34, 0x33]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"  
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __read_data_by_identifier to read_data_by_identifier in the uds object, so can now call below

        try:
            b = a.requestUpload(
                FormatIdentifier = [0x00],
                MemoryAddress = [0x40, 0x03, 0xE0, 0x00],
                MemorySize = [0x00, 0x00, 0x0E, 0x56],
            )  # ... calls __request_upload, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [0x34, 0x00, 0x44, 0x40, 0x03, 0xE0, 0x00, 0x00, 0x00, 0x0E, 0x56], False
        )
        self.assertEqual(0x33, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_wdbi_neg_response_0x70(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x34, 0x70]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"        
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __read_data_by_identifier to read_data_by_identifier in the uds object, so can now call below

        try:
            b = a.requestUpload(
                FormatIdentifier = [0x00],
                MemoryAddress = [0x40, 0x03, 0xE0, 0x00],
                MemorySize = [0x00, 0x00, 0x0E, 0x56],
            )  # ... calls __request_upload, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [0x34, 0x00, 0x44, 0x40, 0x03, 0xE0, 0x00, 0x00, 0x00, 0x0E, 0x56], False
        )
        self.assertEqual(0x70, b["NRC"])


if __name__ == "__main__":
    unittest.main()
