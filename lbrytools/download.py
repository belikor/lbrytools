#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2021 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
# ----------------------------------------------------------------------------
"""Functions to help with downloading content from the LBRY network."""
import json
import os
import random
import subprocess
import sys

from lbrytools.funcs import check_lbry

from lbrytools.search import search_item
from lbrytools.search import ch_search_latest
from lbrytools.search import sort_items
from lbrytools.search import parse_claim_file

from lbrytools.print import print_info_pre_get
from lbrytools.print import print_info_post_get


def lbrynet_get(get_cmd=None):
    """Run the lbrynet get command and return the information that it shows.

    Parameters
    ----------
    get_cmd: list of str
        A list of strings that defines a command to get a claim.
        This list has at least three elements,
        and is passed to the `subprocess.run` method for execution.
        ::
            get_cmd = ['lbrynet', 'get', 'lbry://@asaaa#5/a#b']

    Returns
    -------
    dict
        Returns the dictionary that represents the standard output
        of the get command.
    """
    if not get_cmd:
        print("No input command, using default value.")
        get_cmd = ["lbrynet",
                   "get",
                   "'lbry://@asaaa#5/a#b'"]
        print("Download: " + " ".join(get_cmd))

    check_lbry()
    output = subprocess.run(get_cmd,
                            capture_output=True,
                            check=True,
                            text=True)
    if output.returncode == 1:
        print(f"Error: {output.stderr}")
        sys.exit(1)

    info_get = json.loads(output.stdout)
    return info_get


def download_single(uri=None, cid=None, name=None,
                    ddir=None, own_dir=True):
    """Download a single item and place it in the download directory.

    If `uri`, `cid`, and `name` are provided, `uri` is used.
    If `cid` and `name` are given, `cid` is used.

    This function is also used to resume the download of a partially
    downloaded claim, that is, one that for any reason didn't complete
    the first time.
    It will download the missing blobs in order to produce
    the full media file (mp4, mp3, mkv, etc.).

    If all blobs are already available, then the media file
    will be recreated (if it doesn't already exist) in the download directory.

    Parameters
    ----------
    uri: str
        A unified resource identifier (URI) to a claim on the LBRY network.
        It can be full or partial.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            uri = '@MyChannel#3/some-video-name#2'
            uri = 'some-video-name'

        The URI is also called the `'canonical_url'` of the claim.
    cid: str, optional
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            name = 'some-video-name'
    ddir: str, optional
        It defaults to `$HOME`.
        The path to the download directory.
    own_dir: bool, optional
        It defaults to `True`, in which case it places the downloaded
        content inside a subdirectory named after the channel in `ddir`.

    Returns
    -------
    dict
        Returns the dictionary that represents the standard output
        of the `lbrynet_get` command.
    False
        If there is a problem or non existing claim, it will return `False`.
    """
    if not (uri or cid or name):
        print("Download item by 'URI', 'claim_id', or 'name'.")
        print(f"uri={uri}, cid={cid}, name={name}")
        return False

    if (not ddir or not isinstance(ddir, str)
            or ddir == "~" or not os.path.exists(ddir)):
        ddir = os.path.expanduser("~")
        print(f"Download directory should exist; set to ddir='{ddir}'")

    # It also checks if it's a reposted claim
    item = search_item(uri=uri, cid=cid, name=name)
    if not item:
        print(f"uri={uri}, cid={cid}, name={name}")
        return False

    uri = item["canonical_url"]

    if "name" in item["signing_channel"]:
        channel = item["signing_channel"]["name"]
    else:
        channel = "@_Unknown_"

    # claim_id = item["claim_id"]

    get_cmd = ["lbrynet",
               "get",
               uri]

    # This is just to print the command that can be used on the terminal.
    # The URI is surrounded by single or double quotes.
    if "'" in get_cmd[2]:
        get_cmd2 = ["lbrynet",
                    "get",
                    '"' + get_cmd[2] + '"']
    else:
        get_cmd2 = ["lbrynet",
                    "get",
                    "'" + get_cmd[2] + "'"]

    # At the moment we cannot download a claim by `'claim_id'` directly.
    # Hopefully in the future `lbrynet` will be extended in this way.
    # get_cmd_id = ["lbrynet",
    #               "get",
    #               "--claim_id=" + claim_id]

    subdir = os.path.join(ddir, channel)
    if own_dir:
        if not os.path.exists(subdir):
            try:
                os.mkdir(subdir)
            except (FileNotFoundError, PermissionError) as err:
                print(f"Cannot open directory for writing; {err}")
                return False
        ddir = subdir

    get_cmd.append("--download_directory=" + ddir)
    get_cmd2.append("--download_directory=" + "'" + ddir + "'")

    print("Download: " + " ".join(get_cmd2))
    print_info_pre_get(item)

    info_get = lbrynet_get(get_cmd)

    if not info_get:
        print(">>> Error: empty information from `lbrynet get`")
        return False

    print_info_post_get(info_get)

    return info_get


