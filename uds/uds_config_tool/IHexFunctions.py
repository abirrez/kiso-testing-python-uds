#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2019, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


import hashlib
import os
from enum import IntEnum
from struct import pack, unpack
from time import sleep, time

from uds.uds_config_tool import DecodeFunctions
from uds.uds_config_tool.ISOStandard.ISOStandard import IsoDataFormatIdentifier


class ihexRecordType(IntEnum):

    DATA = 0x00
    END_OF_FILE = 0x01
    EXTENDED_SEGMENT_ADDRESS = 0x02
    START_SEGMENT_ADDRESS = 0x03
    EXTENDED_LINEAR_ADDRESS = 0x04
    START_LINEAR_ADDRESS = 0x05


class ihexData(object):
    def __init__(self):

        self.__startAddress = 0
        self.__size = 0
        self.__data = []
        self.__send_chunksize = None
        self.__send_chunks = None

    @property
    def start_address(self):
        return self.__startAddress

    @start_address.setter
    def start_address(self, value):
        self.__startAddress = value

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value

    @property
    def data_length(self):
        return len(self.__data)

    @property
    def transmit_chunksize(self):
        return self.__send_chunksize

    @start_address.setter
    def transmit_chunksize(self, value):
        # TODO: need to check permitted ranges if any!!!
        if self.__send_chunksize != value:
            self.__send_chunks = None  # ... send chunks needs re-calculating if required, so force this by setting to null here.
        self.__send_chunksize = value

    def transmit_chunks(
        self, send_chunksize=None
    ):  # ... initialising or re-setting of the chunk size is allowed here for convenience.
        if send_chunksize is not None:
            self.transmit_chunksize = send_chunksize
        if self.__send_chunksize is not None and self.__data != []:
            self.__send_chunks = []
            chunk = []
            count = 0
            for i in range(0, len(self.__data)):
                chunk.append(self.__data[i])
                count += 1
                if count == self.__send_chunksize:
                    self.__send_chunks.append(chunk)
                    chunk = []
                    count = 0
            if len(chunk) != 0:
                self.__send_chunks.append(chunk)
        if self.__send_chunks is None:
            return []
        return self.__send_chunks

    @property
    def transmit_length(self):  # ... this is data_length encoded
        return DecodeFunctions.int_array_to_int_array(
            [self.data_length], "int32", "int8"
        )  # ... length calc'd as [0x00, 0x01, 0x4F, 0xe4] as expected

    def add_data(self, value):
        self.__data += value
        self.__send_chunks = None

    def get_data_from_address(self, address, size):
        raise NotImplemented("get_data_from_address Not yet implemented")

    @property
    def transmit_address(self):
        return DecodeFunctions.int_array_to_int_array(
            [self.__startAddress], "int32", "int8"
        )


