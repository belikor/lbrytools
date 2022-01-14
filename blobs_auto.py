#!/usr/bin/env python3
# --------------------------------------------------------------------------- #
# The MIT License (MIT)                                                       #
#                                                                             #
# Copyright (c) 2021 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de>       #
#                                                                             #
# Permission is hereby granted, free of charge, to any person obtaining       #
# a copy of this software and associated documentation files                  #
# (the "Software"), to deal in the Software without restriction, including    #
# without limitation the rights to use, copy, modify, merge, publish,         #
# distribute, sublicense, and/or sell copies of the Software, and to permit   #
# persons to whom the Software is furnished to do so, subject to the          #
# following conditions:                                                       #
#                                                                             #
# The above copyright notice and this permission notice shall be included     #
# in all copies or substantial portions of the Software.                      #
#                                                                             #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
# DEALINGS IN THE SOFTWARE.                                                   #
# --------------------------------------------------------------------------- #
"""
Count the claims automatically downloaded by the lbrynet daemon.

These blobs are downloaded to help with seeding in the LBRY network.
This is controlled by a parameter in the daemon settings.

The blobs downloaded are estimated from the number
of times that the words `'sent'` and `'downloaded'` are found
in the log files of `lbrynet`, normally under `~/.local/share/lbry/lbrynet`.
"""
import datetime as dt
import os
import time

import lbrytools.funcs as funcs
import lbrytools.sort as sort


def count_auto_blobs(filename):
    """Count the automatically downloaded blobs from the log filename."""
    now = time.time()
    blobs_down = 0
    sd_blobs = []
    down_times = []
    down_times_days = []

    if not os.path.exists(filename):
        return {"log_file": filename,
                "blobs_down": blobs_down,
                "down_times": down_times,
                "now": now,
                "down_times_days": down_times_days}

    sec_per_day = 86400.0

    with open(filename, "r") as fd:
        lines = fd.readlines()

        for line in lines:
            if ("lbry.stream.downloader:" in line
                    and "downloaded sd blob" in line):
                blobs_down += 1
                parts = line.split(" ")
                isoformat = (parts[0] + " " + parts[1]).replace(",", ".")
                dtime = dt.datetime.fromisoformat(isoformat)
                down_times.append(dtime)

                # Days from today to when the blob was downloaded (negative)
                dtime_d = (dtime.timestamp() - now)/sec_per_day
                down_times_days.append(dtime_d)
                sd_blobs.append(parts[-1].strip())

    return {"log_file": filename,
            "blobs_down": blobs_down,
            "sd_blobs": sd_blobs,
            "down_times": down_times,
            "now": now,
            "down_times_days": down_times_days}


def print_network_sd_blobs(data_dir=None,
                           print_blobs=True,
                           file=None, fdate=False, sep=";",
                           server="http://localhost:5279"):
    """Print the downloaded blobs from the logs."""
    data_dir = data_dir or funcs.get_data_dir(server=server)

    if not data_dir:
        return False

    print("Estimate the automatically downloaded claims from the logs")
    print(80 * "-")
    print(f"data_dir: {data_dir}")

    blobs_down = 0

    down_times = []
    down_times_days = []

    success = False

    estimations = []
    log_files = ["lbrynet.log"]
    log_files += [f"lbrynet.log.{i}" for i in range(1, 10)]

    for log_file in log_files:
        filename = os.path.join(data_dir, log_file)
        if os.path.exists(filename):
            print(filename)
        else:
            print(f"{filename}, does not exist")
            continue

        estimation = count_auto_blobs(filename)
        blobs_down += estimation["blobs_down"]
        down_times.extend(estimation["down_times"])
        down_times_days.extend(estimation["down_times_days"])
        success = True
        estimations.append(estimation)

    out = f"Success: {success}"

    if not success:
        print(out)
        return False

    out = []
    out.append(f"Downloaded sd_blobs: {blobs_down}")

    now = time.time()
    out.append("Now: " + time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                                       time.localtime(now)))

    max_dtime = 0
    min_dtime = 0

    if len(down_times_days) > 0:
        max_dtime = max(down_times_days)
        min_dtime = min(down_times_days)

    out.append(f"Newest downloaded blob: {max_dtime:7.2f} days ago")
    out.append(f"Oldest downloaded blob: {min_dtime:7.2f} days ago")

    all_sd_blobs = []

    out.append(40 * "-")
    for estimation in estimations:
        all_sd_blobs.extend(estimation["sd_blobs"])
        _name = os.path.basename(estimation["log_file"]) + sep
        _blobs_down = estimation["blobs_down"]

        _now = time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                             time.localtime(estimation["now"]))
        _max_dtime = 0
        _min_dtime = 0

        if len(estimation["down_times_days"]) > 0:
            _max_dtime = max(estimation["down_times_days"])
            _min_dtime = min(estimation["down_times_days"])

        out.append(f"{_name:15s} "
                   f"down: {_blobs_down:5d}" + f"{sep} "
                   f"down new: {_max_dtime:7.2f}" + f"{sep} "
                   f"down old: {_min_dtime:7.2f}" + f"{sep} "
                   f"{_now}")

    funcs.print_content(out, file=file, fdate=fdate)

    if print_blobs:
        for num, blob in enumerate(all_sd_blobs, start=1):
            print(f"{num:4d}/{blobs_down:4d}: "
                  f"{blob}")

    return estimations


def sd_blobs_compared(print_blobs=True,
                      server="http://localhost:5279"):
    """Find the blobs estimated that we have already donwloaded."""
    items = sort.sort_items(server=server)
    print()
    estimates = print_network_sd_blobs(print_blobs=False,
                                       server=server)
    print()

    print("These are sd_hashes from the logs that are already downloaded")
    print(80 * "-")

    all_sd_blobs = []
    for est in estimates:
        all_sd_blobs.extend(est["sd_blobs"])

    exist = []
    for num, blob in enumerate(all_sd_blobs, start=1):
        for claim in items:
            if blob in claim["sd_hash"] and claim not in exist:
                exist.append(claim)
                print(f"{num:4d}; {blob}; {claim['claim_name']}")

    return exist
