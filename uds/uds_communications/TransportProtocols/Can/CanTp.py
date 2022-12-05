#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"

import configparser
from os import path
from time import sleep

from uds.config import Config
from uds.interfaces import TpInterface
from uds import ResettableTimer, fill_array
from uds.uds_communications.TransportProtocols.Can.CanTpTypes import (
    CANTP_MAX_PAYLOAD_LENGTH,
    CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX,
    CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX,
    FC_BS_INDEX,
    FC_STMIN_INDEX,
    FIRST_FRAME_DATA_START_INDEX,
    FIRST_FRAME_DL_INDEX_HIGH,
    FIRST_FRAME_DL_INDEX_LOW,
    FLOW_CONTROL_BS_INDEX,
    FLOW_CONTROL_STMIN_INDEX,
    N_PCI_INDEX,
    SINGLE_FRAME_DATA_START_INDEX,
    SINGLE_FRAME_DL_INDEX,
    CanTpAddressingTypes,
    CanTpFsTypes,
    CanTpMessageType,
    CanTpMTypes,
    CanTpState,
)


##
# @class CanTp
# @brief This is the main class to support CAN transport protocol
#
# Will spawn a CanTpListener class for incoming messages
# depends on a bus object for communication on CAN
class CanTp(TpInterface):

    config_params = ["reqId", "resId", "addressing_type"]
    PADDING_PATTERN = 0x00

    ##
    # @brief constructor for the CanTp object
    def __init__(self, connector = None, **kwargs):


        self.__N_AE = Config.isotp.n_ae
        self.__N_TA = Config.isotp.n_ta
        self.__N_SA = Config.isotp.n_sa

        Mtype = Config.isotp.m_type
        if Mtype == "DIAGNOSTICS":
            self.__Mtype = CanTpMTypes.DIAGNOSTICS
        elif Mtype == "REMOTE_DIAGNOSTICS":
            self.__Mtype = CanTpMTypes.REMOTE_DIAGNOSTICS
        else:
            raise Exception("Do not understand the Mtype config")

        addressing_type = Config.isotp.addressing_type
        if addressing_type == "NORMAL":
            self.__addressing_type = CanTpAddressingTypes.NORMAL
        elif addressing_type == "NORMAL_FIXED":
            self.__addressing_type = CanTpAddressingTypes.NORMAL_FIXED
        elif self.__addressing_type == "EXTENDED":
            self.__addressing_type = CanTpAddressingTypes.EXTENDED
        elif addressing_type == "MIXED":
            self.__addressing_type = CanTpAddressingTypes.MIXED
        else:
            raise Exception("Do not understand the addressing config")

        self.__reqId = Config.isotp.req_id
        self.__resId = Config.isotp.res_id

        # sets up the relevant parameters in the instance
        if (self.__addressing_type == CanTpAddressingTypes.NORMAL) | (
            self.__addressing_type == CanTpAddressingTypes.NORMAL_FIXED
        ):
            self.__minPduLength = 7
            self.__maxPduLength = 63
            self.__pduStartIndex = 0
        elif (self.__addressing_type == CanTpAddressingTypes.EXTENDED) | (
            self.__addressing_type == CanTpAddressingTypes.MIXED
        ):
            self.__minPduLength = 6
            self.__maxPduLength = 62
            self.__pduStartIndex = 1
        self.__connection = connector
        self.__recvBuffer = []
        self.__discardNegResp = Config.isotp.discard_neg_resp

    ##
    # @brief send method
    # @param [in] payload the payload to be sent
    # @param [in] tpWaitTime time to wait inside loop
    def send(self, payload, functional_req=False, tpWaitTime=0.01):
        self.clear_buffered_messages()
        result = self.encode_isotp(payload, functional_req, tpWaitTime=tpWaitTime)
        return result

    ##
    # @brief encoding method
    # @param payload the payload to be sent
    # @param use_external_snd_rcv_functions boolean to state if external sending and receiving functions shall be used
    # @param [in] tpWaitTime time to wait inside loop
    def encode_isotp(
        self,
        payload,
        functional_req: bool = False,
        use_external_snd_rcv_functions: bool = False,
        tpWaitTime=0.01,
    ):

        payload_length = len(payload)
        payload_ptr = 0

        state = CanTpState.IDLE

        if payload_length > CANTP_MAX_PAYLOAD_LENGTH:
            raise Exception("Payload too large for CAN Transport Protocol")

        if payload_length < self.__maxPduLength:
            state = CanTpState.SEND_SINGLE_FRAME
        else:
            # we might need a check for functional request as we may not be able to service functional requests for
            # multi frame requests
            state = CanTpState.SEND_FIRST_FRAME

        tx_pdu = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        sequence_number = 1
        end_of_message_flag = False

        block_list = []
        curr_block = []

        # this needs fixing to get the timing from the config
        timeout_timer = ResettableTimer(1)
        st_min_timer = ResettableTimer()

        data = None

        while end_of_message_flag is False:

            rx_pdu = None

            if state == CanTpState.WAIT_FLOW_CONTROL:
                rx_pdu = self.get_next_buffered_message()

            if rx_pdu is not None:
                N_PCI = (rx_pdu[0] & 0xF0) >> 4
                if N_PCI == CanTpMessageType.FLOW_CONTROL:
                    fs = rx_pdu[0] & 0x0F
                    if fs == CanTpFsTypes.WAIT:
                        raise Exception("Wait not currently supported")
                    elif fs == CanTpFsTypes.OVERFLOW:
                        raise Exception("Overflow received from ECU")
                    elif fs == CanTpFsTypes.CONTINUE_TO_SEND:
                        if state == CanTpState.WAIT_FLOW_CONTROL:
                            bs = rx_pdu[FC_BS_INDEX]
                            if bs == 0:
                                bs = 585
                            block_list = self.create_block_list(payload[payload_ptr:], bs)
                            st_min = self.decode_stMin(rx_pdu[FC_STMIN_INDEX])
                            curr_block = block_list.pop(0)
                            state = CanTpState.SEND_CONSECUTIVE_FRAME
                            st_min_timer.timeout_time = st_min
                            st_min_timer.start()
                            timeout_timer.stop()
                        else:
                            raise Exception(
                                "Unexpected Flow Control Continue to Send request"
                            )
                    else:
                        raise Exception("Unexpected fs response from ECU")
                else:
                    raise Exception("Unexpected response from device")

            if state == CanTpState.SEND_SINGLE_FRAME:
                if len(payload) <= self.__minPduLength:
                    tx_pdu[N_PCI_INDEX] += CanTpMessageType.SINGLE_FRAME << 4
                    tx_pdu[SINGLE_FRAME_DL_INDEX] += payload_length
                    tx_pdu[SINGLE_FRAME_DATA_START_INDEX:] = fill_array(
                        payload, self.__minPduLength
                    )
                else:
                    tx_pdu[N_PCI_INDEX] = 0
                    tx_pdu[FIRST_FRAME_DL_INDEX_LOW] = payload_length
                    tx_pdu[FIRST_FRAME_DATA_START_INDEX:] = payload
                data = self.transmit(
                    tx_pdu, functional_req, use_external_snd_rcv_functions
                )
                end_of_message_flag = True
            elif state == CanTpState.SEND_FIRST_FRAME:
                payload_length_high_nibble = (payload_length & 0xF00) >> 8
                payload_length_low_nibble = payload_length & 0x0FF
                tx_pdu[N_PCI_INDEX] += CanTpMessageType.FIRST_FRAME << 4
                tx_pdu[FIRST_FRAME_DL_INDEX_HIGH] += payload_length_high_nibble
                tx_pdu[FIRST_FRAME_DL_INDEX_LOW] += payload_length_low_nibble
                tx_pdu[FIRST_FRAME_DATA_START_INDEX:] = payload[
                    0 : self.__maxPduLength - 1
                ]
                payload_ptr += self.__maxPduLength - 1
                data = self.transmit(
                    tx_pdu, functional_req, use_external_snd_rcv_functions
                )
                timeout_timer.start()
                state = CanTpState.WAIT_FLOW_CONTROL
            elif state == CanTpState.SEND_CONSECUTIVE_FRAME:
                if st_min_timer.is_expired():
                    tx_pdu[N_PCI_INDEX] += CanTpMessageType.CONSECUTIVE_FRAME << 4
                    tx_pdu[CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX] += sequence_number
                    tx_pdu[CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX:] = curr_block.pop(
                        0
                    )
                    payload_ptr += self.__maxPduLength
                    data = self.transmit(
                        tx_pdu, functional_req, use_external_snd_rcv_functions
                    )
                    sequence_number = (sequence_number + 1) % 16
                    st_min_timer.restart()
                    if len(curr_block) == 0:
                        if len(block_list) == 0:
                            end_of_message_flag = True
                        else:
                            timeout_timer.start()
                            state = CanTpState.WAIT_FLOW_CONTROL
            else:
                sleep(tpWaitTime)
            tx_pdu = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            # timer / exit condition checks
            if timeout_timer.is_expired():
                raise Exception("Timeout waiting for message")
        if use_external_snd_rcv_functions:
            return data

    ##
    # @brief recv method
    # @param [in] timeout_ms The timeout to wait before exiting
    # @return a list
    def recv(self, timeout_s=1):
        return self.decode_isotp(timeout_s)

    ##
    # @brief decoding method
    # @param timeout_ms the timeout to wait before exiting
    # @param received_data the data that should be decoded in case of ITF Automation
    # @param use_external_snd_rcv_functions boolean to state if external sending and receiving functions shall be used
    # @return a list
    def decode_isotp(
        self,
        timeout_s=1,
        received_data=None,
        use_external_snd_rcv_functions: bool = False,
    ):
        timeout_timer = ResettableTimer(timeout_s)

        payload = []
        payload_ptr = 0
        payload_length = None

        sequence_number_expected = 1

        tx_pdu = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        end_of_message_flag = False

        state = CanTpState.IDLE

        timeout_timer.start()
        while end_of_message_flag is False:

            if (
                use_external_snd_rcv_functions
                and state != CanTpState.RECEIVING_CONSECUTIVE_FRAME
            ):
                rx_pdu = received_data
            else:
                rx_pdu = self.get_next_buffered_message()

            if rx_pdu is not None:
                if rx_pdu[N_PCI_INDEX] == 0x00:
                    rx_pdu = rx_pdu[1:]
                    N_PCI = 0
                else:
                    N_PCI = (rx_pdu[N_PCI_INDEX] & 0xF0) >> 4
                if state == CanTpState.IDLE:
                    if N_PCI == CanTpMessageType.SINGLE_FRAME:
                        payload_length = rx_pdu[N_PCI_INDEX & 0x0F]
                        payload = rx_pdu[
                            SINGLE_FRAME_DATA_START_INDEX : SINGLE_FRAME_DATA_START_INDEX
                            + payload_length
                        ]
                        end_of_message_flag = True
                    elif N_PCI == CanTpMessageType.FIRST_FRAME:
                        payload = rx_pdu[FIRST_FRAME_DATA_START_INDEX:]
                        payload_length = (
                            (rx_pdu[FIRST_FRAME_DL_INDEX_HIGH] & 0x0F) << 8
                        ) + rx_pdu[FIRST_FRAME_DL_INDEX_LOW]
                        payload_ptr = self.__maxPduLength - 1
                        state = CanTpState.SEND_FLOW_CONTROL
                elif state == CanTpState.RECEIVING_CONSECUTIVE_FRAME:
                    if N_PCI == CanTpMessageType.CONSECUTIVE_FRAME:
                        sequence_number = (
                            rx_pdu[CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX] & 0x0F
                        )
                        if sequence_number != sequence_number_expected:
                            raise Exception("Consecutive frame sequence out of order")
                        else:
                            sequence_number_expected = (sequence_number_expected + 1) % 16
                        payload += rx_pdu[CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX:]
                        payload_ptr += self.__maxPduLength
                        timeout_timer.restart()
                    else:
                        raise Exception("Unexpected PDU received")
            else:
                sleep(0.01)

            if state == CanTpState.SEND_FLOW_CONTROL:
                tx_pdu[N_PCI_INDEX] = 0x30
                tx_pdu[FLOW_CONTROL_BS_INDEX] = 0
                tx_pdu[FLOW_CONTROL_STMIN_INDEX] = 0x1E
                self.transmit(tx_pdu)
                state = CanTpState.RECEIVING_CONSECUTIVE_FRAME

            if payload_length is not None:
                if payload_ptr >= payload_length:
                    end_of_message_flag = True

            if timeout_timer.is_expired():
                raise Exception("Timeout in waiting for message")

        return list(payload[:payload_length])


    ##
    # @brief clear out the receive list
    def clear_buffered_messages(self):
        self.__recvBuffer = []

    ##
    # @brief retrieves the next message from the received message buffers
    # @return list, or None if nothing is on the receive list
    def get_next_buffered_message(self):
        length = len(self.__recvBuffer)
        if length != 0:
            return self.__recvBuffer.pop(0)
        else:
            return None

    ##
    # @brief the listener callback used when a message is received
    def callback_on_receive(self, msg):
        if self.__addressing_type == CanTpAddressingTypes.NORMAL:
            if msg.arbitration_id == self.__resId:
                self.__recvBuffer.append(msg.data[self.__pduStartIndex :])
        elif self.__addressing_type == CanTpAddressingTypes.NORMAL_FIXED:
            raise Exception("I do not know how to receive this addressing type yet")
        elif self.__addressing_type == CanTpAddressingTypes.MIXED:
            raise Exception("I do not know how to receive this addressing type yet")
        else:
            raise Exception("I do not know how to receive this addressing type")

    ##
    # @brief function to decode the StMin parameter
    @staticmethod
    def decode_stMin(val):
        if val <= 0x7F:
            time = val / 1000
            return time
        elif (val >= 0xF1) & (val <= 0xF9):
            time = (val & 0x0F) / 10000
            return time
        else:
            raise Exception("Unknown STMin time")

    ##
    # @brief creates the blocklist from the blocksize and payload
    def create_block_list(self, payload, blockSize):

        block_list = []
        curr_block = []
        curr_pdu = []

        payload_ptr = 0
        blockPtr = 0

        payload_length = len(payload)
        pdu_length = self.__maxPduLength
        block_length = blockSize * pdu_length

        working = True
        while working:
            if (payload_ptr + pdu_length) >= payload_length:
                working = False
                curr_pdu = fill_array(
                    payload[payload_ptr:], pdu_length, fillValue=self.PADDING_PATTERN
                )
                curr_block.append(curr_pdu)
                block_list.append(curr_block)

            if working:
                curr_pdu = payload[payload_ptr : payload_ptr + pdu_length]
                curr_block.append(curr_pdu)
                payload_ptr += pdu_length
                blockPtr += pdu_length

                if blockPtr == block_length:
                    block_list.append(curr_block)
                    curr_block = []
                    blockPtr = 0

        return block_list

    ##
    # @brief transmits the data over can using can connection
    def transmit(
        self, data, functional_req=False, use_external_snd_rcv_functions: bool = False
    ):
        # check functional request
        if functional_req:
            raise Exception("Functional requests are currently not supported")

        transmit_data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        if (self.__addressing_type == CanTpAddressingTypes.NORMAL) | (
            self.__addressing_type == CanTpAddressingTypes.NORMAL_FIXED
        ):
            transmit_data = data
        elif self.__addressing_type == CanTpAddressingTypes.MIXED:
            transmit_data[0] = self.__N_AE
            transmit_data[1:] = data
        else:
            raise Exception("I do not know how to send this addressing type")
        self.__connection.transmit(transmit_data, self.__reqId)

    @property
    def req_dd_address(self):
        return self.__reqId

    @req_dd_address.setter
    def req_dd_address(self, value):
        self.__reqId = value

    @property
    def res_id_address(self):
        return self.__resId

    @res_id_address.setter
    def res_id_address(self, value):
        self.__resId = value

    @property
    def connection(self):
        return self.__connection

    @connection.setter
    def connection(self, value):
        self.__connection = value