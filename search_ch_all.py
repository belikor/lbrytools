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
"""Base functions to get all claims from a single channel on the network.

The original `claim_search` method gets a maximum of 50 claims in a page,
and maximum 20 pages, so 1000 results in total.
We need to search by `creation_height` to search for the latest 1000 claims,
then use a lower `creation_height` to find an earlier set of 1000 claims,
and repeat this process in order to find all claims to the beginning
of the blockchain.
"""
import requests

import lbrytools.funcs as funcs
import lbrytools.search_utils as sutils


def search_page(channel, page=1,
                last_height=99_000_900,
                print_msg=True,
                print_blocks=True,
                server="http://localhost:5279"):
    """Return 1 of the newest 20 pages (50 claims max) from a channel.

    The `last_height` parameter specifies the highest block
    to use as reference; it will look for claims before this block.
    """
    msg = {"method": "claim_search",
           "params": {"channel": channel,
                      # "claim_type": "stream",
                      "page_size": 50,
                      # "has_source": True,
                      "order_by": "creation_height",
                      "creation_height": "<=" + str(last_height),
                      "page": page}}

    output = requests.post(server, json=msg).json()
    if "error" in output:
        return False

    result = output["result"]

    if result["total_items"] < 1:
        print(f"{channel}: channel not found, "
              "or no downloadable items in this channel")
        return False

    items = result["items"]
    n_items = len(items)
    total_items = result["total_items"]

    if n_items < 1:
        return False

    if print_msg and result["page"] == 1 and total_items == 1000:
        print("This is a big channel with at least 1000 claims")

    page_height_h = items[0]["meta"]["creation_height"]
    page_height_l = items[-1]["meta"]["creation_height"]

    if print_blocks:
        print(f"Page: {page:2d}; total items: {total_items:4d}; "
              f"claims: {n_items:4d}; "
              f"block range: {page_height_h:8d}..{page_height_l:8d}")

    return result


def search_pages(channel,
                 last_height=99_000_900,
                 pages=0,
                 print_init=True,
                 server="http://localhost:5279"):
    """Return a maximum of 20 pages (1000 claims max) from a channel.

    The `pages` parameter cannot be larger than `total_pages`,
    as reported by a preliminary search.

    The `last_height` parameter specifies the highest block
    to use as reference; it will look for claims before this block.
    """
    # Initial search just to know how big the channel is
    result = search_page(channel, page=1, last_height=last_height,
                         print_msg=print_init,
                         print_blocks=False,
                         server=server)

    if not result:
        return False

    if not pages or pages >= result["total_pages"]:
        total_pages = result["total_pages"]
    elif pages < result["total_pages"]:
        total_pages = pages

    results = []

    for page in range(1, total_pages + 1):
        res = search_page(channel, page=page, last_height=last_height,
                          print_msg=False,
                          print_blocks=True,
                          server=server)
        results.append(res)

    return results


