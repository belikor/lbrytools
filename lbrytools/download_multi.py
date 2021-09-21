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
"""Functions to help with downloading multiple claims from the LBRY network."""
import os
import random

import lbrytools.funcs as funcs
import lbrytools.search as srch
import lbrytools.search_ch as srch_ch
import lbrytools.sort as sort
import lbrytools.download as dld


def ch_download_latest(channel=None, number=2,
                       ddir=None, own_dir=True, save_file=True,
                       server="http://localhost:5279"):
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
    save_file: bool, optional
        It defaults to `True`, in which case all blobs of the stream
        will be downloaded, and the media file (mp4, mp3, mkv, etc.)
        will be placed in the downloaded directory.
        If it is `False` it will only download the first blob (`sd_hash`)
        in the stream, so the file will be in the local database
        but the complete file won't be placed in the download directory.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

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
    if not funcs.server_exists(server=server):
        return False

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
    items = srch_ch.ch_search_latest(channel=channel, number=number,
                                     server=server)
    if not items:
        print()
        return False

    n_items = len(items)

    for it, item in enumerate(items, start=1):
        print(f"Claim {it}/{n_items}")
        info_get = dld.download_single(cid=item["claim_id"],
                                       ddir=ddir, own_dir=own_dir,
                                       save_file=save_file,
                                       server=server)
        list_info_get.append(info_get)
        print()

    return list_info_get


def ch_download_latest_multi(channels=None, ddir=None, own_dir=True,
                             save_file=True, number=None, shuffle=True,
                             server="http://localhost:5279"):
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
    save_file: bool, optional
        It defaults to `True`, in which case all blobs of the stream
        will be downloaded, and the media file (mp4, mp3, mkv, etc.)
        will be placed in the downloaded directory.
        If it is `False` it will only download the first blob (`sd_hash`)
        in the stream, so the file will be in the local database
        but the complete file won't be placed in the download directory.
    number: int, optional
        It defaults to `None`.
        If this is present, it will override the individual
        numbers in `channels`.
        That is, the number of claims that will be downloaded
        will be the same for every channel.
    shuffle: bool, optional
        It defaults to `True`, in which case it will shuffle
        the list of channels so that they are not processed in the order
        that they come.

        If the list is very long the LBRY daemon may stop processing
        the claims, so it may happen that only the first channels
        are processed but not the last ones.
        So by processing the channels in random order, we increase
        the probability of processing all channels by running this function
        multiple times.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

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
    if not funcs.server_exists(server=server):
        return False

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

    list_ch_info = []

    if shuffle:
        if isinstance(channels, tuple):
            channels = list(channels)
        random.shuffle(channels)
        random.shuffle(channels)

    # Each element of the `channels` list may be a string,
    # a list with a single element, or a list with multiple elements (two).
    #     ch1 = "Channel"
    #     ch2 = ["@Ch1"]
    #     ch3 = ["Mychan", 2]
    #     channels = [ch1, ch2, ch3]

    for it, channel in enumerate(channels, start=1):
        ch_info = []
        if isinstance(channel, str):
            _number = DEFAULT_NUM
        elif isinstance(channel, (list, tuple)):
            if len(channel) < 2:
                _number = DEFAULT_NUM
            else:
                _number = channel[1]
                if not isinstance(_number, (int, float)) or _number < 0:
                    print(f">>> Number set to {DEFAULT_NUM}")
                    _number = DEFAULT_NUM
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
                                     ddir=ddir, own_dir=own_dir,
                                     save_file=save_file,
                                     server=server)

        list_ch_info.append(ch_info)

    return list_ch_info


