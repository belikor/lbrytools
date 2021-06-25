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

import lbrytools.search as srch


def print_info_pre_get(item=None, offline=False):
    """Print information about the item found in the LBRY network.

    Parameters
    ----------
    item: dict
        A dictionary with the information of an item, obtained
        from `search_item`.
        ::
            item = search_item(uri="some-video-name")
    offline: bool, optional
        It defaults to `False`, in which case it assumes the item was
        resolved online through `lbrynet resolve` or `lbrynet claim search`.

        If it is `True` it assumes the item was resolved offline
        through `lbrynet file list`.
        This is required for 'invalid' claims, that is,
        those that have been removed from the online database
        and only exists locally.

    Returns
    -------
    list of 7 elements (str)
        If the item is valid, it will return a list of strings
        with information on that item.
        The information is `'canonical_url'` or `'claim_name'`, `'claim_id'`,
        `'release_time'` including date and time,
        `'title'`, `'stream_type'` (video, audio, document, etc.),
        `'size'` in MB, and `'duration'` in minutes and seconds.

        Due to the different types of claims in the network,
        some of them may not have `'release_time'`, `'size'`,
        or `'duration'`.
        In this case the corresponding missing value is set to `'0'`.
    False
        If there is a problem or no item, it will return `False`.
    """
    if not item:
        print("Error: no item. Get one item with `search_item(uri)`")
        return False

    if offline:
        item["value"] = item["metadata"]

    _time = "0"
    if "release_time" in item["value"]:
        _time = int(item["value"]["release_time"])
        _time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                              time.localtime(_time))

    _size = 0
    if "source" in item["value"] and "size" in item["value"]["source"]:
        _size = float(item["value"]["source"]["size"])/(1024*1024)

    if offline:
        _title = item["claim_name"]
    else:
        _title = item["name"]
    if "title" in item["value"]:
        _title = item["value"]["title"]

    if offline:
        _type = item["mime_type"]
    else:
        _type = item["type"]
    if "stream_type" in item["value"]:
        _type = item["value"]["stream_type"]

    length_s = 0
    rem_s = 0
    rem_min = 0

    if "video" in item["value"] and "duration" in item["value"]["video"]:
        length_s = item["value"]["video"]["duration"]
    if "audio" in item["value"] and "duration" in item["value"]["audio"]:
        length_s = item["value"]["audio"]["duration"]

    rem_s = length_s % 60
    rem_min = (length_s - rem_s)/60

    if offline:
        info = ["claim_name: " + item["claim_name"]]
    else:
        info = ["canonical_url: " + item["canonical_url"]]

    _info = ["claim_id: " + item["claim_id"],
             "release_time: " + _time,
             "title: " + _title,
             "stream_type: " + _type,
             "size: {:.4f} MB".format(_size),
             "duration: {} min {} s".format(rem_min, rem_s)]
    info.extend(_info)

    for line in info:
        print(line)
    return info


def print_info_post_get(info_get=None):
    """Print information about the downloaded item from lbrynet get.

    Parameters
    ----------
    info_get: dict
        A dictionary with the information obtained from downloading
        a claim.
        ::
            info_get = lbrynet_get(get_cmd)

    Returns
    -------
    bool
        It returns `True` if the information was read and printed
        without problems.
        If there is a problem or no item, it will return `False`.
    """
    if not info_get:
        print("Error: no item information. "
              "Get the information with `lbrynet_get(cmd)`")
        return False

    err = False

    if "error" in info_get:
        print(">>> Error: " + info_get["error"])
        err = True
    elif not info_get["blobs_in_stream"]:
        # In certain cases the information does not have blobs in the stream
        # nor download path. This may need to be checked if it causes
        # an error that cannot be handled later.
        # elif (not info_get["blobs_in_stream"]
        #       or not info_get["download_path"]):
        # print(info_get)
        print(">>> Error in downloading claim, "
              f"blobs_in_stream={info_get['blobs_in_stream']}, "
              f"download_path={info_get['download_path']}")
        err = True

    if not err:
        print("blobs_completed: {}".format(info_get["blobs_completed"]))
        print("blobs_in_stream: {}".format(info_get["blobs_in_stream"]))
        print("download_path: {}".format(info_get["download_path"]))
        print("completed: {}".format(info_get["completed"]))
    else:
        print(">>> Skip download.")

    return True


