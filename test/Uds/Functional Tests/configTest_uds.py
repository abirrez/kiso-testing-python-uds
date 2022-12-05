from time import sleep

import can
from can import Listener, Notifier

from uds import Uds


def on_callback_receive(msg):
    print(
        "Received: {0} on ID: {1} on virtualInterface".format(
            list(msg.data), hex(msg.arbitration_id)
        )
    )
    pass


def on_callback_receive2(msg):
    print(
        "Received: {0} on ID: {1} on anotherBus".format(
            list(msg.data), hex(msg.arbitration_id)
        )
    )
    pass


if __name__ == "__main__":

    bus = can.interface.Bus("virtualInterface", bustype = "virtual")
    bus2 = can.interface.Bus("anotherBus", bustype = "virtual")

    listener = Listener()
    listener.on_message_received = on_callback_receive
    notifier = Notifier(bus, [listener], 0)

    listener2 = Listener()
    listener2.on_message_received = on_callback_receive2
    notifier2 = Notifier(bus2, [listener2], 0)

    a = Uds()
    a.send([0x22, 0xF1, 0x8C], response_required  = False)

    b = Uds("bootloader.ini")
    b.send([0x22, 0xF1, 0x80], response_required = False)

    c = Uds("bootloader2.ini")
    c.send([0x22, 0xF1, 0x81], response_required = False)

    try:
        d = Uds("subaruEcm.ini")
    except:
        print("Subaru ECM test passed, using doip, exception caught")

    e = Uds(reqId = 0x620, resId = 0x670)
    e.send([0x22, 0xF1, 0x83], response_required = False)

    sleep(1)
