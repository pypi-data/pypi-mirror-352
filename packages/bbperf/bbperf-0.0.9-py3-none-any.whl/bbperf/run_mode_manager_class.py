# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

import time

from . import const

from .data_sample_evaluator_class import DataSampleEvaluatorClass

class RunModeManagerClass:

    # args are client args
    def __init__(self, args0, shared_run_mode0):
        self.args = args0
        self.shared_run_mode = shared_run_mode0

        self.job_start_time = None
        self.run_mode_running_start_time = None
        self.min_rtt_ms = None
        self.last_10_rtt_list = []
        self.num_good_samples = 0
        self.total_dropped_as_of_last_interval = 0
        self.data_sample_evaluator = DataSampleEvaluatorClass(self.args)


    # updates shared_run_mode and r_record["is_sample_valid"]
    def update(self, r_record):
        curr_time = time.time()

        # first record
        if self.job_start_time is None:
            self.job_start_time = curr_time

        curr_rtt_ms = r_record["rtt_ms"]

        # update unloaded latency?
        if r_record["r_record_type"] == "cal":
            if (self.min_rtt_ms is None) or (curr_rtt_ms < self.min_rtt_ms):
                self.min_rtt_ms = curr_rtt_ms

        # CALIBRATING
        if self.shared_run_mode.value == const.RUN_MODE_CALIBRATING:

            # check to see if we should leave calibration
            self.last_10_rtt_list.append(curr_rtt_ms)
            if len(self.last_10_rtt_list) > 10:
                self.last_10_rtt_list = self.last_10_rtt_list[1:11]

            # are we done calibrating?
            # because either end early or hit max calibration time
            if ((min(self.last_10_rtt_list) > self.min_rtt_ms) or
                (curr_time > self.job_start_time + const.MAX_DURATION_CALIBRATION_TIME_SEC)):

                self.shared_run_mode.value = const.RUN_MODE_RUNNING
                self.run_mode_running_start_time = curr_time

            return

        # run mode is RUNNING or STOP

        # have we reached max time for data run without getting any valid data samples?
        if ((self.num_good_samples == 0) and (curr_time > (self.run_mode_running_start_time + const.MAX_DATA_COLLECTION_TIME_WITHOUT_VALID_DATA))):
            self.shared_run_mode.value = const.RUN_MODE_STOP

        # check to see if we should stop RUNNING

        if self.args.udp:
            dropped_this_interval = r_record["total_dropped"] - self.total_dropped_as_of_last_interval
            if dropped_this_interval < 0:
                dropped_this_interval = 0
            dropped_this_interval_percent = (dropped_this_interval * 100.0) / r_record["r_sender_interval_pkts_sent"]
            # remember this for next loop:
            self.total_dropped_as_of_last_interval = r_record["total_dropped"]
        else:
            dropped_this_interval = -1
            dropped_this_interval_percent = -1

        r_record["interval_dropped"] = dropped_this_interval
        r_record["interval_dropped_percent"] = dropped_this_interval_percent

        # how many good samples do we have?
        if self.data_sample_evaluator.is_sample_valid(
                self.run_mode_running_start_time,
                dropped_this_interval_percent,
                r_record["sender_interval_rate_mbps"],
                r_record["receiver_interval_rate_mbps"]):

            r_record["is_sample_valid"] = 1
            self.num_good_samples += 1
        else:
            r_record["is_sample_valid"] = 0

        # num samples is 10x because we collect every 0.1 seconds
        if self.num_good_samples > (self.args.time * 10):
            self.shared_run_mode.value = const.RUN_MODE_STOP