def print_multi_list(list_ch_info=None):
    """Print the summary of downloaded claims from multiple channels.

    This is meant to be used with the returned list from
    `ch_download_latest_multi`.

    Parameters
    ----------
    list of lists of dicts
        A list of lists, where each internal list represents one channel,
        and this internal list has as many dictionaries as downloaded claims.
        The information in each dictionary represents the standard output
        of the `lbrynet_get` command for each downloaded claim.

        If the download fails, then the corresponding item in the list
        may be `False`, in which case no claim information is printed.

    Returns
    -------
    bool
        It returns `True` if the information was read and printed
        without problems.
        If there is a problem or no list of items, it will return `False`.
    """
    if not list_ch_info or not isinstance(list_ch_info, (list, tuple)):
        print("Print information from a list of lists from multiple "
              "channels obtained from `ch_download_latest_multi`.")
        return False

    if len(list_ch_info) < 1:
        print("Empty list.")
        return False

    # flat_list = [item for sublist in list_ch_info for item in sublist]
    flat_list = []
    for sublist in list_ch_info:
        if not sublist:
            flat_list.append(None)
            continue

        for item in sublist:
            if not item:
                flat_list.append(None)
                continue
            flat_list.append(item)

    n_items = len(flat_list)

    print("Summary of downloads")

    for it, item in enumerate(flat_list, start=1):
        out = "{:2d}/{:2d}, ".format(it, n_items)

        if not item:
            print(out + "empty item; failed download?")
            continue

        if "claim_id" in item:
            print(out + "{}, {}, {}".format(item["claim_id"],
                                            item["channel_name"],
                                            item["claim_name"]))
        elif "error" in item:
            print(out + "{}".format(item["error"]))
        else:
            print(out + "not downloaded")

    return True


