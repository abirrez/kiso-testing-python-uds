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
from uds.uds_config_tool.IHexFunctions import ihex_file
from uds.uds_config_tool.UdsConfigTool import createUdsConnection


class TransferDataTestCase(unittest.TestCase):

    """Note: this has been run with a modified Uds.py transfer_ihex_file() function to skip the reqDownload and transExit (I couldn't figure out how to mock these here)
    # patches are inserted in reverse order
    @mock.patch('uds.TestTp.recv')
    @mock.patch('uds.TestTp.send')
    def test_transDataRequest_ihex(self,
                     canTp_send,
                     canTp_recv,
                     reqDownload,
                     transExit):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x76, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection('../Functional Tests/Bootloader.odx', 'bootloader', transport_protocol="TEST")
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        b = a.transfer_file("./unitTest01.hex",1280)	# ... calls __transfer_data, which does the Uds.send - takes block_sequence_counter and parameterRecord

        canTp_send.assert_called_with([0x36, 0x01, 0x00, 0x08, 0x00, 0x70, 0x00, 0x09, 0x4E, 0x80, 0x45, 0x34, 0x30, 0x30, 0x2D, 0x55, 0x44, 0x53],False)
        self.assertEqual({'block_sequence_counter':[0x01],'transferResponseParameterRecord':[0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]}, b)  # ... (returns a dict)
    """

    """ REMOVING THIS TEST AS "block" list is no longer exposed this way ...
    # patches are inserted in reverse order
    @mock.patch('uds.TestTp.recv')
    @mock.patch('uds.TestTp.send')
    def test_transDataRequest_ihex01(self,
                     canTp_send,
                     canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x76, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]

        app_blocks = ihex_file("./unitTest01.hex")
        app_blocks.transmit_chunksize = 1280

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection('../Functional Tests/Bootloader.odx', 'bootloader', transport_protocol="TEST")
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        b = a.transfer_data(transfer_block=app_blocks.block[0])	# ... calls __transfer_data, which does the Uds.send - takes block_sequence_counter and parameterRecord
	
        canTp_send.assert_called_with([0x36, 0x01, 0x00, 0x08, 0x00, 0x70, 0x00, 0x09, 0x4E, 0x80, 0x45, 0x34, 0x30, 0x30, 0x2D, 0x55, 0x44, 0x53],False)
        self.assertEqual({'block_sequence_counter':[0x01],'transferResponseParameterRecord':[0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]}, b)  # ... (returns a dict)
    """

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_request_ihex02(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x76, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]

        app_blocks = ihex_file("./unitTest01.hex")
        app_blocks.transmit_chunksize = 1280

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", "bootloader", transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        b = a.transfer_data(
            transfer_blocks=app_blocks
        )  # ... calls __transfer_data, which does the Uds.send - takes block_sequence_counter and parameterRecord

        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0x00,
                0x08,
                0x00,
                0x70,
                0x00,
                0x09,
                0x4E,
                0x80,
                0x45,
                0x34,
                0x30,
                0x30,
                0x2D,
                0x55,
                0x44,
                0x53,
            ],
            False,
        )
        self.assertEqual(
            {
                "block_sequence_counter": [0x01],
                "transferResponseParameterRecord": [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF],
            },
            b,
        )  # ... (returns a dict)

    """ REMOVING THIS TEST AS "block" list is no longer exposed this way ...
    # patches are inserted in reverse order
    @mock.patch('uds.TestTp.recv')
    @mock.patch('uds.TestTp.send')
    def test_transDataRequest_ihex03(self,
                     canTp_send,
                     canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x76, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection('../Functional Tests/Bootloader.odx', 'bootloader',ihex_file="./unitTest01.hex")
        a.ihex_file.transmit_chunksize = 1280
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        b = a.transfer_data(transfer_block=a.ihex_file.block[0])	# ... calls __transfer_data, which does the Uds.send - takes block_sequence_counter and parameterRecord
	
        canTp_send.assert_called_with([0x36, 0x01, 0x00, 0x08, 0x00, 0x70, 0x00, 0x09, 0x4E, 0x80, 0x45, 0x34, 0x30, 0x30, 0x2D, 0x55, 0x44, 0x53],False)
        self.assertEqual({'block_sequence_counter':[0x01],'transferResponseParameterRecord':[0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]}, b)  # ... (returns a dict)
    """

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_request_ihex04(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x76, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx",
            "bootloader",
            ihex_file="./unitTest01.hex",
            transport_protocol = "TEST",
        )
        a.ihex_file.transmit_chunksize = 1280
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        b = a.transfer_data(
            transfer_blocks=a.ihex_file
        )  # ... calls __transfer_data, which does the Uds.send - takes block_sequence_counter and parameterRecord

        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0x00,
                0x08,
                0x00,
                0x70,
                0x00,
                0x09,
                0x4E,
                0x80,
                0x45,
                0x34,
                0x30,
                0x30,
                0x2D,
                0x55,
                0x44,
                0x53,
            ],
            False,
        )
        self.assertEqual(
            {
                "block_sequence_counter": [0x01],
                "transferResponseParameterRecord": [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF],
            },
            b,
        )  # ... (returns a dict)

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_request_ihex05(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x76, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        a.ihex_file = "./unitTest01.hex"
        a.ihex_file.transmit_chunksize = 1280
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        b = a.transfer_data(
            transfer_blocks = a.ihex_file
        )  # ... calls __transfer_data, which does the Uds.send - takes block_sequence_counter and parameterRecord

        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0x00,
                0x08,
                0x00,
                0x70,
                0x00,
                0x09,
                0x4E,
                0x80,
                0x45,
                0x34,
                0x30,
                0x30,
                0x2D,
                0x55,
                0x44,
                0x53,
            ],
            False,
        )
        self.assertEqual(
            {
                "block_sequence_counter": [0x01],
                "transferResponseParameterRecord": [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF],
            },
            b,
        )  # ... (returns a dict)

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_request(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x76, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        b = a.transfer_data(
            0x01,
            [
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
        )  # ... calls __transfer_data, which does the Uds.send - takes block_sequence_counter and parameterRecord

        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
            False,
        )
        self.assertEqual(
            {
                "block_sequence_counter": [0x01],
                "transferResponseParameterRecord": [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF],
            },
            b,
        )  # ... (returns a dict)

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_request_seq02(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x76, 0x02, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        b = a.transfer_data(
            0x02,
            [
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
        )  # ... calls __transfer_data, which does the Uds.send - takes block_sequence_counter and parameterRecord

        canTp_send.assert_called_with(
            [
                0x36,
                0x02,
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
            False,
        )
        self.assertEqual(
            {
                "block_sequence_counter": [0x02],
                "transferResponseParameterRecord": [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF],
            },
            b,
        )  # ... (returns a dict)

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_neg_response_0x13(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x36, 0x13]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        try:
            b = a.transfer_data(
                0x01,
                [
                    0xF1,
                    0xF2,
                    0xF3,
                    0xF4,
                    0xF5,
                    0xF6,
                    0xF7,
                    0xF8,
                    0xF9,
                    0xFA,
                    0xFB,
                    0xFC,
                    0xFD,
                    0xFE,
                    0xFF,
                ],
            )  # ... calls __transfer_data, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
            False,
        )
        self.assertEqual(0x13, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_neg_nesponse_0x24(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x36, 0x24]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        try:
            b = a.transfer_data(
                0x01,
                [
                    0xF1,
                    0xF2,
                    0xF3,
                    0xF4,
                    0xF5,
                    0xF6,
                    0xF7,
                    0xF8,
                    0xF9,
                    0xFA,
                    0xFB,
                    0xFC,
                    0xFD,
                    0xFE,
                    0xFF,
                ],
            )  # ... calls __transfer_data, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
            False,
        )
        self.assertEqual(0x24, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_neg_response_0x31(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x36, 0x31]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        try:
            b = a.transfer_data(
                0x01,
                [
                    0xF1,
                    0xF2,
                    0xF3,
                    0xF4,
                    0xF5,
                    0xF6,
                    0xF7,
                    0xF8,
                    0xF9,
                    0xFA,
                    0xFB,
                    0xFC,
                    0xFD,
                    0xFE,
                    0xFF,
                ],
            )  # ... calls __transfer_data, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
            False,
        )
        self.assertEqual(0x31, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_neg_response_0x71(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x36, 0x71]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        try:
            b = a.transfer_data(
                0x01,
                [
                    0xF1,
                    0xF2,
                    0xF3,
                    0xF4,
                    0xF5,
                    0xF6,
                    0xF7,
                    0xF8,
                    0xF9,
                    0xFA,
                    0xFB,
                    0xFC,
                    0xFD,
                    0xFE,
                    0xFF,
                ],
            )  # ... calls __transfer_data, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
            False,
        )
        self.assertEqual(0x71, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_neg_response_0x72(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x36, 0x72]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        try:
            b = a.transfer_data(
                0x01,
                [
                    0xF1,
                    0xF2,
                    0xF3,
                    0xF4,
                    0xF5,
                    0xF6,
                    0xF7,
                    0xF8,
                    0xF9,
                    0xFA,
                    0xFB,
                    0xFC,
                    0xFD,
                    0xFE,
                    0xFF,
                ],
            )  # ... calls __transfer_data, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
            False,
        )
        self.assertEqual(0x72, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_neg_response_0x73(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x36, 0x73]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        try:
            b = a.transfer_data(
                0x01,
                [
                    0xF1,
                    0xF2,
                    0xF3,
                    0xF4,
                    0xF5,
                    0xF6,
                    0xF7,
                    0xF8,
                    0xF9,
                    0xFA,
                    0xFB,
                    0xFC,
                    0xFD,
                    0xFE,
                    0xFF,
                ],
            )  # ... calls __transfer_data, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
            False,
        )
        self.assertEqual(0x73, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_neg_responsee_0x92(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x36, 0x92]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        try:
            b = a.transfer_data(
                0x01,
                [
                    0xF1,
                    0xF2,
                    0xF3,
                    0xF4,
                    0xF5,
                    0xF6,
                    0xF7,
                    0xF8,
                    0xF9,
                    0xFA,
                    0xFB,
                    0xFC,
                    0xFD,
                    0xFE,
                    0xFF,
                ],
            )  # ... calls __transfer_data, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
            False,
        )
        self.assertEqual(0x92, b["NRC"])

    # patches are inserted in reverse order
    @mock.patch("uds.TestTp.recv")
    @mock.patch("uds.TestTp.send")
    def test_trans_data_neg_response_0x93(self, canTp_send, canTp_recv):

        canTp_send.return_value = False
        canTp_recv.return_value = [0x7F, 0x36, 0x93]

        # Parameters: xml file (odx file), ecu name (not currently used) ...
        a = createUdsConnection(
            "../Functional Tests/Bootloader.odx", 
            "bootloader", 
            transport_protocol = "TEST"
        )
        # ... creates the uds object and returns it; also parses out the rdbi info and attaches the __transfer_data to transfer_data in the uds object, so can now call below

        try:
            b = a.transfer_data(
                0x01,
                [
                    0xF1,
                    0xF2,
                    0xF3,
                    0xF4,
                    0xF5,
                    0xF6,
                    0xF7,
                    0xF8,
                    0xF9,
                    0xFA,
                    0xFB,
                    0xFC,
                    0xFD,
                    0xFE,
                    0xFF,
                ],
            )  # ... calls __transfer_data, which does the Uds.send
        except:
            b = traceback.format_exc().split("\n")[-2:-1][
                0
            ]  # ... extract the exception text
        canTp_send.assert_called_with(
            [
                0x36,
                0x01,
                0xF1,
                0xF2,
                0xF3,
                0xF4,
                0xF5,
                0xF6,
                0xF7,
                0xF8,
                0xF9,
                0xFA,
                0xFB,
                0xFC,
                0xFD,
                0xFE,
                0xFF,
            ],
            False,
        )
        self.assertEqual(0x93, b["NRC"])


if __name__ == "__main__":
    unittest.main()
