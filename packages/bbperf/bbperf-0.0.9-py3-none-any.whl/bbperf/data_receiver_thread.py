# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

import time
import socket

from . import const
from . import util

# args are client args
def run(args, control_conn, data_sock):

    if args.verbosity:
        print("starting data receiver process", flush=True)

    # do not block on the below recv calls as we want to exit the process when
    # the "end of run" timer expires even if the flow of packets has stopped
    data_sock.settimeout(0.05)

    total_recv_calls = 0

    interval_start_time = time.time()
    interval_end_time = interval_start_time + const.SAMPLE_INTERVAL_SEC

    interval_pkts_received = 0
    interval_bytes_received = 0

    socket_timeout_timer_active = False
    socket_timeout_timer_start_time = None

    # do until end of test duration
    # we will not get a connection close with udp
    while True:
        num_bytes_read = 0

        try:
            # works for both tcp and udp
            # recv with timeout
            bytes_read = data_sock.recv(const.BUFSZ)

            num_bytes_read = len(bytes_read)

            if num_bytes_read == 0:
                # (tcp only) peer has disconnected
                if args.verbosity:
                    print("peer disconnected (data socket)", flush=True)
                # exit process
                break

            socket_timeout_timer_active = False

        except socket.timeout:
            if socket_timeout_timer_active:
                if (time.time() - socket_timeout_timer_start_time) > const.SOCKET_TIMEOUT_SEC:
                    raise Exception("FATAL: data_receiver_thread: timeout during data socket read")
            else:
                socket_timeout_timer_active = True
                socket_timeout_timer_start_time = time.time()

        if args.udp and num_bytes_read == len(const.UDP_STOP_MSG) and (bytes_read.decode() == const.UDP_STOP_MSG):
            if args.verbosity:
                print("data receiver thread: received udp stop message, exiting", flush=True)
            break

        if num_bytes_read == 0:
            # recv must have timed out, skip the rest of this loop
            continue

        curr_time_sec = time.time()

        total_recv_calls += 1

        interval_pkts_received += 1                     # valid for udp only
        interval_bytes_received += num_bytes_read

        # end of interval
        # send interval record over control connection
        if curr_time_sec > interval_end_time:
            interval_time_sec = curr_time_sec - interval_start_time

            # find the packet send time in the user payload

            a_b_block = None

            idx_of_a = bytes_read.find(b' a ')
            if idx_of_a > -1:
                idx_of_b = bytes_read.find(b' b ', idx_of_a)
                if idx_of_b > -1:
                    a_b_block = bytes_read[ idx_of_a : idx_of_b + 3 ]

            if a_b_block is None:
                # skip sending for this packet, but stay "in" sample interval
                continue

            # sending info back to client on control connection

            ba = bytearray()
            ba.extend(a_b_block)
            ba.extend(str(interval_time_sec).encode())
            ba.extend(b' ')
            ba.extend(str(interval_pkts_received).encode())
            ba.extend(b' ')
            ba.extend(str(interval_bytes_received).encode())
            ba.extend(b' ')
            ba.extend(str(total_recv_calls).encode())       # num of pkts received, valid for udp only
            ba.extend(b' c ')

            try:
                control_conn.send(ba)

            except Exception:
                print("ERROR: send on control socket failed", flush=True)
                # exit process
                break

            interval_bytes_received = 0
            interval_pkts_received = 0

            interval_start_time = curr_time_sec
            interval_end_time = interval_start_time + const.SAMPLE_INTERVAL_SEC


    # peer disconnected (or an error)
    util.done_with_socket(data_sock)
    control_conn.close()

    if args.verbosity:
        print("exiting data receiver process", flush=True)
