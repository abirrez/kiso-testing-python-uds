from time import sleep

from can import Bus, Listener, Notifier

from uds import Uds


def callback_on_receive(msg):

    if msg.arbitration_id == 0x600:
        print("Bootloader Receive:", list(msg.data))
    if msg.arbitration_id == 0x7E0:
        print("PCM Receive:", list(msg.data))


if __name__ == "__main__":

    recv_bus = Bus("virtualInterface", bustype="virtual")

    listener = Listener()
    notifier = Notifier(recv_bus, [listener], 0)

    listener.on_message_received = callback_on_receive

    a = Uds()

    a.send([0x22, 0xF1, 0x8C], response_required = False)

    sleep(2)