class ihex_file(object):
    def __init__(self, filename=None, padding=0xFF, continuous_blocking=True):

        hexFile = open(filename, "r")

        self.__blocks = []

        eof_flag = False
        linecount = 1

        next_address = None

        current_block = None
        base_address = 0

        self.__send_chunksize = None

        while not eof_flag:
            line = hexFile.readline()
            linecount += 1

            if line[0] != ":":
                hexFile.close()
                raise Exception("Unexpected line on line {0}".format(linecount))

            line_array = bytes.fromhex(line[1:])

            # get the main data
            index = 0
            data_length = line_array[index]
            index += 1
            address = (line_array[index] << 8) | (line_array[index + 1])
            index += 2
            record_type = line_array[index]
            index += 1
            data = line_array[index : index + data_length]
            index += data_length
            checksum = line_array[index]

            calculated_checksum = 0

            for i in range(len(line_array) - 1):
                calculated_checksum = (calculated_checksum + line_array[i]) % 256

            calculated_checksum = (~calculated_checksum + 1) % 256

            if calculated_checksum != checksum:
                hexFile.close()
                raise Exception(
                    "Checksum on line {0} does not match. Actual: {1}, Calculated: {2}".format(
                        linecount, checksum, calculated_checksum
                    )
                )

            # print("Length: {0:#x}, Address: {1:#x}, record_type: {2:#x}, data: {3}, checksum: {4:#x}, calculated_checksum: {5:#x}".format(data_length,
            #                                                                                                                             address,
            #                                                                                                                             record_type,
            #                                                                                                                             data,
            #                                                                                                                             checksum,
            #                                                                                                                             calculated_checksum))

            if (
                record_type == ihexRecordType.DATA
            ):  # ... We match data first as it's the most common record type, so more efficient
                if next_address is None:
                    current_block.start_address = base_address + address

                # As each line of data is individually addressed, there may be disconuities present in the data.
                # If so (i.e. a gap in the addressing), and a continuous record is required, then pad the data.
                # NOTE: by default, padding is expected.
                if next_address is not None:
                    if address != next_address:
                        if continuous_blocking:
                            padding_block = []
                            [
                                padding_block.append(padding)
                                for i in range(0, address - next_address)
                            ]
                            current_block.add_data(padding_block)

                current_block.add_data(data)
                next_address = address + data_length

            elif (
                record_type == ihexRecordType.EXTENDED_LINEAR_ADDRESS
            ):  # ... new block - append any existing block to the blocklist or initialise the current block record
                if current_block is not None:
                    # IMPORTANT NOTE (possible TODO): Richard indicated that the last data line may need some tail end padding - if that's the case, we would know about it
                    # till here, so the need for such padidng would have to be detected here and added (e.g. check a "required" flag, and if true, run a moduls op on
                    # block length to detect if padding needed, then add padding bytes, as above in continuous_blocking case).
                    self.__blocks.append(current_block)
                current_block = ihexData()  # ... start the new block
                base_address = ((data[0] << 8) + data[1]) << 16
                next_address = None

            elif (
                record_type == ihexRecordType.END_OF_FILE

            ):  # ... add the final block to the block list
                eof_flag = True
                if current_block is not None:
                    self.__blocks.append(current_block)

            elif record_type == ihexRecordType.EXTENDED_SEGMENT_ADDRESS:
                hexFile.close()
                raise NotImplemented("Not implemented extended segment address")

            elif record_type == ihexRecordType.START_SEGMENT_ADDRESS:
                hexFile.close()
                raise NotImplemented("Start segment address not implemented")

            elif record_type == ihexRecordType.START_LINEAR_ADDRESS:
                hexFile.close()
                raise NotImplemented("Start linear address not implemented")
        hexFile.close()

    @property
    def data_length(self):
        return sum([self.__blocks[i].data_length for i in range(self.num_blocks)])

    @property
    def num_blocks(self):
        return len(self.__blocks)

    @property
    def blocks(self):
        return self.__blocks

    @property
    def transmit_chunksize(self):
        return self.__send_chunksize

    @transmit_chunksize.setter
    def transmit_chunksize(self, value):
        # TODO: need to check permitted ranges if any!!!
        self.__send_chunksize = value
        for block in self.__blocks:
            block.transmit_chunksize = value

    def transmit_chunks(
        self, send_chunksize=None
    ):  # ... initialising or re-setting of the chunk size is allowed here for convenience.
        if send_chunksize is not None:
            self.transmit_chunksize = send_chunksize
        return sum(
            [self.__blocks[i].transmit_chunks() for i in range(self.num_blocks)], []
        )

    @property
    def transmit_length(self):  # ... this is data_length encoded
        return DecodeFunctions.int_array_to_int_array([self.data_length], "int32", "int8")

    @property
    def transmit_address(self):
        return self.__blocks[0].transmit_address


if __name__ == "__main__":

    app_blocks = ihex_file(
        "../../test/Uds-Config-Tool/Functional Tests/e400_uds_test_app_e400.hex"
    )
    # print(("found num blocks : ",  app_blocks.num_blocks))
    # print(("len block data[0] : ", app_blocks.block[0].data_length))
    # print(("len block data[1] : ", app_blocks.block[1].data_length))

    # smaller_chunks = app_blocks.block[0].transmit_chunks(send_chunksize=1280)  # ... breaking the data block to transmittable chunks
    # print(("found num small blocks : ", len(smaller_chunks)))
    # smaller_chunks = app_blocks.block[1].transmit_chunks(send_chunksize=1280)  # ... breaking the data block to transmittable chunks
    # print(("found num small blocks : ", len(smaller_chunks)))

    # transmit_chunks = sum([app_blocks.block[i].transmit_chunks(send_chunksize=1280) for i in range(app_blocks.num_blocks)],[])
    # print(("transmit total chunks : ", len(transmit_chunks)))

    # print(("transmit start address (all) : ", app_blocks.transmit_address))
    # print(("transmit start address (block 0) : ", app_blocks.block[0].transmit_address))
    # print(("transmit start address (block 1) : ", app_blocks.block[1].transmit_address))

    # transmit_length = sum([len(app_blocks.block[i].data) for i in range(app_blocks.num_blocks)])
    # print(("data length (total) : ",      app_blocks.data_length))
    # print(("transmit length (total) : ",  app_blocks.transmit_length))
    # print(("transmit length (block 0): ", app_blocks.block[0].transmit_length))

    """ Examples - see also unittest_TransDataFunctions.py for ihex test cases ...
    app_blocks = ihex_file("../../test/Uds-Config-Tool/Functional Tests/TGT-ASSY-1383_v2.1.0_sbl.hex")
    e400 = createUdsConnection("Bootloader.odx", "Bootloader", reqId=0x600, resId=0x650, interface="peak")
    a = e400.requestDownload([IsoDataFormatIdentifier.NO_COMPRESSION_METHOD], app_blocks.transmit_address, app_blocks.transmit_length)
	....
	app_blocks.transmit_chunksize = 1280
	a = e400.transfer_data(transfer_block=app_blocks.block[0])
	# ... or ...
	a = e400.transfer_data(transfer_blocks=app_blocks)
    ....
    a = e400.transferExit()
    """
