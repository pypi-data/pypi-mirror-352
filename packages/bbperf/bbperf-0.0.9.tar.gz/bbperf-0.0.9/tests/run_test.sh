#!/bin/bash

# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

SERVER_ADDR=127.0.0.1

EXTRAARGS="-t 10"

set -x

bbperf -c $SERVER_ADDR $EXTRAARGS

bbperf -c $SERVER_ADDR $EXTRAARGS -R

bbperf -c $SERVER_ADDR $EXTRAARGS -u

bbperf -c $SERVER_ADDR $EXTRAARGS -u -R

bbperf -c $SERVER_ADDR $EXTRAARGS -J /tmp/foo578439759837.out
set -x
cat /tmp/foo578439759837.out
rm /tmp/foo578439759837.out

