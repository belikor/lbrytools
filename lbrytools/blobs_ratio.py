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
Estimate the blob seeding ratio (upload/download) from the log files.

Based on: @BrendonBrewer:3/ratio:0

The number of blobs uploaded or downloaded is estimated from the number
of times that the words `'sent'` and `'downloaded'` are found
in the log files of `lbrynet`, normally under `~/.local/share/lbry/lbrynet`.

If Numpy and Matplotlib are available it will create a histogram
of activity of blobs per hour versus the day they were accessed
counting back from today.
"""
import datetime as dt
import os
import requests
import sys
import time

try:
    import numpy as np
    import matplotlib.backends.backend_tkagg as mbacks
    import matplotlib.pyplot as plt
    PLOTTING = True
except ModuleNotFoundError as err:
    print(err)
    PLOTTING = False


def server_exists(server="http://localhost:5279"):
    """Return True if the server is up, and False if not."""
    try:
        requests.post(server)
    except requests.exceptions.ConnectionError:
        print(f"Cannot establish connection to 'lbrynet' on {server}")
        print("Start server with:")
        print("  lbrynet start")
        return False
    return True


def get_data_dir(server="http://localhost:5279"):
    """Return the directory where LBRY stores its data."""
    msg = {"method": "settings_get"}
    out_set = requests.post(server, json=msg).json()
    data_dir = out_set["result"]["data_dir"]
    return data_dir


def count_updown_blobs(filename):
    """Count the uploaded and downloaded blobs from the log filename."""
    now = time.time()
    blobs_up = 0
    blobs_down = 0
    up_times = []
    down_times = []
    up_times_days = []
    down_times_days = []

    if not os.path.exists(filename):
        return {"log_file": filename,
                "blobs_up": blobs_up,
                "blobs_down": blobs_down,
                "up_times": up_times,
                "down_times": down_times,
                "now": now,
                "up_times_days": up_times_days,
                "down_times_days": down_times_days}

    sec_per_day = 86400.0

    with open(filename, "r") as fd:
        lines = fd.readlines()

        for line in lines:
            if "lbry.blob_exchange.server:" in line and "sent" in line:
                blobs_up += 1
                parts = line.split(" ")
                isoformat = (parts[0] + " " + parts[1]).replace(",", ".")
                utime = dt.datetime.fromisoformat(isoformat)
                up_times.append(utime)

                # Days from today to when the blob was uploaded (negative)
                utime_d = (utime.timestamp() - now)/sec_per_day
                up_times_days.append(utime_d)

            if "lbry.blob_exchange.client:" in line and "downloaded" in line:
                blobs_down += 1
                parts = line.split(" ")
                isoformat = (parts[0] + " " + parts[1]).replace(",", ".")
                dtime = dt.datetime.fromisoformat(isoformat)
                down_times.append(dtime)

                # Days from today to when the blob was downloaded (negative)
                dtime_d = (dtime.timestamp() - now)/sec_per_day
                down_times_days.append(dtime_d)

    return {"log_file": filename,
            "blobs_up": blobs_up,
            "blobs_down": blobs_down,
            "up_times": up_times,
            "down_times": down_times,
            "now": now,
            "up_times_days": up_times_days,
            "down_times_days": down_times_days}


def plot_histogram(up_times_days, down_times_days, now=0.0,
                   tk_frame=None):
    """Plot the histogram of the uploaded and downloaded blobs.

    The Y is the number of blobs uploaded or downloaded in a single hour.
    The X is the fraction of day (hour) when those blobs were uploaded.

    The days are negative because it assumes the blobs were downloaded
    in the past, meaning all values to the left correspond to days
    before the present time.

    Parameters
    ----------
    up_times_days: list of float
        List of intervals in days from now to the past, when blobs
        were uploaded, `[-40, -30, -10, -5.235, -0.001]`.
        It is negative because these occurrences were in the past,
        that is, 40 days ago, 30 days ago, 10 days ago, etc.
    down_times_days: list of float
        List of intervals in days from now to the past, when blobs
        were downloaded.
    now: float, optional
        It defaults to `0.0`, in which case it calculates the time
        in this instance, `time.time()`.
        It is a float indicating the Unix epoch time, meaning seconds
        since 1970-01-01.
        This value represent the reference time for all values
        in `up_times_days` and `down_times_days`.
    """
    if not now:
        now = time.time()
    now_txt = time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                            time.localtime(now))

    up_times_d = np.array(up_times_days)
    down_times_d = np.array(down_times_days)

    oldest_day = np.min(np.hstack([up_times_d, down_times_d]))

    # The bins for the histograms will be the fractions of day
    # representing hours of the day
    days_per_hour = 1/24

    fractions_day = [0.0]

    while fractions_day[-1] > oldest_day:
        fractions_day.append(fractions_day[-1] - days_per_hour)

    # More negative values left and zero to the right
    fractions_day = fractions_day[::-1]

    blobs_up = len(up_times_d)
    blobs_down = len(down_times_d)
    ratio = 0.0
    try:
        ratio = float(blobs_up)/blobs_down
    except ZeroDivisionError:
        pass

    xlabel = "Time (days ago)"
    ylabel = "Blobs per hour"
    opt = {"alpha": 0.9, "edgecolor": "k"}

    X0 = Y0 = [0]
    mk = {"label": now_txt,
          "marker": "o", "markeredgecolor": "k", "markersize": 9,
          "markeredgewidth": 2.0, "linestyle": ""}

    fig, axs = plt.subplots(2, 1, sharey=False, sharex=True)

    axs[0].hist(up_times_d, bins=fractions_day,
                color="g", label=f"Uploaded: {blobs_up}", **opt)
    axs[0].set_xlabel(xlabel)
    axs[0].set_ylabel(ylabel)
    axs[0].plot(X0, Y0, markerfacecolor="g", **mk)
    axs[0].legend()
    axs[0].set_title(f"Up/down ratio: {ratio:.4f}")

    axs[1].hist(down_times_d, bins=fractions_day,
                color="r", label=f"Downloaded: {blobs_down}", **opt)
    axs[1].set_xlabel(xlabel)
    axs[1].set_ylabel(ylabel)
    axs[1].plot(X0, Y0, markerfacecolor="r", **mk)
    axs[1].legend()

    if tk_frame:
        canvas = mbacks.FigureCanvasTkAgg(fig, master=tk_frame)
        canvas.draw()
        # canvas.get_tk_widget().grid(row=0, column=0)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        tbar = mbacks.NavigationToolbar2Tk(canvas, tk_frame)
        tbar.update()
        # canvas.get_tk_widget().grid(row=1, column=0)
        canvas.get_tk_widget().pack(fill="both", expand=True)
    else:
        plt.show()


def print_blobs_ratio(data_dir=None, plot_hst=True,
                      file=None, fdate=False, sep=";", tk_frame=None,
                      server="http://localhost:5279"):
    """Estimate the number of blobs uploaded and downloaded from the logs.

    Parse the log files in `data_dir` to find references
    to `lbry.blob.exchange` to see when blobs have been `sent` (uploaded)
    or `downloaded`.

    data_dir: str, optional
        It defaults to `None`, in which case the `data_dir` is taken
        from the saved `lbrynet` settings.
        If it is given it must be the parent directory where the `lbrynet.log`
        files are located.
    plot_hst: bool, optional
        It defaults to `True`, in which case it will try plotting
        histograms of the blob activity in the past days. It assumes Numpy
        and Matplotlib are available.
        If it is `False` it won't create any plot.
    file: str, optional
        It defaults to `None`.
        It must be a writable path to which the summary will be written.
        Otherwise the summary will be printed to the terminal.
    fdate: bool, optional
        It defaults to `False`.
        If it is `True` it will add the date to the name of the summary file.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        It returns the list of dictionaries representing the information
        read from each log file.
        The keys are:
            - 'log_file': log file successfully read
            - 'blobs_up': number of blobs uploaded
            - 'blobs_down': number of blobs downloaded
            - 'up_times': list of `datetime.datetimes` with all times
              the blobs where uploaded
            - 'down_times': list of `datetime.datetimes` with all times
              the blobs where downloaded
            - 'now': reference time for up_times_days and down_times_days"
            - 'up_times_days': list of floats representing the days
              from the current time to the day a blob was uploaded
            - 'down_times_days': list of floats representing the days
              from the current time to the day a blob was downloaded
    False
        If there is a problem it will return `False`.
    """
    # if not server_exists(server=server):
    #     return 1
    data_dir = data_dir or get_data_dir(server=server)

    if not data_dir:
        return False

    print("Estimate the blob upload/download ratio from the logs")
    print(80 * "-")
    print(f"data_dir: {data_dir}")

    blobs_up = 0
    blobs_down = 0

    up_times = []
    down_times = []
    up_times_days = []
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

        estimation = count_updown_blobs(filename)
        blobs_up += estimation["blobs_up"]
        blobs_down += estimation["blobs_down"]
        up_times.extend(estimation["up_times"])
        down_times.extend(estimation["down_times"])
        up_times_days.extend(estimation["up_times_days"])
        down_times_days.extend(estimation["down_times_days"])
        success = True
        estimations.append(estimation)

    out = f"Success: {success}"

    if not success:
        print(out)
        return False

    out = []
    out.append(f"Uploaded blobs: {blobs_up}")
    out.append(f"Downloaded blobs: {blobs_down}")

    ratio = 0.0
    try:
        ratio = float(blobs_up)/blobs_down
    except ZeroDivisionError:
        pass

    out.append(f"Up/down ratio: {ratio:8.4f}")
    now = time.time()
    out.append("Now: " + time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                                       time.localtime(now)))

    max_utime = 0
    min_utime = 0
    max_dtime = 0
    min_dtime = 0

    if len(up_times_days) > 0:
        max_utime = max(up_times_days)
        min_utime = min(up_times_days)

    if len(down_times_days) > 0:
        max_dtime = max(down_times_days)
        min_dtime = min(down_times_days)

    out.append(f"Newest uploaded blob: {max_utime:7.2f} days ago")
    out.append(f"Oldest uploaded blob: {min_utime:7.2f} days ago")
    out.append(f"Newest downloaded blob: {max_dtime:7.2f} days ago")
    out.append(f"Oldest downloaded blob: {min_dtime:7.2f} days ago")

    out.append(40 * "-")
    for estimation in estimations:
        _name = os.path.basename(estimation["log_file"]) + sep
        _blobs_up = estimation["blobs_up"]
        _blobs_down = estimation["blobs_down"]
        ratio = 0.0
        try:
            ratio = float(_blobs_up)/_blobs_down
        except ZeroDivisionError:
            pass

        _now = time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                             time.localtime(estimation["now"]))
        _max_utime = 0
        _min_utime = 0
        _max_dtime = 0
        _min_dtime = 0

        if len(estimation["up_times_days"]) > 0:
            _max_utime = max(estimation["up_times_days"])
            _min_utime = min(estimation["up_times_days"])

        if len(estimation["down_times_days"]) > 0:
            _max_dtime = max(estimation["down_times_days"])
            _min_dtime = min(estimation["down_times_days"])

        out.append(f"{_name:15s} "
                   f"up: {_blobs_up:6d}" + f"{sep} "
                   f"down: {_blobs_down:6d}" + f"{sep} "
                   f"ratio: {ratio:8.4f}" + f"{sep} "
                   f"up new: {_max_utime:7.2f}" + f"{sep} "
                   f"up old: {_min_utime:7.2f}" + f"{sep} "
                   f"down new: {_max_dtime:7.2f}" + f"{sep} "
                   f"down old: {_min_dtime:7.2f}" + f"{sep} "
                   f"{_now}")

    if not PLOTTING:
        print("Numpy and Matplotlib not available; no plot generated")

    fd = 0

    if file:
        dirn = os.path.dirname(file)
        base = os.path.basename(file)

        if fdate:
            fdate = time.strftime("%Y%m%d_%H%M", time.localtime()) + "_"
        else:
            fdate = ""

        file = os.path.join(dirn, fdate + base)

        try:
            fd = open(file, "w")
        except (FileNotFoundError, PermissionError) as err:
            print(f"Cannot open file for writing; {err}")

    if file and fd:
        print("\n".join(out), file=fd)
        fd.close()
        print(f"Summary written: {file}")
    else:
        print("\n".join(out))

    if plot_hst and PLOTTING:
        plot_histogram(up_times_days, down_times_days, now=now,
                       tk_frame=tk_frame)

    return estimations


if __name__ == "__main__":
    if len(sys.argv) > 2:
        data_dir = sys.argv[1]
        server = sys.argv[2]
        print_blobs_ratio(data_dir=data_dir, server=server)
    elif len(sys.argv) == 2:
        data_dir = sys.argv[1]
        print_blobs_ratio(data_dir=data_dir)
    else:
        print_blobs_ratio()
