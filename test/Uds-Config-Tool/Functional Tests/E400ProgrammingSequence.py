import hashlib
from struct import pack, unpack
from time import sleep, time

from uds import createUdsConnection


class ihexData(object):
    def __init__(self):

        self.__startAddress = 0
        self.__size = 0
        self.__data = []

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

    def add_data(self, value):
        self.__data += value

    def get_data_from_address(self, address, size):
        raise NotImplemented("get_data_from_address Not yet implemented")


class ihex_file(object):
    def __init__(self, filename = None, padding = 0xFF, continuous_blocking = True):

        hexFile = open(filename, "r")

        self.__blocks = []

        eof_flag = False
        linecount = 1

        current_address = None
        next_address = None

        current_block = None
        base_address = 0

        while not eof_flag:

            line = hexFile.readline()

            if line[0] != ":":
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

            if record_type == 0x00:
                if current_address is None:
                    current_block.start_address = base_address + address

                if next_address is not None:
                    if address != next_address:
                        if continuous_blocking:
                            padding_block = []
                            [
                                padding_block.append(padding)
                                for i in range(0, address - next_address)
                            ]
                            current_block.add_data(padding_block)
                        else:
                            # print("new block")
                            pass
                current_block.add_data(data)
                current_address = address
                next_address = address + data_length

            elif record_type == 0x01:
                eof_flag = True
                if current_block is not None:
                    self.__blocks.append(current_block)
            elif record_type == 0x02:
                raise NotImplemented("Not implemented extended segment address")
            elif record_type == 0x03:
                raise NotImplemented("Start segment address not implemented")
            elif record_type == 0x04:
                # print("New block")
                if current_block is None:
                    current_block = ihexData()
                    base_address = address << 16
                else:
                    self.__blocks.append(current_block)

            elif record_type == 0x05:
                raise NotImplemented("Start linear address not implemented")

            linecount += 1

            pass

    def get_blocks(self):
        return self.__blocks


def calculate_key_from_seed(seed, ecuKey):

    device_secret = [
        0x46,
        0x45,
        0x44,
        0x43,
        0x42,
        0x41,
        0x39,
        0x38,
        0x37,
        0x36,
        0x35,
        0x34,
        0x33,
        0x32,
        0x31,
        0x30,
    ]

    md5_input = device_secret + seed + device_secret
    c = pack("%sB" % len(md5_input), *md5_input)
    d = hashlib.md5(c).digest()
    dUnpack = unpack("%sB" % 16, d)
    send_list = [val for val in dUnpack]

    return send_list


if __name__ == "__main__":

    # secondaryBootloaderContainer = chunkIhexFile("TGT-ASSY-1383_v2.1.0_sbl.hex")
    # print(secondaryBootloaderContainer)
    secondary_bootloader = ihex_file("TGT-ASSY-1383_v2.1.0_sbl.hex")
    blocks = secondary_bootloader.get_blocks()
    block_data = blocks[0].data
    smaller_chunks = []
    chunk = []
    count = 0
    for i in range(0, len(block_data)):
        chunk.append(block_data[i])
        count += 1
        if count == 1280:
            smaller_chunks.append(chunk)
            chunk = []
            count = 0

    if len(chunk) != 0:
        smaller_chunks.append(chunk)

    e400 = createUdsConnection(
        "Bootloader.odx", 
        "Bootloader", 
        reqId=0x600, 
        resId=0x650, 
        interface = "peak"
    )

    a = e400.read_data_by_identifier("ECU Serial Number")
    print("Serial Number: {0}".format(a["ECU Serial Number"]))

    a = e400.read_data_by_identifier("PBL Part Number")
    print("PBL Part Number: {0}".format(a["PBL Part Number"]))

    a = e400.read_data_by_identifier("PBL Version Number")
    print("PBL Version Number: {0}".format(a["PBL Version Number"]))

    a = e400.diagnosticSessionControl("Programming Session")
    print("In Programming Session")

    a = e400.securityAccess("Programming Request")
    print("Security Key: {0}".format(a))

    b = calculate_key_from_seed(a, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    print("Calculated Key: {0}".format(b))

    a = e400.securityAccess("Programming Key", b)
    print("Security Access Granted")

    print("Setting up transfer of Secondary Bootloader")
    a = e400.requestDownload([0], [0x40, 0x03, 0xE0, 0x00], [0x00, 0x00, 0x0E, 0x56])
    # print(a)

    print("Transferring Secondary Bootloader")
    for i in range(len(smaller_chunks)):
        a = e400.transfer_data(i + 1, smaller_chunks[i])

    print("Finished Transfer")
    a = e400.transferExit()

    print("Jumping to Secondary Bootloader")
    a = e400.routineControl("Start Secondary Bootloader", 1, [0x4003E000])
    # print(a)

    print("Erasing Memory")
    a = e400.routineControl(
        "Erase Memory",
        1,
        [("memoryAddress", [0x00080000]), ("memorySize", [0x000162E4])],
    )
    # print(a)

    working = True
    while working:

        a = e400.routineControl("Erase Memory", 3)
        # print(a)
        if (a["Erase Memory Status"]) == [0x30]:
            print("Erased memory")
            working = False
        elif a["Erase Memory Status"] == [0x31]:
            print("ABORTED")
            raise Exception("Erase memory unsuccessful")
        sleep(0.001)

    application = ihex_file("e400_uds_test_app_e400.ihex")
    blocks = application.get_blocks()
    block_data = blocks[0].data
    smaller_chunks = []
    chunk = []
    count = 0
    for i in range(0, len(block_data)):
        chunk.append(block_data[i])
        count += 1
        if count == 1280:
            smaller_chunks.append(chunk)
            chunk = []
            count = 0

    if len(chunk) != 0:
        smaller_chunks.append(chunk)

    print("Setting up transfer for Application")
    a = e400.requestDownload([0], [0x00, 0x08, 0x00, 0x00], [0x00, 0x01, 0x62, 0xE4])

    print("Transferring Application")
    for i in range(0, len(smaller_chunks)):

        a = e400.transfer_data(i + 1, smaller_chunks[i])

    print("Transfer Exit")
    a = e400.transferExit()

    a = e400.routineControl("Check Valid Application", 0x01)

    working = True
    while working:
        # a = e400.send([0x31, 0x03, 0x03, 0x04])
        # print(a)
        # if a[4] == 0x30:
        #     working = False
        #     print("Success")
        # elif a[4] == 0x31:
        #     working = False
        #     print("Aborted")
        a = e400.routineControl("Check Valid Application", 0x03)

        routine_status = a["Valid Application Status"][0]
        application_present = a["Valid Application Present"][0]

        if routine_status == 0x30:
            working = False
            print("Routine Finished")

            if application_present == 0x01:
                print("Application Invalid")
            elif application_present == 0x02:
                print("Application Valid")
        elif routine_status == 0x31:
            working = False
            print("Aborted")
        elif routine_status == 0x32:
            # print("Working")
            pass

        sleep(0.01)

    e400.ecuReset("Hard Reset", suppress_response = True)
