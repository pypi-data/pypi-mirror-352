# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

import time

from . import const

class DataSampleEvaluatorClass:

    # args are client args
    def __init__(self, args0):
        self.args = args0
        self.valid_flag = False

    # once a sample is valid then all subsequent samples are valid
    def is_sample_valid(self, run_mode_running_start_time, dropped_this_interval_percent, sender_throughput_rate_mbps, receiver_throughput_rate_mbps):
        if self.valid_flag:
            return True

        # samples are never valid until we have passed the "ignore time"
        if time.time() < (run_mode_running_start_time + const.DATA_SAMPLE_IGNORE_TIME_SEC):
            return False

        throughput_rate_ratio = abs(sender_throughput_rate_mbps - receiver_throughput_rate_mbps) / receiver_throughput_rate_mbps

        # udp
        if self.args.udp and (dropped_this_interval_percent > 0):
            self.valid_flag = True
            return True

        # tcp
        if (not self.args.udp) and (throughput_rate_ratio < 0.01) and (receiver_throughput_rate_mbps > 1.0):
            self.valid_flag = True
            return True

        return False