def print_items(items=None, show="all",
                title=False, typ=False, path=False,
                cid=True, blobs=True, ch=False, ch_online=True, name=True,
                start=1, end=0, channel=None,
                file=None, fdate=False,
                server="http://localhost:5279"):
    """Print information on each claim in the given list of claims.

    Parameters
    ----------
    items: list of dict
        List of items to print information about.
        Each item should be a dictionary filled with information
        from the standard output of the `lbrynet file list` command.
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
        Show the type of claim (video, audio, document, etc.).
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

        Using this parameter sets `ch=True`, and is slow because
        it needs to perform an additional search for the channel.
    file: str, optional
        It defaults to `None`.
        It must be a user writable path to which the summary will be written.
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
    bool
        It returns `True` if it printed the summary successfully.
        If there is any error it will return `False`.
    """
    if not items or not isinstance(items, (list, tuple)):
        print("No input item list. "
              "A list of items must be obtained from `lbrynet file list`.")
        print(f"items={items}, "
              f"show={show}, "
              f"title={title}, typ={typ}, path={path}, "
              f"cid={cid}, blobs={blobs}, ch={ch}, ch_online={ch_online}, "
              f"name={name}, start={start}, end={end}, "
              f"channel={channel}, file={file}, fdate={fdate}")
        if file:
            print("No file written.")
        return False

    n_items = len(items)

    if (not isinstance(show, str)
            or show not in ("all", "media", "missing", "incomplete", "full")):
        print(">>> Error: show can only be 'all', 'media', 'missing', "
              "'incomplete', or 'full'")
        print(f"show={show}")
        return False

    if channel:
        if not isinstance(channel, str):
            print(">>> Error: channel must be a string")
            return False
        ch = True

    if file and not isinstance(file, str):
        print("The file must be a string.")
        print(f"file={file}")
        return False

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

    for it, item in enumerate(items, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        _path = item["download_path"]
        _blobs = item["blobs_completed"]
        _blobs_in_stream = item["blobs_in_stream"]
        # _completed = item["completed"]

        # Skip printing an item depending on the value of `show`,
        # and whether the blobs or media files exist or not
        if show in "media" and not _path:
            continue
        elif show in "missing" and _path:
            continue
        elif show in "incomplete" and _blobs == _blobs_in_stream:
            continue
        elif show in "full" and _blobs < _blobs_in_stream:
            continue

        _time = int(item["metadata"]["release_time"])
        _time = time.localtime(_time)
        _time = time.strftime("%Y%m%d_%H:%M:%S%z", _time)
        _title = item["metadata"]["title"]
        _claim_id = item["claim_id"]
        _claim_name = item["claim_name"]
        _type = item["metadata"]["stream_type"]

        out = "{:4d}/{:4d}, {}, ".format(it, n_items, _time)

        if title:
            out += f"{_title}, "
        if typ:
            out += f"{_type}, "
        if path:
            out += f"{_path}, "

        if cid:
            out += f"{_claim_id}, "
        if blobs:
            out += "{:3d}/{:3d}, ".format(_blobs, _blobs_in_stream)
        if ch:
            if ch_online:
                # Searching online is slower but it gets the full channel name
                _channel = srch.find_channel(cid=item["claim_id"], full=True,
                                             server=server)
                if not _channel:
                    print(out + _claim_name)
                    print()
                    continue
            else:
                # Searching offline is necessary for "invalid" claims
                # that no longer exist as active claims online.
                # We don't want to skip this item so we force a channel name.
                _channel = item["channel_name"]
                if not _channel:
                    _channel = "_None_"

            out += f"{_channel}, "

            # Skip if the item is not published by the specified channel
            if channel and channel not in _channel:
                continue

        if name:
            out += f"{_claim_name}, "

        if _path:
            out += "media"
        else:
            out += "missing"

        if file and fd:
            print(out, file=fd)
        else:
            print(out)

    if file and fd:
        fd.close()
        print(f"Summary written: {file}")

    return True


def print_summary(show="all",
                  title=False, typ=False, path=False,
                  cid=True, blobs=True, ch=False, ch_online=True, name=True,
                  start=1, end=0, channel=None, invalid=False,
                  file=None, fdate=False,
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
        items = srch.sort_invalid(server=server)
        if len(items) < 1:
            if file:
                print("No file written.")
            return False

        print()
        status = print_items(items, show=show,
                             title=title, typ=typ, path=path,
                             cid=cid, blobs=blobs, ch=ch, ch_online=False,
                             name=name,
                             start=start, end=end, channel=channel,
                             file=file, fdate=fdate,
                             server=server)
    else:
        items = srch.sort_items(server=server)
        if len(items) < 1:
            if file:
                print("No file written.")
            return False

        print()
        status = print_items(items, show=show,
                             title=title, typ=typ, path=path,
                             cid=cid, blobs=blobs, ch=ch, ch_online=ch_online,
                             name=name,
                             start=start, end=end, channel=channel,
                             file=file, fdate=fdate,
                             server=server)
    return status


def print_channels(full=True, canonical=False,
                   simple=False, invalid=False, offline=False,
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
    if invalid:
        items = srch.sort_invalid(server=server)
    else:
        items = srch.sort_items(server=server)

    if not items:
        if invalid:
            print("No invalid claims found. No channels will be listed.")
        else:
            print("No items found. No channels will be listed.")
        return False

    if invalid:
        offline = True

    all_channels = []

    for item in items:
        channel = srch.find_channel(cid=item["claim_id"],
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
    print()

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

    if simple:
        out = ", ".join(all_channels)
        print(out)
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
            c1 = all_channels[index + 0]
            c2 = all_channels[index + 1]
            c3 = all_channels[index + 2]
            print(f"{row:3d}: {c1:33s} {c2:33s} {c3:33s}")
            index += 3
            row += 3

    # Print the last row, which may be the only row if row=1
    if res == 1:
        c1 = all_channels[index + 0]
        print(f"{row:3d}: {c1:33s}")
    if res == 2:
        c1 = all_channels[index + 0]
        c2 = all_channels[index + 1]
        print(f"{row:3d}: {c1:33s} {c2:33s}")
    if res == 0:
        c1 = all_channels[index + 0]
        c2 = all_channels[index + 1]
        c3 = all_channels[index + 2]
        print(f"{row:3d}: {c1:33s} {c2:33s} {c3:33s}")

    return all_channels
