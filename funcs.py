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
"""Auxiliary functions for other methods of the lbrytools package."""
import os
import random
import regex
import requests
import subprocess
import time

try:
    import emoji
    EMOJI_LOADED = True
except ModuleNotFoundError:
    EMOJI_LOADED = False

TFMT = "%Y-%m-%d_%H:%M:%S%z %A"
TFMTp = "%Y-%m-%d_%H:%M:%S%z"
TFMTf = "%Y%m%d_%H%M"


def start_lbry():
    """Launch the lbrynet client through subprocess."""
    subprocess.run(["lbrynet", "start"], stdout=subprocess.DEVNULL)


def check_lbry(server="http://localhost:5279"):
    """Check if the LBRY daemon is running, and launch it if it's not.

    Send a `'status'` request to the server `'http://localhost:5279'`,
    and check for `'is_running'` being `True`.

    Start the service if it is not running.
    ::
        lbrynet start

    Other functions that need to call `lbrynet` should call this method
    before doing other things.

    Parameters
    ----------
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        It returns `True` if the LBRY daemon is already running.
        It returns `False` if the LBRY daemon was not running
        but it was started manually.
    """
    msg = {"method": "status"}
    try:
        output = requests.post(server, json=msg).json()
    except requests.exceptions.ConnectionError as err:
        # Trap all with requests.exceptions.RequestException
        print(err)
        start_lbry()
        return False

    if "result" not in output:
        print(">>> No 'result' in the JSON-RPC server output")
        start_lbry()
        return False

    if "is_running" in output["result"] and output["result"]["is_running"]:
        return True

    start_lbry()
    return False

    # Only really works in Linux
    # try:
    #     subprocess.run(["pidof", "lbrynet"], stdout=subprocess.DEVNULL)
    #     return True
    # except subprocess.CalledProcessError:
    #     start_lbry()
    #     return False


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
    msg = {"method": "settings_get",
           "params": {}}

    output = requests.post(server, json=msg).json()
    data_dir = output["result"]["data_dir"]
    return data_dir


def get_bdir(server="http://localhost:5279"):
    """Return the directory where LBRY stores the blob files."""
    msg = {"method": "settings_get",
           "params": {}}

    output = requests.post(server, json=msg).json()
    datadir = output["result"]["data_dir"]
    blobdir = os.path.join(datadir, "blobfiles")
    return blobdir


def default_ddir(server="http://localhost:5279"):
    """Get the default download directory for lbrynet."""
    if not server_exists(server=server):
        return os.path.expanduser("~")

    msg = {"method": "settings_get"}
    out_set = requests.post(server, json=msg).json()
    ddir = out_set["result"]["download_dir"]
    return ddir


def get_download_dir(ddir=None,
                     server="http://localhost:5279"):
    """Get the entered directory if it exists, or the default directory."""
    old_ddir = str(ddir)

    if not ddir or not os.path.exists(ddir):
        ddir = default_ddir(server=server)
        print(f"Directory does not exist: {old_ddir}")
        print(f"Default directory: {ddir}")

    return ddir


def print_content(output_list, file=None, fdate=False):
    """Print contents to the terminal or to a file."""
    fd = 0

    if file:
        dirn = os.path.dirname(file)
        base = os.path.basename(file)

        if fdate:
            fdate = time.strftime(TFMTf, time.gmtime()) + "_"
        else:
            fdate = ""

        file = os.path.join(dirn, fdate + base)

        try:
            fd = open(file, "w")
        except (FileNotFoundError, PermissionError) as err:
            print(f"Cannot open file for writing; {err}")

    content = "\n".join(output_list)

    if file and fd:
        print(content, file=fd)
        fd.close()
        print(f"Summary written: {file}")
    else:
        print(content)

    return content


