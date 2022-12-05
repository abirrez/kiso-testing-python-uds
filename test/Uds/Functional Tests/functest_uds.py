#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from threading import Thread
from time import sleep, time

import can

from uds import Uds

recv_buffer = []
bus = can.interface.Bus("virtualInterface", bustype="virtual")


def clear_receive_buffer():
    global recv_buffer
    recv_buffer = []


def get_next_received_message():
    global recv_buffer
    if len(recv_buffer) == 0:
        return None
    else:
        return recv_buffer.pop(0)


def on_receive_callback(msg):
    global recv_buffer
    recv_buffer.append(msg.data)


def single_frame_response_target():

    global bus

    working = True
    start_time = time()

    can_msg = can.Message(arbitration_id = 0x650)
    clear_receive_buffer()

    while working:
        curr_time = time()
        if (curr_time - start_time) > 5:
            working = False

        recv_msg = get_next_received_message()

        if recv_msg is not None:
            can_msg.data = [0x04, 0x62, 0xF1, 0x8C, 0x01]
            bus.send(can_msg)
            working = False


def multi_frame_response_target():

    global bus

    working = True
    start_time = time()

    can_msg = can.Message(arbitration_id = 0x650)
    clear_receive_buffer()

    index = 0

    response = False

    while working:
        curr_time = time()
        if (curr_time - start_time) > 50:
            working = False

        recv_msg = get_next_received_message()

        if recv_msg is not None:
            response = True

        if response:
            if index == 0:
                sleep(0.002)
                can_msg.data = [0x10, 0x13, 0x62, 0xF1, 0x8C, 0x30, 0x30, 0x30]
                index = 1
            elif index == 1:
                can_msg.data = [0x21, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30]
                index = 2
            elif index == 2:
                can_msg.data = [0x22, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x00]
                working = False

            bus.send(can_msg)
            sleep(0.020)


if __name__ == "__main__":

    listener = can.Listener()
    notifier = can.Notifier(bus, [listener], 0)

    listener.on_message_received = on_receive_callback

    udsConnection = Uds()

    print("Test 1")
    clear_receive_buffer()
    receiveThread = Thread(target = single_frame_response_target)
    receiveThread.start()
    sleep(0.2)
    a = udsConnection.send([0x22, 0xF1, 0x8C])
    print(a)

    while receiveThread.is_alive():
        pass

    print("Test 2")
    clear_receive_buffer()
    receiveThread = Thread(target = multi_frame_response_target)
    receiveThread.start()
    a = udsConnection.send([0x22, 0xF1, 0x8C])
    print(a)

    while receiveThread.is_alive():
        pass