def redownload_latest(number=2, ddir=None, own_dir=True, save_file=True,
                      shuffle=False,
                      server="http://localhost:5279"):
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
    save_file: bool, optional
        It defaults to `True`, in which case all blobs of the stream
        will be downloaded, and the media file (mp4, mp3, mkv, etc.)
        will be placed in the downloaded directory.
        If it is `False` it will only download the first blob (`sd_hash`)
        in the stream, so the file will be in the local database
        but the complete file won't be placed in the download directory.
    shuffle: bool, optional
        It defaults to `False`.
        If it is `True` it will shuffle the list of claims
        so that `number` indicates a random number of claims,
        not only the newest ones.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary represents
        the standard output of the `lbrynet_get` command for each
        re-downloaded claim.
    """
    if not funcs.server_exists(server=server):
        return False

    if not number or not isinstance(number, int) or number < 0:
        number = 2
        print("Number must be a positive integer, "
              f"set to default value, number={number}")

    if (not ddir or not isinstance(ddir, str)
            or ddir == "~" or not os.path.exists(ddir)):
        ddir = os.path.expanduser("~")
        print(f"Download directory should exist; set to ddir='{ddir}'")

    sorted_items = sort.sort_items(server=server)
    sorted_items.reverse()

    if shuffle:
        random.shuffle(sorted_items)
        random.shuffle(sorted_items)
        random.shuffle(sorted_items)

    list_info_get = []

    print(80 * "-")

    for it, item in enumerate(sorted_items, start=1):
        if it > number:
            break

        print(f"Re-download claim {it}/{number}")
        d = dld.download_single(cid=item["claim_id"],
                                ddir=ddir, own_dir=own_dir,
                                save_file=save_file,
                                server=server)
        list_info_get.append(d)
        print()

    return list_info_get


def download_claims(ddir=None, own_dir=True, save_file=True,
                    start=1, end=0, file=None, sep=";", invalid=False,
                    server="http://localhost:5279"):
    """Download claims from a file, or redownload the ones already present.

    Parameters
    ----------
    ddir: str, optional
        It defaults to `$HOME`.
        The path to the download directory.
    own_dir: bool, optional
        It defaults to `True`, in which case it places the downloaded
        content inside a subdirectory named after the channel in `ddir`.
    save_file: bool, optional
        It defaults to `True`, in which case all blobs of the stream
        will be downloaded, and the media file (mp4, mp3, mkv, etc.)
        will be placed in the downloaded directory.
        If it is `False` it will only download the first blob (`sd_hash`)
        in the stream, so the file will be in the local database
        but the complete file won't be placed in the download directory.
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
        and one data field is the `'claim_id'` which can be used
        with `download_single` to get that claim. The value of `sep`
        indicates the separator between the fields.

        If `file=None` it will re-download the claims obtained
        from `sort_items` which should already be present
        in the system fully or partially.
    sep: str, optional
        It defaults to `;`. It is the separator character between
        the data fields in the read file. Since the claim name
        can have commas, a semicolon `;` is used by default.
    invalid: bool, optional
        It defaults to `False`, in which case it will assume
        the processed claims are still valid in the online database.
        It will use `lbrynet claim search` to resolve the `claim_id`.

        If it is `True` it will assume the claims are no longer valid,
        that is, that the claims have been removed from the online database
        and only exist locally.
        In this case, it will use `lbrynet file list` to resolve
        the `claim_id`.

        Therefore this parameter is required if `file` is a document
        containing 'invalid' claims, otherwise the claims won't be found.
        For 'invalid' claims they cannot be downloaded anymore from the online
        database; if their binary blobs are complete, the media files
        (mp4, mp3, mkv, etc.) will simply be recreated in `ddir`.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary represents
        the standard output of the `lbrynet_get` command for each
        downloaded claim.
    False
        If there is a problem, non-existing claims, or non-existing file,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    print(80 * "-")

    if not file:
        print("Redownload from existing claims")
        sorted_items = sort.sort_items(server=server)

        if not sorted_items:
            print(">>> Error: no claims previously downloaded.")
            return False
    else:
        if file and not isinstance(file, str) or not os.path.exists(file):
            print("The file path must exist.")
            print(f"file={file}")
            return False

        print("Download from existing file")
        sorted_items = srch.parse_claim_file(file=file, sep=sep)
        print()

        if not sorted_items:
            print(">>> Error: the file must have a 'claim_id' "
                  "(40-character alphanumeric string); "
                  "could not parse the file.")
            print(f"file={file}")
            return False

    n_items = len(sorted_items)

    list_info_get = []

    for it, item in enumerate(sorted_items, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        print(f"Claim {it}/{n_items}")
        info_get = dld.download_single(cid=item["claim_id"],
                                       invalid=invalid,
                                       ddir=ddir, own_dir=own_dir,
                                       save_file=save_file,
                                       server=server)
        list_info_get.append(info_get)
        print()

    return list_info_get
