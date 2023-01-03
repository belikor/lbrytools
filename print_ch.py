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

import lbrytools.funcs as funcs
import lbrytools.sort as sort
import lbrytools.resolve_ch as resch


def find_ch_th(cid, full, canonical, offline, server):
    """Wrapper to use with threads in 'print_channels'."""
    channel = resch.find_channel(cid=cid,
                                 full=full, canonical=canonical,
                                 offline=offline,
                                 server=server)

    if not channel:
        print()

    return channel


def print_three_cols(all_channels,
                     file=None, fdate=False, pre_num=True, sep=";"):
    """Print all channels in three columns.

    Determine how many rows are required to display all channels
    in three columns, and then add three channels to each row,
    except for the last row, which may have 1, 2 or 3 elements:
        c1      c2      c3
        c4      c5      c6
        c7

    The maximum channel length can be used to evenly space all channels
    in the columns. How do we integrate this into the format specifier?
    ::
        print(f"{c1:<length>s}")

        length = 0
        for ch in all_channels:
            if len(ch) > length:
                length = len(ch)
    """
    n_channels = len(all_channels)

    res = n_channels % 3

    if res == 0:
        rows = n_channels/3
    else:
        rows = n_channels/3 + 1

    out = []
    index = 0
    row = 1

    # Collect the rows that are full, only if the number of rows
    # is more than 1
    if rows > 1:
        for u in range(int(rows) - 1):
            c1 = all_channels[index + 0] + f"{sep}"
            c2 = all_channels[index + 1] + f"{sep}"
            c3 = all_channels[index + 2] + f"{sep}"

            line = f"{c1:33s} {c2:33s} {c3:33s}"

            if pre_num:
                line = f"{row:3d}: " + line

            out.append(line)

            index += 3
            row += 3

    # Collect the last row, which may be the only row if row=1.
    # The last row may have 1 item, 2 items or 3 items
    # depending on the residue calculated earlier
    if res == 0:
        c1 = all_channels[index + 0] + f"{sep}"
        c2 = all_channels[index + 1] + f"{sep}"
        c3 = all_channels[index + 2]

        line = f"{c1:33s} {c2:33s} {c3:33s}"

        if pre_num:
            line = f"{row:3d}: " + line

        out.append(line)

    if res == 1:
        c1 = all_channels[index + 0]

        line = f"{c1:33s}"

        if pre_num:
            line = f"{row:3d}: " + line

        out.append(line)

    if res == 2:
        c1 = all_channels[index + 0] + f"{sep}"
        c2 = all_channels[index + 1]

        line = f"{c1:33s} {c2:33s}"

        if pre_num:
            line = f"{row:3d}: " + line

        out.append(line)

    funcs.print_content(out, file=file, fdate=fdate)


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

            channel = find_ch_th(item["claim_id"],
                                 full, canonical, offline,
                                 server)
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

    if simple:
        out = [f"{sep} ".join(all_channels)]

        funcs.print_content(out, file=file, fdate=fdate)
    else:
        print_three_cols(all_channels,
                         file=file, fdate=fdate, pre_num=pre_num, sep=sep)

    e_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
    if print_msg:
        print()
        print(f"start: {s_time}")
        print(f"end:   {e_time}")

    return all_channels
