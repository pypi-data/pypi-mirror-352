# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

import time
import socket
import select

from . import util
from . import const


# falling off the end of this method terminates the process
def run(args, data_sock, shared_run_mode, shared_udp_sending_rate_pps):
    if args.verbosity:
        print("data sender: start of process", flush=True)

    # udp autorate
    if args.udp:
        udp_pps = shared_udp_sending_rate_pps.value
        batch_size, delay_between_batches = util.convert_udp_pps_to_batch_info(udp_pps)

    # start sending

    if args.verbosity:
        print("data sender: sending", flush=True)

    curr_time_sec = time.time()

    interval_start_time = curr_time_sec
    interval_end_time = interval_start_time + const.SAMPLE_INTERVAL_SEC

    interval_time_sec = 0.0
    interval_send_count = 0
    interval_bytes_sent = 0

    accum_send_count = 0
    accum_bytes_sent = 0

    total_send_counter = 1

    calibration_start_time = time.time()

    while True:
        curr_time_sec = time.time()

        if (shared_run_mode.value == const.RUN_MODE_CALIBRATING):
            if curr_time_sec > (calibration_start_time + const.MAX_DURATION_CALIBRATION_TIME_SEC):
                error_msg = "FATAL: data_sender_thread: time in calibration exceeded max allowed"
                print(error_msg, flush=True)
                raise Exception(error_msg)

            is_calibrated = False
        else:
            is_calibrated = True

        record_type = b'run' if is_calibrated else b'cal'

        # we want to be fast here, since this is data write loop, so use ba.extend

        ba = bytearray()
        ba.extend(b' a ')
        ba.extend(record_type)
        ba.extend(b' ')
        ba.extend(str(curr_time_sec).encode())
        ba.extend(b' ')
        ba.extend(str(interval_time_sec).encode())
        ba.extend(b' ')
        ba.extend(str(interval_send_count).encode())
        ba.extend(b' ')
        ba.extend(str(interval_bytes_sent).encode())
        ba.extend(b' ')
        ba.extend(str(total_send_counter).encode())
        ba.extend(b' b ')

        if args.udp:
            ba.extend(const.PAYLOAD_1K)
        elif is_calibrated:
            ba.extend(const.PAYLOAD_4K)
        else:
            ba.extend(const.PAYLOAD_1K)

        try:
            # blocking
            # we want to block here, as blocked time should "count"

            # we use select to take advantage of tcp_notsent_lowat
            _, _, _ = select.select( [], [data_sock], [])

            # this works for both tcp and udp
            num_bytes_sent = data_sock.send(ba)

            if num_bytes_sent <= 0 or num_bytes_sent != len(ba):
                raise Exception("ERROR: data_sender_thread.run(): send failed")

        except ConnectionResetError:
            print("Connection reset by peer", flush=True)
            # exit process
            break

        except BrokenPipeError:
            # this can happen at the end of a tcp reverse test
            print("broken pipe error", flush=True)
            # exit process
            break

        except BlockingIOError:
            # same as EAGAIN EWOULDBLOCK
            # we did not send, loop back up and try again
            continue

        except socket.timeout:
            # we did not send
            # the timeout value here is 20 seconds, so that is end of days -- kill everything
            error_msg = "FATAL: data_sender_thread: socket timeout"
            print(error_msg, flush=True)
            raise Exception(error_msg)

        total_send_counter += 1
        accum_send_count += 1
        accum_bytes_sent += num_bytes_sent

        if curr_time_sec > interval_end_time:
            interval_time_sec = curr_time_sec - interval_start_time
            interval_send_count = accum_send_count
            interval_bytes_sent = accum_bytes_sent

            if args.verbosity > 2:
                print("data_sender: a {} {} {} {} {} {} b".format(
                    record_type, curr_time_sec, interval_time_sec, interval_send_count, interval_bytes_sent, total_send_counter),
                    flush=True
                )

            interval_start_time = curr_time_sec
            interval_end_time = interval_start_time + const.SAMPLE_INTERVAL_SEC
            accum_send_count = 0
            accum_bytes_sent = 0

            # update udp autorate
            if args.udp:
                udp_pps = shared_udp_sending_rate_pps.value
                batch_size, delay_between_batches = util.convert_udp_pps_to_batch_info(udp_pps)

        # send very slowly at first to establish unloaded latency
        if not is_calibrated:
            time.sleep(0.2)
            # initialize batch variables here in case next loop is batch processing
            current_batch_start_time = time.time()
            current_batch_counter = 0
            continue

        # normal end of test
        if shared_run_mode.value == const.RUN_MODE_STOP:
            break

        # pause between udp batches if necessary
        if args.udp:
            current_batch_counter += 1
            if current_batch_counter >= batch_size:
                this_delay = delay_between_batches - (curr_time_sec - current_batch_start_time)
                if this_delay > 0:
                    time.sleep(delay_between_batches)
                current_batch_start_time += delay_between_batches
                current_batch_counter = 0


    # send STOP message
    if args.udp:
        if args.verbosity:
            print("data sender: sending udp stop message", flush=True)
        payload_bytes = const.UDP_STOP_MSG.encode()
        # 3 times just in case the first one does not make it to the destination
        data_sock.send(payload_bytes)
        time.sleep(0.1)
        try:
            data_sock.send(payload_bytes)
        except:
            # probable "ConnectionRefusedError: [Errno 111] Connection refused" here if first message was processed successfully
            pass
        time.sleep(0.1)
        try:
            data_sock.send(payload_bytes)
        except:
            # probable "ConnectionRefusedError: [Errno 111] Connection refused" here if first message was processed successfully
            pass

    util.done_with_socket(data_sock)

    if args.verbosity:
        print("data sender: end of process", flush=True)
