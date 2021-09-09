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
"""Functions to print information about the claims in the LBRY network."""
import os
import time

import lbrytools.search_ch as srch_ch
import lbrytools.sort as sort
import lbrytools.print as prnt


def print_summary(show="all",
                  title=False, typ=False, path=False,
                  cid=True, blobs=True, ch=False, ch_online=True, name=True,
                  start=1, end=0, channel=None, invalid=False,
                  file=None, fdate=False, sep=";",
                  server="http://localhost:5279"):
    """Print a summary of the items downloaded from the LBRY network.

    Parameters
    ----------
    show: str, optional
        It defaults to `'all'`, in which case it shows all items.
        If it is `'incomplete'` it will show claims that are missing blobs.
        If it is `'full'` it will show claims that have all blobs.
        If it is `'media'` it will show claims that have the media file
        (mp4, mp3, mkv, etc.).
        Normally only items that have all blobs also have a media file;
        however, if the claim is currently being downloaded
        a partial media file may be present.
        If it is `'missing'` it will show claims that don't have
        the media file, whether the full blobs are present or not.
    title: bool, optional
        It defaults to `False`.
        Show the title of the claim.
    typ: bool, optional
        It defaults to `False`.
        Show the type of claim (video, audio, document, etc.)
    path: bool, optional
        It defaults to `False`.
        Show the full path of the saved media file.
    cid: bool, optional
        It defaults to `True`.
        Show the `'claim_id'` of the claim.
        It is a 40 character alphanumeric string.
    blobs: bool, optional
        It defaults to `True`.
        Show the number of blobs in the file, and how many are complete.
    ch: bool, optional
        It defaults to `False`.
        Show the name of the channel that published the claim.

        This is slow if `ch_online=True`.
    ch_online: bool, optional
        It defaults to `True`, in which case it searches for the channel name
        by doing a reverse search of the item online. This makes the search
        slow.

        By setting it to `False` it will consider the channel name
        stored in the input dictionary itself, which will be faster
        but it won't be the full name of the channel. If no channel is found
        offline, then it will set a default value `'_None_'` just so
        it can be printed with no error.

        This parameter only has effect if `ch=True`, or if `channel`
        is used, as it internally sets `ch=True`.
    name: bool, optional
        It defaults to `True`.
        Show the name of the claim.
    start: int, optional
        It defaults to 1.
        Show claims starting from this index in the list of items.
    end: int, optional
        It defaults to 0.
        Show claims until and including this index in the list of items.
        If it is 0, it is the same as the last index in the list.
    channel: str, optional
        It defaults to `None`.
        It must be a channel's name, in which case it shows
        only the claims published by this channel.

        Using this parameter sets `ch=True`.
    invalid: bool, optional
        It defaults to `False`, in which case it prints every single claim
        previously downloaded.

        If it is `True` it will only print those claims that are 'invalid',
        that is, those that cannot be resolved anymore from the online
        database. This probably means that the author decided to remove
        the claims at some point after they were downloaded originally.
        This can be verified with the blockchain explorer, by following
        the claim ID for an 'unspent' transaction.

        Using this parameter sets `ch_online=False` as the channel name
        of invalid claims cannot be resolved online, only from the offline
        database.
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
    bool
        It returns `True` if it printed the summary successfully.
        If there is any error it will return `False`.
    """
    if invalid:
        items = sort.sort_invalid(server=server)
        if not items or len(items) < 1:
            if file:
                print("No file written.")
            return False

        print()
        status = prnt.print_items(items=items, show=show,
                                  title=title, typ=typ, path=path,
                                  cid=cid, blobs=blobs, ch=ch,
                                  ch_online=False, name=name,
                                  start=start, end=end, channel=channel,
                                  file=file, fdate=fdate, sep=sep,
                                  server=server)
    else:
        items = sort.sort_items(server=server)
        if not items or len(items) < 1:
            if file:
                print("No file written.")
            return False

        print()
        status = prnt.print_items(items=items, show=show,
                                  title=title, typ=typ, path=path,
                                  cid=cid, blobs=blobs, ch=ch,
                                  ch_online=ch_online, name=name,
                                  start=start, end=end, channel=channel,
                                  file=file, fdate=fdate, sep=sep,
                                  server=server)
    return status


def print_channels(full=True, canonical=False,
                   simple=False, invalid=False, offline=False,
                   start=1, end=0,
                   print_msg=True,
                   file=None, fdate=False,
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
        long string, each channel separated from another by a comma.
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

    all_channels = []

    for it, item in enumerate(items, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        channel = srch_ch.find_channel(cid=item["claim_id"],
                                       full=full, canonical=canonical,
                                       offline=offline,
                                       server=server)
        if channel:
            all_channels.append(channel)
        else:
            print()

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
        print(f"Original channels found: {n_channels} "
              "(does not include unresolved channels)")
    else:
        print(f"Original channels found: {n_channels} "
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
        out = ", ".join(all_channels)

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
            c1 = all_channels[index + 0] + ","
            c2 = all_channels[index + 1] + ","
            c3 = all_channels[index + 2] + ","
            out = f"{row:3d}: {c1:33s} {c2:33s} {c3:33s}"
            if file and fd:
                print(out, file=fd)
            else:
                print(out)
            index += 3
            row += 3

    # Print the last row, which may be the only row if row=1
    if res == 1:
        c1 = all_channels[index + 0]
        out = f"{row:3d}: {c1:33s}"
    if res == 2:
        c1 = all_channels[index + 0] + ","
        c2 = all_channels[index + 1]
        out = f"{row:3d}: {c1:33s} {c2:33s}"
    if res == 0:
        c1 = all_channels[index + 0] + ","
        c2 = all_channels[index + 1] + ","
        c3 = all_channels[index + 2]
        out = f"{row:3d}: {c1:33s} {c2:33s} {c3:33s}"

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
