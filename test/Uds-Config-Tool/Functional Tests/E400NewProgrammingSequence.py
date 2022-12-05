import hashlib
from struct import pack, unpack
from time import sleep, time

from uds import DecodeFunctions, createUdsConnection, ihex_file


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

    sbl = ihex_file("TGT-ASSY-1383_v2.1.0_sbl.hex")

    app = ihex_file("e400_uds_test_app_e400.ihex")

    e400 = createUdsConnection(
        "Bootloader.odx", 
        "Bootloader", 
        reqId=0x601, 
        resId=0x651, 
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
    transmit_address = sbl.transmit_address
    transmit_length = sbl.transmit_length

    a = e400.requestDownload([0], transmit_address, transmit_length)
    # print(a)

    print("Transferring Secondary Bootloader")
    chunks = sbl.transmit_chunks(send_chunksize=1280)
    for i in range(len(chunks)):
        a = e400.transfer_data(i + 1, chunks[i])

    print("Finished Transfer")
    a = e400.transferExit()

    print("Jumping to Secondary Bootloader")
    a = e400.routineControl(
        "Start Secondary Bootloader",
        1,
        [DecodeFunctions.build_int_from_list(transmit_address)],
    )
    # print(a)

    print("In Secondary Bootloader")
    print("Erasing Memory")

    transmit_address = app.transmit_address
    transmit_length = app.transmit_length
    a = e400.routineControl(
        "Erase Memory",
        1,
        [
            ("memoryAddress", [DecodeFunctions.build_int_from_list(transmit_address)]),
            ("memorySize", [DecodeFunctions.build_int_from_list(transmit_length)]),
        ],
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

    print("Setting up transfer for Application")

    print("Transferring Application")
    blocks = app.blocks

    for i in blocks:
        chunks = i.transmit_chunks(1280)
        transmit_address = i.transmit_address
        transmit_length = i.transmit_length
        a = e400.requestDownload([0], transmit_address, transmit_length)

        for j in range(0, len(chunks)):
            a = e400.transfer_data(j + 1, chunks[j])

    # for i in range(0, len(chunks)):
    #
    #     a = e400.transfer_data(i+1, chunks[i])

    print("Transfer Exit")
    a = e400.transferExit()

    a = e400.routineControl("Check Valid Application", 0x01)

    working = True
    while working:

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

    e400.ecuReset("Hard Reset", suppress_response=True)
