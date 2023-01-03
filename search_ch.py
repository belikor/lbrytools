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
"""Functions to help with searching channels in the LBRY network."""
import lbrytools.funcs as funcs
import lbrytools.search_ch_all as srchall


def ch_search_latest(channel=None, number=2,
                     server="http://localhost:5279"):
    """Search for the latest claims published by a specific channel.

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
        The number of claims to search that were last posted by `channel`.
        If `number=0` it will search all claims ever published
        by this channel.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary represents a claim
        by `channel`. The newest claims will be first.
    False
        If there is a problem, or no existing channel,
        it will return False.
    """
    if not funcs.server_exists(server=server):
        return False

    if not channel or not isinstance(channel, str):
        print("Search items by channel name (string), "
              "and number of items (int).")
        print(f"channel={channel}, number={number}")
        return False

    if number is None or not isinstance(number, int):
        number = 2
        print(f"Number set to default value, number={number}")

    if channel.startswith("[") and channel.endswith("]"):
        channel = channel[1:-1]

    if not channel.startswith("@"):
        channel = "@" + channel

    if number:
        claims_info = srchall.ch_search_n_claims(channel,
                                                 number=number,
                                                 reverse=True,
                                                 server=server)
    else:
        claims_info = srchall.ch_search_all_claims(channel,
                                                   reverse=True,
                                                   server=server)

    return claims_info["claims"]


def get_streams(channel=None, number=2, print_msg=True,
                server="http://localhost:5279"):
    """Get streams downloadable and discard other things."""
    output = ch_search_latest(channel=channel, number=number,
                              server=server)
    if not output:
        return False

    claims = output

    if print_msg:
        print()
    n_claims = len(claims)

    streams = []
    for num, stream in enumerate(claims, start=1):
        if "value" in stream and "source" in stream["value"]:
            streams.append(stream)
            name = stream["name"]
            sd_hash = stream["value"]["source"]["sd_hash"]
            if print_msg:
                print(f"{num:3d}/{n_claims:3d}; {name}; {sd_hash}")

    n_streams = len(streams)
    if not n_streams:
        return False

    return streams