def sanitize_text(text="random_string"):
    """Sanitize text with complex unicode characters.

    Some names have complex unicode characters, especially emojis.
    With this method we remove these `grapheme clusters` so that applications
    that receive the string don't cause an error.

    Many terminals and interface toolkits are able to display the emojis
    without problem but others such as Tkinter Text widgets
    may crash when trying to display such symbols.
    """
    # This will find unicode country flags, which are actually composed
    # of two or more characters together, like 'U' 'S' is the US flag,
    # and 'F' 'R' is the France flag.
    flags = regex.findall(u'[\U0001F1E6-\U0001F1FF]', text)

    text_normalized = ""

    # Only remove the emojis if we have the `emoji` package loaded
    if EMOJI_LOADED:
        emoji_dict = emoji.UNICODE_EMOJI['en']
    else:
        emoji_dict = ""

    for character in text:
        if character in emoji_dict or character in flags:
            text_normalized += "\u275A"  # monospace black box
        else:
            text_normalized += character

    return text_normalized


def process_ch_num(channels=None,
                   number=None, shuffle=True):
    """Process the channels which are contained in a list.

    It returns a properly formatted list of pairs.

    Parameters
    ----------
    channels: list of elements
        Each element of the `channels` list may be a string,
        a list with a single element, or a list with two elements.

        For example, given
        ::
            ch1 = "Channel"
            ch2 = ["@Ch1"]
            ch3 = ["Mychan", 2]

        A valid input is
        ::
            channels = [ch1, ch2, ch3]
            channels = ["Channel", ["@Ch1"], ["MyChan", 2]]
    number: int, optional
        It defaults to `None`.
        If this is present, it will override the individual
        numbers in `channels`.
    shuffle: bool, optional
        It defaults to `True`, in which case it will shuffle
        the list of channels so that they are not processed in the order
        that they come.

    Returns
    --------
    list of dict
        It returns a list of dictionaries, where each element corresponds
        to a channel. The two keys are:
            - 'channel', the actual channel name; if the input is invalid,
              this will be set to `None`.
            - 'number', the number of items from this channel;
              if the input is invalid this value will be set to 0.
    False
        If there is a problem such as an empty input it will return `False`.
    """
    if isinstance(channels, str):
        channels = [channels]

    if not channels or not isinstance(channels, (list, tuple)):
        m = ["Specify channels and a number of claims.",
             "  [",
             "    ['@MyChannel', 2],",
             "    ['@AwesomeCh:8', 1],",
             "    ['@A-B-C#a', 3]",
             "  ]"]
        print("\n".join(m))
        print(f"channels={channels}")
        return False

    DEFAULT_NUM = 2

    if number:
        if not isinstance(number, int) or number < 0:
            number = DEFAULT_NUM
            print("Number must be a positive integer, "
                  f"set to default value, number={number}")

        print("Global value overrides per channel number, "
              f"number={number}")

    n_channels = len(channels)

    if n_channels <= 0:
        print(">>> No channels in the list")
        return False

    out_ch_info = []

    if shuffle:
        if isinstance(channels, tuple):
            channels = list(channels)
        random.shuffle(channels)
        random.shuffle(channels)

    for num, channel in enumerate(channels, start=1):
        ch_info = {"channel": None,
                   "number": 0}

        if isinstance(channel, str):
            c_number = DEFAULT_NUM
        elif isinstance(channel, (list, tuple)):
            if len(channel) < 2:
                c_number = DEFAULT_NUM
            else:
                c_number = channel[1]

                if not isinstance(c_number, (int, float)) or c_number < 0:
                    print(f">>> Number set to {DEFAULT_NUM}")
                    c_number = DEFAULT_NUM

                c_number = int(c_number)

            channel = channel[0]

        if not isinstance(channel, str):
            print(f"Channel {num}/{n_channels}, {channel}")
            print(">>> Error: channel must be a string. Skip channel.")
            print()
            out_ch_info.append(ch_info)
            continue

        if channel.startswith("[") and channel.endswith("]"):
            # Sometimes we want to have the channel surrounded
            # by brackets `[@channels]` to indicate it is invalid.
            # We just allow the channel as is.
            pass
        elif not channel.startswith("@"):
            channel = "@" + channel

        # Number overrides the individual number for all channels
        if number:
            c_number = number

        ch_info["channel"] = channel
        ch_info["number"] = c_number
        out_ch_info.append(ch_info)

    return out_ch_info