def ch_search_n_claims(channel,
                       number=1000,
                       last_height=99_000_900,
                       reverse=False,
                       server="http://localhost:5279"):
    """Return all claims of a channel up to the specified number.

    Parameters
    ----------
    channel: str
        Channel for which to find claims.
    number: int, optional
        It defaults to 1000.
    last_height: int, optional
        Last block used to find claims.
        It will find claims in blocks before this block height, therefore,
        to find all claims this value must be larger than the last block
        in the blockchain at present time.
        The default value will have to be increased if the blockchain
        ever reaches this value, although this is unlikely in the short term.
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
    dict
        A dictionary with nine keys:
        - 'claims': a list of dictionaries where every dictionary represents
          a claim returned by `claim_search`.
          The list is ordered in ascending order by default (old claims first),
          and in descending order (new claims first) if `reverse=True`.
        - 'size': total size of the claims in bytes.
          It can be divided by 1024 to obtain kibibytes, by another 1024
          to obtain mebibytes, and by another 1024 to obtain gibibytes.
        - 'duration': total duration of the claims in seconds.
          It will count only stream types which have a duration
          such as audio and video.
        - 'size_GB': total size in GiB (floating point value)
        - 'd_h': integer hours HH when the duration is shown as HH:MM:SS
        - 'd_min': integer minutes MM when the duration is shown as HH:MM:SS
        - 'd_s`: integer seconds SS when the duration is shown as HH:MM:SS
        - 'days': total seconds converted into days (floating point value)
        - 'summary': paragraph of text describing the number of claims,
           the total size in GiB, and the total duration expressed as HH:MM:SS,
           and days
    False
        It there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if not channel.startswith("@"):
        channel = "@" + channel

    print(f"Channel: {channel}")
    print(f"Search claims below block height: {last_height}")
    print(f"Number: {number}")
    print(80 * "-")

    if not number:
        return False

    all_claims = []

    cycles = number // 1000 + 1
    remainder = number % 1000

    for cycle in range(1, cycles + 1):
        if cycle < cycles:
            pages = 20
        else:
            pages = remainder // 50 + 1
        print(f"Search cycle: {cycle}")

        if cycle == 1:
            results = search_pages(channel, last_height=last_height,
                                   pages=pages,
                                   print_init=True,
                                   server=server)
        else:
            results = search_pages(channel, last_height=last_height,
                                   pages=pages,
                                   print_init=False,
                                   server=server)

        if not results:
            claims_info = sutils.sort_filter_size([])

            return claims_info

        for page in results:
            all_claims.extend(page["items"])

        last_height = all_claims[-1]["meta"]["creation_height"]

        if results[0]["total_pages"] < 20:
            break

    print()
    claims_info = sutils.sort_filter_size(all_claims,
                                          number=number,
                                          reverse=reverse)

    return claims_info


def ch_search_all_claims(channel,
                         last_height=99_000_900,
                         reverse=False,
                         server="http://localhost:5279"):
    """Return all claims of a channel, ordered by release time.

    Parameters
    ----------
    channel: str
        Channel for which to find claims.
    last_height: int, optional
        Last block used to find claims.
        It will find claims in blocks before this block height, therefore,
        to find all claims this value must be larger than the last block
        in the blockchain at present time.
        The default value will have to be increased if the blockchain
        ever reaches this value, although this is unlikely in the short term.
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
    dict
        A dictionary with nine keys:
        - 'claims': a list of dictionaries where every dictionary represents
          a claim returned by `claim_search`.
          The list is ordered in ascending order by default (old claims first),
          and in descending order (newer claims first) if `reverse=True`.
        - 'size': total size of the claims in bytes.
          It can be divided by 1024 to obtain kibibytes, by another 1024
          to obtain mebibytes, and by another 1024 to obtain gibibytes.
        - 'duration': total duration of the claims in seconds.
          It will count only stream types which have a duration
          such as audio and video.
        - 'size_GB': total size in GiB (floating point value)
        - 'd_h': integer hours HH when the duration is shown as HH:MM:SS
        - 'd_min': integer minutes MM when the duration is shown as HH:MM:SS
        - 'd_s`: integer seconds SS when the duration is shown as HH:MM:SS
        - 'days': total seconds converted into days (floating point value)
        - 'summary': paragraph of text describing the number of claims,
           the total size in GiB, and the total duration expressed as HH:MM:SS,
           and days
    False
        It there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if not channel.startswith("@"):
        channel = "@" + channel

    print(f"Channel: {channel}")
    print(f"Search claims below block height: {last_height}")
    print("Number: all")
    print(80 * "-")

    cycle = 1
    print(f"Search cycle: {cycle}")
    results = search_pages(channel, last_height=last_height,
                           pages=20,
                           print_init=True,
                           server=server)

    if not results:
        claims_info = sutils.sort_filter_size([])

        return claims_info

    total_items = results[0]["total_items"]

    all_claims = []

    for page in results:
        all_claims.extend(page["items"])

    # A maximum of 1000 items can be found with a single `search_pages` call,
    # that is, 20 pages with 50 items each.
    # If there are more items, `search_pages` is called again with a new
    # `creation_height` condition to find the next 1000 claims,
    # and this is repeated until all claims have been found.
    finished = False

    if total_items == 1000:
        earliest_height = all_claims[-1]["meta"]["creation_height"]
    else:
        finished = True

    while not finished:
        cycle += 1
        print(f"Search cycle: {cycle}")
        results = search_pages(channel, last_height=earliest_height,
                               pages=20,
                               print_init=False,
                               server=server)
        for page in results:
            all_claims.extend(page["items"])

        if results[0]["total_items"] == 1000:
            earliest_height = all_claims[-1]["meta"]["creation_height"]
        else:
            finished = True

    print()
    claims_info = sutils.sort_filter_size(all_claims,
                                          number=0,
                                          reverse=reverse)

    return claims_info


def get_all_claims(channel,
                   last_height=99_000_900,
                   reverse=False,
                   server="http://localhost:5279"):
    """Return all claims of a channel, ordered by release time.

    Not used at the moment, but this is closer to miko's original code.

    Parameters
    ----------
    channel: str
        Channel for which to find claims.
    last_height: int, optional
        Last block used to find claims.
        It will find claims in blocks before this block height, therefore,
        to find all claims this value must be larger than the last block
        in the blockchain at present time.
        The default value will have to be increased if the blockchain
        ever reaches this value, although this is unlikely in the short term.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        on the output list.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with nine keys:
        - 'claims': a list of dictionaries where every dictionary represents
          a claim returned by `claim_search`.
          The list is ordered in ascending order by default (old claims first),
          and in descending order (new claims first) if `reverse=True`.
        - The other eight keys are the same from
          `search_utils.downloadable_size`, 'size', 'duration', 'size_GB',
          'd_h', 'd_min', 'd_s', 'days', and 'summary'.
    False
        It there is a problem it will return `False`.
    """
    if not channel.startswith("@"):
        channel = "@" + channel

    print(f"Channel: {channel}")
    print(f"Search claims below block height: {last_height}")
    print(80 * "-")

    finished = False
    cycle = 1
    page = 1
    claims = []

    while not finished:
        # Find claims in the blocks smaller than the last block height.
        # A maximum of 1000 items can be found with a single call,
        # that is, 20 pages with 50 items each.
        # If there are more items, this is called again with a new
        # `creation_height` condition to find the next batch of claims,
        # and this is repeated until all claims have been found.
        if page == 1:
            print(f"Search cycle: {cycle}")

        if cycle == 1:
            result = search_page(channel, page=page,
                                 last_height=last_height,
                                 print_msg=True,
                                 print_blocks=True,
                                 server=server)
        else:
            result = search_page(channel, page=page,
                                 last_height=last_height,
                                 print_msg=False,
                                 print_blocks=True,
                                 server=server)

        if not result:
            finished = True
            break

        items = result["items"]
        n_items = len(items)

        if n_items < 1:
            finished = True
            break

        for num, item in enumerate(items, start=1):
            claims.append(item)

            if page == 20:
                last_height = item["meta"]["creation_height"]

        if page < 20:
            page += 1
        elif page == 20:
            finished = result["total_pages"] < result["page"]
            page = 1
            cycle += 1

    print()
    claims_info = sutils.sort_filter_size(claims,
                                          number=0,
                                          reverse=reverse)

    return claims_info


if __name__ == "__main__":
    output = ch_search_all_claims("@AlisonMorrow")  # ~722
    print()
    output = ch_search_all_claims("@rossmanngroup")  # ~3152
