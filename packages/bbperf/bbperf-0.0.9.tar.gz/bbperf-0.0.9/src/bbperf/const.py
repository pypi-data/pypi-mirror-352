# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

SERVER_PORT = 5301

DEFAULT_VALID_DATA_COLLECTION_TIME_SEC = 20

# max duration for calibration phase
MAX_DURATION_CALIBRATION_TIME_SEC = 20

# cap the amount of time we will wait for valid data
MAX_DATA_COLLECTION_TIME_WITHOUT_VALID_DATA = 60

# ignore incoming data for this amount of time after starting data collection phase
DATA_SAMPLE_IGNORE_TIME_SEC = 1

# for socket recv()
BUFSZ = 4096

PAYLOAD_1K = b'a'*1024
PAYLOAD_4K = b'a'*4096

RUN_MODE_CALIBRATING = 1
RUN_MODE_RUNNING = 2
RUN_MODE_STOP = 3

SAMPLE_INTERVAL_SEC = 0.1
STDOUT_INTERVAL_SEC = 1

RATE_LIMITED_BATCH_SIZE_PKTS_UDP_PKTS = 20
RATE_LIMITED_BATCH_SIZE_PKTS_TCP_PKTS = 5

SETUP_COMPLETE_MSG = "setup complete"
START_MSG = " start "
UDP_STOP_MSG = "stop"

SOCKET_TIMEOUT_SEC=20

UDP_DEFAULT_INITIAL_RATE = 8000

UDP_MIN_RATE = 100
UDP_MAX_RATE = 800000
