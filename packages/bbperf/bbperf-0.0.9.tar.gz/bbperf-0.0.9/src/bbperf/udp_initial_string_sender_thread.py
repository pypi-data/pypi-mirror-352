# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

import time

from . import udp_helper


# falling off the end of this method terminates the process
def run(args, data_sock, data_initial_string, shared_initial_string_done):
    if args.verbosity:
        print("udp initial string sender thread: start of process", flush=True)

    ping_interval_sec = 0.2
    ping_duration_sec = 5
    total_pings_to_send = ping_duration_sec / ping_interval_sec

    send_count = 0

    while True:
        if shared_initial_string_done.value == 1:
            break

        udp_helper.send_string(args, data_sock, data_initial_string)
        send_count += 1

        time.sleep(ping_interval_sec)

        if send_count > total_pings_to_send:
            break

    if args.verbosity:
        print("udp initial string sender thread: end of process", flush=True)
