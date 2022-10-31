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
"""Functions to print channels in the LBRY network."""
import time
import concurrent.futures as fts
import os

import lbrytools.funcs as funcs
import lbrytools.sort as sort
import lbrytools.search_ch as srch_ch
import lbrytools.search_ch_all as srchall
import lbrytools.print_claims as prntc


def find_ch_th(cid, full, canonical, offline, server):
    """Wrapper to use with threads in 'print_channels'."""
    channel = srch_ch.find_channel(cid=cid,
                                   full=full, canonical=canonical,
                                   offline=offline,
                                   server=server)
    return channel


def print_channels(full=True, canonical=False,
                   simple=False, invalid=False, offline=False,
                   threads=32,
                   start=1, end=0,
                   print_msg=True,
                   file=None, fdate=False, pre_num=True, sep=";",
                   server="http://localhost:5279"):
    """Print a unique list of channels by inspecting all downloaded claims.

    Certain claims were published anonymously, so for these the channel
    is `@_Unknown_`.

    Parameters
    ----------
    full: bool, optional
        It defaults to `True`, in which case the returned
        name includes the digits after `'#'` or `':'` that uniquely identify
        that channel in the network.
        If it is `False` it will return just the base name.
        This parameter only works with `invalid=False` and `offline=False`,
        as the full name always needs to be resolved online.
        This value is ignored if `canonical=True`.
    canonical: bool, optional
        It defaults to `False`.
        If it is `True` the `'canonical_url'` of the channel is returned
        regardless of the value of `full`.
        This parameter only works with `invalid=False` and `offline=False`,
        as the canonical name always needs to be resolved online.
    simple: bool, optional
        It defaults to `False`, in which case the channels are printed
        in three columns.
        If it is `True` the channels will be printed as a single,
        long string, each channel separated from another by a `sep` symbol.
    invalid: bool, optional
        It defaults to `False`, in which case it will try to resolve
        the list of claims from the online database (blockchain),
        and will also try to resolve the channel name online, unless
        `offline=True`.

        If it is `True` it will assume the claims are no longer valid,
        that is, that the claims have been removed from the online database
        and only exist locally.
        This also implies `offline=True`, meaning that the channel name
        will be determined from the offline database.
    offline: bool, optional
        It defaults to `False`, in which case it will try to resolve
        the channel name from the online database (blockchain).

        If it is `True` it will try to resolve the channel name
        from the offline database. This will be faster but may not
        print all known channels, only those that have been resolved
        when the claims were initially downloaded.
    threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to find channels,
        meaning claims that will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
    start: int, optional
        It defaults to 1.
        Count the channels starting from this index in the list of channels.
    end: int, optional
        It defaults to 0.
        Count the channels until and including this index
        in the list of channels.
        If it is 0, it is the same as the last index in the list.
    print_msg: bool, optional
        It defaults to `True`, in which case it will print the final time
        taken to print the channels.
        If it is `False` it will not print this information.
    file: str, optional
        It defaults to `None`.
        It must be a writable path to which the summary will be written.
        Otherwise the summary will be printed to the terminal.
    fdate: bool, optional
        It defaults to `False`.
        If it is `True` it will add the date to the name of the summary file.
    pre_num: bool, optional
        It defaults to `True`, in which case it will print the index
        of the channel at the beginning of the line; this way it is easy
        to count the channels.
        If it is `False` it won't show a number, just the channels.
    sep: str, optional
        It defaults to `;`. It is the separator for the fields.
        Since the claim name accepts commas, a semicolon is chosen by default.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of str
        It returns a list with all channel names found.
    False
        If there is a problem like non existing channels,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    s_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
    if invalid:
        items = sort.sort_invalid(server=server)
    else:
        items = sort.sort_items(server=server)

    if not items:
        if invalid:
            print("No invalid claims found. No channels will be listed.")
        else:
            print("No items found. No channels will be listed.")
        return False

    print()
    if invalid:
        offline = True

    # Iterables to be passed to the ThreadPoolExecutor
    all_channels = []
    n_items = len(items)
    cids = (item["claim_id"] for item in items)
    fulls = (full for n in range(n_items))
    canonicals = (canonical for n in range(n_items))
    offs = (offline for n in range(n_items))
    servers = (server for n in range(n_items))

    if threads:
        with fts.ThreadPoolExecutor(max_workers=threads) as executor:
            # The input must be iterables
            results = executor.map(find_ch_th,
                                   cids, fulls, canonicals, offs,
                                   servers)

            # generator to list, only non False items are added
            all_channels = [ch for ch in results if ch]
    else:
        for num, item in enumerate(items, start=1):
            if num < start:
                continue
            if end != 0 and num > end:
                break

            channel = srch_ch.find_channel(cid=item["claim_id"],
                                           full=full, canonical=canonical,
                                           offline=offline,
                                           server=server)
            if channel:
                all_channels.append(channel)

    if not all_channels:
        print("No unique channels could be determined.")
        if invalid:
            print("It is possible that the channels "
                  "were not resolved when the claims "
                  "were initially downloaded.")
        else:
            print("It is possible that the claims are now invalid, "
                  "or that the channels were not resolved when "
                  "the claims were initially downloaded.")
        return False

    all_channels = list(set(all_channels))
    all_channels.sort()

    n_channels = len(all_channels)

    if invalid or offline:
        print(f"Channels found: {n_channels} "
              "(does not include unresolved channels)")
    else:
        print(f"Channels found: {n_channels} "
              "(does not include invalid claims, or unresolved channels)")

    print(80 * "-")

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

    if simple:
        out = f"{sep} ".join(all_channels)

        if file and fd:
            print(out, file=fd)
            fd.close()
            print(f"Summary written: {file}")
        else:
            print(out)

        e_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
        if print_msg:
            print()
            print(f"start: {s_time}")
            print(f"end:   {e_time}")
        return all_channels

    # Maximum channel length can be used to evenly space all channels
    # in columns. How do we integrate this into the format specifier?
    # print(f"{c1:<length>s}")
    #
    # length = 0
    # for ch in all_channels:
    #     if len(ch) > length:
    #         length = len(ch)

    # Determine how many rows are required to display
    # all channels in three columns
    # c1    c2     c3
    # c4    c5
    res = n_channels % 3
    if res == 0:
        rows = n_channels/3
    else:
        rows = n_channels/3 + 1

    index = 0
    row = 1

    # Print rows that are full, only if the number of rows is more than 1
    if rows > 1:
        for u in range(int(rows)-1):
            c1 = all_channels[index + 0] + f"{sep}"
            c2 = all_channels[index + 1] + f"{sep}"
            c3 = all_channels[index + 2] + f"{sep}"
            if pre_num:
                out = f"{row:3d}: {c1:33s} {c2:33s} {c3:33s}"
            else:
                out = f"{c1:33s} {c2:33s} {c3:33s}"
            if file and fd:
                print(out, file=fd)
            else:
                print(out)
            index += 3
            row += 3

    # Print the last row, which may be the only row if row=1
    if res == 1:
        c1 = all_channels[index + 0]
        if pre_num:
            out = f"{row:3d}: {c1:33s}"
        else:
            out = f"{c1:33s}"
    if res == 2:
        c1 = all_channels[index + 0] + f"{sep}"
        c2 = all_channels[index + 1]
        if pre_num:
            out = f"{row:3d}: {c1:33s} {c2:33s}"
        else:
            out = f"{c1:33s} {c2:33s}"
    if res == 0:
        c1 = all_channels[index + 0] + f"{sep}"
        c2 = all_channels[index + 1] + f"{sep}"
        c3 = all_channels[index + 2]
        if pre_num:
            out = f"{row:3d}: {c1:33s} {c2:33s} {c3:33s}"
        else:
            out = f"{c1:33s} {c2:33s} {c3:33s}"

    if file and fd:
        print(out, file=fd)
        fd.close()
        print(f"Summary written: {file}")
    else:
        print(out)

    e_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
    if print_msg:
        print()
        print(f"start: {s_time}")
        print(f"end:   {e_time}")

    return all_channels


def print_ch_claims(channel,
                    number=0,
                    blocks=False, claim_id=False,
                    typ=False, ch_name=False,
                    title=False, sanitize=False,
                    start=1, end=0,
                    reverse=False,
                    last_height=99_000_900,
                    file=None, fdate=None, sep=";",
                    server="http://localhost:5279"):
    """Print the claims from a single clannel.

    Parameters
    ----------
    channel: str
        Channel for which to show claims.
    number: int, optional
        It defaults to 0, in which case the returned list will contain
        all unique claims.
        If this is any other number, it return only the newest claims
        up to an including `number`.
    blocks: bool, optional
        It defaults to `False`, in which case it won't print
        the `creation height` and `height` blocks of the claims.
        If it is `True` it will print these values, which gives some idea
        of when the claim was registered in the blockchain.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim ID (40-character string).
    typ: bool, optional
        It defaults to `False`.
        If it is `True` it will print the value type of the claim,
        the stream type (only for `stream` claims), and the media type
        (only for `stream` claims).
    ch_name: bool, optional
        It defaults to `False` in which case the name of the channel
        won't appear.
        If it is `True` it will print the channel name.
    title: bool, optional
        It defaults to `False`, in which case the claim name will be printed.
        If it is `True` it will print the title of the claim instead.
        To download a stream, the claim name or the claim ID must be used.
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the name of the claim and channel.
        If it is `True` it will remove these unicode characters.
        This option requires the `emoji` package to be installed.
    start: int, optional
        It defaults to 1.
        Show claims starting from this index in the list of items.
    end: int, optional
        It defaults to 0.
        Show claims until and including this index in the list of items.
        If it is 0, it is the same as the last index in the list.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the output list.
        If it is `True` newer claims are at the beginning of the list.
    last_height: int, optional
        Last block used to find claims.
        It will find claims in blocks before this block height, therefore,
        to find all claims this value must be larger than the last block
        in the blockchain at present time.
        The default value will have to be increased if the blockchain
        ever reaches this value, although this is unlikely in the short term.
    file: str, optional
        It defaults to `None`.
        It must be a writable path to which the summary will be written.
        Otherwise the summary will be printed to the terminal.
    fdate: bool, optional
        It defaults to `False`.
        If it is `True` it will add the date to the name of the summary file.
    sep: str, optional
        It defaults to `;`. It is the separator character between
        the data fields in the printed summary. Since the claim name
        can have commas, a semicolon `;` is used by default.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    str
        String that will be printed.
    False
        It there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if not channel.startswith("@"):
        channel = "@" + channel

    if number:
        output = srchall.ch_search_n_claims(channel,
                                            number=number,
                                            last_height=last_height,
                                            reverse=False,
                                            server=server)
    else:
        output = srchall.ch_search_all_claims(channel,
                                              last_height=last_height,
                                              reverse=False,
                                              server=server)

    if not output:
        return False

    content = prntc.print_sch_claims(output["claims"],
                                     blocks=blocks, claim_id=claim_id,
                                     typ=typ, ch_name=ch_name,
                                     title=title, sanitize=sanitize,
                                     start=start, end=end,
                                     reverse=reverse,
                                     file=file, fdate=fdate, sep=sep)

    return content


if __name__ == "__main__":
    output = print_ch_claims("@AlisonMorrow")  # 410
#    output = print_ch_claims("@BrittanyVenti")  # 600
#    output = print_ch_claims("@BrodieRobertson")  # 860
#    output = print_ch_claims("@Karlyn")  # 950
#    output = print_ch_claims("@DistroTube")  # 1008
#    output = print_ch_claims("@mises")  # 1200
#    output = print_ch_claims("@timcast")  # 1860
#    output = print_ch_claims("@TimcastIRL")  # 2080
#    output = print_ch_claims("@rossmanngroup")  # 2580
#    output = print_ch_claims("@Styxhexenhammer666")  # 3590
