#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"

import threading
from pathlib import Path
from typing import Callable

from uds.config import Config
from uds.factories import TpFactory
from uds.uds_config_tool.UdsConfigTool import UdsTool
from uds.uds_config_tool.IHexFunctions import ihex_file as ihexFileParser
from uds.uds_config_tool.ISOStandard.ISOStandard import IsoDataFormatIdentifier

##
# @brief a description is needed
class Uds(object):

    ##
    # @brief a constructor
    # @param [in] reqId The request ID used by the UDS connection, defaults to None if not used
    # @param [in] resId The response Id used by the UDS connection, defaults to None if not used
    def __init__(self, odx = None, ihex_file = None, **kwargs):

        self.__transport_protocol = Config.uds.transport_protocol
        self.__P2_CAN_Client = Config.uds.p2_can_client
        self.__P2_CAN_Server = Config.uds.p2_can_server

        self.tp = TpFactory.select_transport_protocol(self.__transport_protocol, **kwargs)

        # used as a semaphore for the tester present
        self.__transmission_active_flag = False

        # The above flag should prevent tester_present operation, but in case of race conditions, this lock prevents actual overlapo in the sending
        self.sendLock = threading.Lock()

        # Process any ihex file that has been associated with the ecu at initialisation
        self.__ihexFile = ihexFileParser(ihex_file) if ihex_file is not None else None
        self.load_odx(odx)

    def load_odx(self, odx_file: Path)-> None:
        """Lod the given odx file and create the associated UDS 
        diagnostic services:
        
        :param odx_file: idx file full path
        """
        if odx_file is None:
            return
        UdsTool.create_service_containers(odx_file)
        UdsTool.bind_containers(self)

    def overwrite_transmit_method(self, func : Callable):
        """override transmit method from the asscociated __connection

        :param func: callable use to replace the current configured 
            transmit method
        """
        self.tp.connection.transmit = func

    def overwrite_receive_method(self, func : Callable):
        """override the TP reception method

        :param func: callable use to replace the current 
            get_next_buffered_message method
        """
        self.tp.get_next_buffered_message = func

    @property
    def ihex_file(self):
        return self.__ihexFile

    @ihex_file.setter
    def ihex_file(self, value):
        if value is not None:
            self.__ihexFile = ihexFileParser(value)

    ##
    # @brief Currently only called from transfer_file to transfer ihex files
    def transfer_ihex_file(self, transmit_chunk_size = None, compression_method = None):
        if transmit_chunk_size is not None:
            self.__ihexFile.transmit_chunksize = transmit_chunk_size
        if compression_method is None:
            compression_method = IsoDataFormatIdentifier.NO_COMPRESSION_METHOD
        self.requestDownload(
            [compression_method],
            self.__ihexFile.transmit_address,
            self.__ihexFile.transmit_length,
        )
        self.transfer_data(transfer_blocks=self.__ihexFile)
        return self.transferExit()

    ##
    # @brief This will eventually support more than one file type, but for now is limited to ihex only
    def transfer_file(
        self, file_name = None, transmit_chunk_size = None, compression_method = None
    ):
        if file_name is None and self.__ihexFile is None:
            raise FileNotFoundError("file to transfer has not been specified")

        # Currently only ihex is recognised and supported
        if file_name[-4:] == ".hex" or file_name[-5:] == ".ihex":
            self.__ihexFile = ihexFileParser(file_name)
            return self.transfer_ihex_file(transmit_chunk_size, compression_method)
        else:
            raise FileNotFoundError(
                "file to transfer has not been recognised as a supported type ['.hex','.ihex']"
            )

    ##
    # @brief
    def send(self, msg, response_required = True, functional_req = False, tpWaitTime = 0.01):
        # sets a current transmission in progress - tester present (if running) will not send if this flag is set to true
        self.__transmission_active_flag = True
        # print(("__transmission_active_flag set:",self.__transmission_active_flag))

        response = None

        # We're moving to threaded operation, so putting a lock around the send operation.
        self.sendLock.acquire()
        try:
            a = self.tp.send(msg, functional_req, tpWaitTime)
        finally:
            self.sendLock.release()

        if functional_req is True:
            response_required = False

        # Note: in automated mode (unlikely to be used any other way), there is no response from tester present, so threading is not an issue here.
        if response_required:
            while True:
                response = self.tp.recv(self.__P2_CAN_Client)
                if not ((response[0] == 0x7F) and (response[2] == 0x78)):
                    break

        # If the diagnostic session control service is supported, record the sending time for possible use by the tester present functionality (again, if present) ...
        try:
            self.sessionSetLastSend()
        except:
            pass  # ... if the service isn't present, just ignore

        # Lets go of the hold on transmissions - allows test present to resume operation (if it's running)
        self.__transmission_active_flag = False
        # print(("__transmission_active_flag cleared:",self.__transmission_active_flag))

        return response

    ##
    # @brief
    def is_transmitting(self):
        return self.__transmission_active_flag