def ch_download_latest(channel=None, number=2,
                       ddir=None, own_dir=True):
    """Download the latest claims published by a specific channel.

    Parameters
    ----------
    channel: str
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    number: int, optional
        It defaults to 2.
        The number of items to download that were last posted by `channel`.
    ddir: str, optional
        It defaults to `$HOME`.
        The path to the download directory.
    own_dir: bool, optional
        It defaults to `True`, in which case it places the downloaded
        content inside a subdirectory named after the channel in `ddir`.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary represents
        the standard output of the `lbrynet_get` command for each
        downloaded claim.
    False
        If there is a problem, or no existing channel,
        it will return `False`.
    """
    if not channel or not isinstance(channel, str):
        print("Download items from a single channel.")
        print(f"channel={channel}")
        return False

    if not number or not isinstance(number, int) or number < 0:
        number = 2
        print("Number must be a positive integer, "
              f"set to default value, number={number}")

    if (not ddir or not isinstance(ddir, str)
            or ddir == "~" or not os.path.exists(ddir)):
        ddir = os.path.expanduser("~")
        print(f"Download directory should exist; set to ddir='{ddir}'")

    list_info_get = []
    items = ch_search_latest(channel=channel, number=number)

    if not items:
        print()
        return False

    n_items = len(items)

    for it, item in enumerate(items, start=1):
        print(f"Item {it}/{n_items}")

        info_get = download_single(uri=item["canonical_url"],
                                   ddir=ddir, own_dir=True)
        list_info_get.append(info_get)
        print()

    return list_info_get


def ch_download_latest_multi(channels=None, ddir=None, own_dir=True,
                             number=None):
    """Download the latest claims published by a list of a channels.

    Parameters
    ----------
    channels: list of lists
        Each element in the list is a list of two elements.
        The first element is a channel's name, full or partial;
        the second element is an integer that indicates the number
        of newest items from that channel that will be downloaded.
        ::
            channels = [
                         ['@MyChannel#5', 3],
                         ['GoodChannel#f', 4],
                         ['Fast_channel', 2]
                       ]
    ddir: str, optional
        It defaults to `$HOME`.
        The path to the download directory.
    own_dir: bool, optional
        It defaults to `True`, in which case it places the downloaded
        content inside a subdirectory named after the channel in `ddir`.
    number: int, optional
        It defaults to `None`.
        If this is present, it will override the individual
        numbers in `channels`.
        That is, the number of claims that will be downloaded
        will be the same for every channel.

    Alternative input
    -----------------
    channels: list of str
        The list of channels can also be specified as a list of strings.
        ::
            channels = [
                         '@MyChannel#5',
                         'GoodChannel#f',
                         'Fast_channel'
                       ]
            number = 4

        In this case `number` must be specified explicitly to control
        the number of claims that will be downloaded for every channel.

    Returns
    -------
    list of lists of dicts
        A list of lists, where each internal list represents one channel,
        and this internal list has as many dictionaries as downloaded claims.
        The information in each dictionary represents the standard output
        of the `lbrynet_get` command for each downloaded claim.
    False
        If there is a problem, or an empty channel list,
        it will return `False`.
    """
    if not channels or not isinstance(channels, (list, tuple)):
        m = ["Download items from a list of channels and items.",
             "  [",
             "    ['@MyChannel', 2],",
             "    ['@AwesomeCh:8', 1],",
             "    ['@A-B-C#a', 3]",
             "  ]"]
        print("\n".join(m))
        print(f"channels={channels}")
        return False

    if (not ddir or not isinstance(ddir, str)
            or ddir == "~" or not os.path.exists(ddir)):
        ddir = os.path.expanduser("~")
        print(f"Download directory should exist; set to ddir='{ddir}'")

    if number:
        if not isinstance(number, int) or number < 0:
            number = 2
            print("Number must be a positive integer, "
                  f"set to default value, number={number}")

        print("Global value overrides per channel number, "
              f"number={number}")

    n_channels = len(channels)
    list_ch_info = []

    if n_channels <= 0:
        print(">>> No channels in the list")
        return False

    # Each element of the `channels` list may be a string,
    # a list with a single element, or a list with multiple elements (two).
    #     ch1 = "Channel"
    #     ch2 = ["@Ch1"]
    #     ch3 = ["Mychan", 2]
    #     channels = [ch1, ch2, ch3]
    for it, channel in enumerate(channels, start=1):
        ch_info = []
        if isinstance(channel, str):
            _number = 2
        elif isinstance(channel, (list, tuple)):
            if len(channel) < 2:
                _number = 2
            else:
                _number = channel[1]
                if not isinstance(_number, (int, float)):
                    print(">>> Number set to 2")
                    _number = 2
                _number = int(_number)

            channel = channel[0]

        if not isinstance(channel, str):
            print(f"Channel {it}/{n_channels}, {channel}")
            print(">>> Error: channel must be a string. Skip channel.")
            print()
            list_ch_info.append(ch_info)
            continue

        if not channel.startswith("@"):
            channel = "@" + channel

        # Number overrides the individual number for all channels
        if number:
            _number = number

        print(f"Channel {it}/{n_channels}, {channel}")
        ch_info = ch_download_latest(channel=channel, number=_number,
                                     ddir=ddir, own_dir=own_dir)

        list_ch_info.append(ch_info)

    return list_ch_info


