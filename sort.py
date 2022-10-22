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
"""Functions to help with sorting downloaded claims from the LBRY network."""
import requests

import lbrytools.funcs as funcs
import lbrytools.search as srch
import lbrytools.search_utils as sutils
import lbrytools.search_ch as srch_ch


def sort_items(channel=None, reverse=False,
               server="http://localhost:5279"):
    """Return a list of claims that were downloaded, sorted by time.

    If `channel` is provided it will list the downloaded claims
    by this channel only.
    Otherwise it will list all claims.

    Parameters
    ----------
    channel: str, optional
        It defaults to `None`.
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the output list.
        If it is `True` newer claims are at the beginning of the list.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        A list of dictionaries that represent the claims that were previously
        downloaded fully or partially.
        Each dictionary is filled with information from the standard output
        of the `lbrynet file list` command.

        The dictionaries are ordered by `'release_time'`, with older claims
        appearing first.
        Certain claims don't have `'release_time'` so for them we add
        this key, and use the value of `'timestamp'` for it.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    page_size = 99000
    cmd = ["lbrynet",
           "file",
           "list",
           "--page_size=" + str(page_size)]

    if channel and not isinstance(channel, str):
        print("Channel must be a string. Set to 'None'.")
        print(f"channel={channel}")
        channel = None

    if channel:
        if not channel.startswith("@"):
            channel = "@" + channel
        cmd.append("--channel_name=" + "'" + channel + "'")

    print("List: " + " ".join(cmd))
    print(80 * "-")

    msg = {"method": cmd[1] + "_" + cmd[2],
           "params": {"page_size": page_size}}
    if channel:
        msg["params"]["channel_name"] = channel

        # A bug (lbryio/lbry-sdk #3316) prevents the `lbrynet file list`
        # command from finding the channel, therefore the channel must be
        # resolved with `lbrynet resolve` before it becomes known by other
        # functions.
        ch = srch_ch.resolve_channel(channel=channel, server=server)
        if not ch:
            return False

    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    items = output["result"]["items"]

    n_items = len(items)

    if n_items < 1:
        if channel:
            print("No items found; at least one item must be downloaded; "
                  f"check that the name is correct, channel={channel}")
        else:
            print("No items found; at least one item must be downloaded.")
        return False

    print(f"Number of items: {n_items}")

    new_items = []

    # Older claims may not have 'release_time'; we use the 'timestamp' instead
    for it, item in enumerate(items, start=1):
        if "release_time" not in item["metadata"]:
            print(f"{it}/{n_items}, {item['claim_name']}, using 'timestamp'")
            item["metadata"]["release_time"] = item["timestamp"]
        new_items.append(item)

    # Sort by using the original 'release_time'; older items first
    sorted_items = sorted(new_items,
                          key=lambda v: int(v["metadata"]["release_time"]),
                          reverse=reverse)

    return sorted_items


def sort_invalid(channel=None, reverse=False,
                 server="http://localhost:5279"):
    """Return a list of invalid claims that were previously downloaded.

    Certain claims that were downloaded in the past may be invalid now because
    they were removed by their authors from the network after
    they were initially downloaded. This can be confirmed by looking up
    the claim ID in the blockchain explorer, and finding the 'unspent'
    transaction.

    Parameters
    ----------
    channel: str, optional
        It defaults to `None`.
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the output list.
        If it is `True` newer claims are at the beginning of the list.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        A list of dictionaries that represent 'invalid claims'
        that were previously downloaded fully or partially.

        Each dictionary is filled with information from the standard output
        of the `lbrynet file list` command, but filtered in such a way
        that it only includes claims which are no longer searchable online
        by `lbrynet resolve` or `lbrynet claim search`.

        The dictionaries are ordered by `'release_time'`, with older claims
        appearing first.
        Certain claims don't have `'release_time'` so for them we add
        this key, and use the value of `'timestamp'` for it.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    items = sort_items(channel=channel, reverse=reverse,
                       server=server)
    if not items:
        return False

    n_items = len(items)

    invalid_items = []

    for it, item in enumerate(items, start=1):
        online_item = srch.search_item(cid=item["claim_id"], offline=False,
                                       print_error=False,
                                       server=server)
        if not online_item:
            if len(invalid_items) == 0:
                print()
            claim_id = item["claim_id"]
            claim_name = item["claim_name"]
            channel = item["channel_name"]
            print(f"Claim {it:4d}/{n_items:4d}, "
                  f"{claim_id}, {channel}, {claim_name}")
            invalid_items.append(item)

    n_invalid = len(invalid_items)
    if n_invalid > 0:
        print(f"Invalid items found: {n_invalid} "
              "(possibly deleted from the network)")
    else:
        print(f"Invalid items found: {n_invalid}")

    return invalid_items


def sort_items_size(channel=None, reverse=False, invalid=False,
                    server="http://localhost:5279"):
    """Return a list of claims that were downloaded, their size and length.

    Parameters
    ----------
    channel: str, optional
        It defaults to `None`.
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the output list.
        If it is `True` newer claims are at the beginning of the list.
    invalid: bool, optional
        It defaults to `False`, in which case it will return all items
        previously downloaded.
        If it is `True` it will only return those claims that were removed
        by their authors from the network after they were initially downloaded.
        These can no longer be resolved online, nor can they be re-downloaded.
        The blobs belonging to these claims can be considered orphaned
        and can be removed to save hard disk space.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with three keys:
        - 'claims': a list of dictionaries where every dictionary represents
          a claim returned by `file_list`.
          The list is ordered in ascending order by default (old claims first),
          and in descending order (newer claims first) if `reverse=True`.
          Certain claims don't have `'release_time'` so for them we add
          this key, and use the value of `'timestamp'` for it.
          If there are no claims the list may be empty.
        - 'size': total size of the claims in bytes.
          It can be divided by 1024 to obtain kibibytes, by another 1024
          to obtain mebibytes, and by another 1024 to obtain gibibytes.
        - 'duration': total duration of the claims in seconds.
          It will count only stream types which have a duration
          such as audio and video.
          The duration can be divided by 3600 to obtain hours,
          then by 24 to obtain days.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if invalid:
        claims = sort_invalid(channel=channel, reverse=reverse,
                              server=server)
    else:
        claims = sort_items(channel=channel, reverse=reverse,
                            server=server)

    if not claims:
        claims = []

    print()
    output = sutils.downloadable_size(claims, local=True)
    total_size = output["size"]
    total_duration = output["duration"]

    n_claims = len(claims)
    GB = total_size / (1024**3)  # to GiB

    hrs = total_duration / 3600
    days = hrs / 24

    hr = total_duration // 3600
    mi = (total_duration % 3600) // 60
    sec = (total_duration % 3600) % 60

    print(40 * "-")
    print(f"Total unique claims: {n_claims}")
    print(f"Total download size: {GB:.4f} GiB")
    print(f"Total duration: {hr} h {mi} min {sec} s, or {days:.4f} days")

    return {"claims": claims,
            "size": total_size,
            "duration": total_duration}