def redownload_latest(number=2, ddir=None, own_dir=True, rand=False):
    """Attempt to redownload the latest claims that were already downloaded.
    
    This function is useful to resume the download of partially
    downloaded claims, that is, those that for any reason didn't complete
    the first time.
    It will download the missing blobs in order to produce
    the full media file (mp4, mp3, mkv, etc.).

    If all blobs are already available, then the media files
    will be recreated (if they don't already exist) in the download directory.

    Parameters
    ----------
    number: int, optional
        It defaults to 2.
        The number of items that will be re-downloaded from the list of claims
        which were already downloaded.
        For example, `number=10` will attempt to re-download
        the 10 newest items.
    ddir: str, optional
        It defaults to `$HOME`.
        The path to the download directory.
    own_dir: bool, optional
        It defaults to `True`, in which case it places the downloaded
        content inside a subdirectory named after the channel in `ddir`.
    rand: bool, optional
        It defaults to `False`.
        If it is `True` it will shuffle the list of claims
        so that `number` indicates a random number of claims,
        not only the newest ones.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary represents
        the standard output of the `lbrynet_get` command for each
        re-downloaded claim.
    """
    if not number or not isinstance(number, int) or number < 0:
        number = 2
        print("Number must be a positive integer, "
              f"set to default value, number={number}")

    if (not ddir or not isinstance(ddir, str)
            or ddir == "~" or not os.path.exists(ddir)):
        ddir = os.path.expanduser("~")
        print(f"Download directory should exist; set to ddir='{ddir}'")

    sorted_items = sort_items()
    sorted_items.reverse()

    if rand:
        random.shuffle(sorted_items)
        random.shuffle(sorted_items)
        random.shuffle(sorted_items)

    list_info_get = []

    print(80 * "-")

    for it, item in enumerate(sorted_items, start=1):
        if it > number:
            break
        print(f"Re-download {it}/{number}")

        d = download_single(cid=item["claim_id"], ddir=ddir, own_dir=own_dir)
        list_info_get.append(d)
        print()

    return list_info_get


def redownload_claims(ddir=None, own_dir=True,
                      start=1, end=0, file=None):
    """Try to re-download all claims already downloaded, or from a file.

    Parameters
    ----------
    ddir: str, optional
        It defaults to `$HOME`.
        The path to the download directory.
    own_dir: bool, optional
        It defaults to `True`, in which case it places the downloaded
        content inside a subdirectory named after the channel in `ddir`.
    start: int, optional
        It defaults to 1.
        Operate on the item starting from this index in the internal list
        of claims or in the claims provided by `file`.
    end: int, optional
        It defaults to 0.
        Operate until and including this index in the internal list of claims
        or in the claims provided by `file`.
        If it is 0, it is the same as the last index.
    file: str, optional
        It defaults to `None`.
        The file to read claims from. It is a comma-separated value (CSV)
        list of claims, in which each row represents a claim,
        and one element is the `'claim_id'` which can be used
        with `download_single` to get that claim.

        If `file=None` it will re-download the claims obtained
        from `sort_items` which should already be present in the system
        fully or partially.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary represents
        the standard output of the `lbrynet_get` command for each
        downloaded claim.
    False
        If there is a problem, or no existing file,
        it will return `False`.
    """
    print(80 * "-")

    if not file:
        print("Redownload from existing claims")
        sorted_items = sort_items()

        if not sorted_items:
            print(">>> Error: no claims previously downloaded.")
            return False
    else:
        if file and not isinstance(file, str) or not os.path.exists(file):
            print("The file path must exist.")
            print(f"file={file}")
            return False

        print("Redownload from existing file")
        sorted_items = parse_claim_file(file)
        print()

        if not sorted_items:
            print(">>> Error: the file must have a 'claim_id' "
                  "(40-character alphanumeric string); "
                  "could not parse the file.")
            print(f"file={file}")
            return False

    n_items = len(sorted_items)
    print(80 * "-")
    print(f"Effective claims: {n_items}")

    list_info_get = []

    for it, item in enumerate(sorted_items, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        print("{:4d}/{:4d}".format(it, n_items))
        info_get = download_single(cid=item["claim_id"],
                                   ddir=ddir, own_dir=own_dir)
        list_info_get.append(info_get)
        print()

    return list_info_get
