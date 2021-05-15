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
"""Functions to print information about the claims in the LBRY network."""
import os
import time

from lbrytools.search import find_channel
from lbrytools.search import sort_items


def print_info_pre_get(item=None):
    """Print information about the item found in the LBRY network.

    Parameters
    ----------
    item: dict
        A dictionary with the information of an item, obtained
        from `search_item`.
        ::
            item = search_item(uri="some-video-name")

    Returns
    -------
    list of 7 elements (str)
        If the item is valid, it will return a list of strings
        with information on that item.
        The information is `'canonical_url'`, `'claim_id'`,
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

    _time = "0"
    if "release_time" in item["value"]:
        _time = int(item["value"]["release_time"])
        _time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                              time.localtime(_time))

    _size = 0
    if "size" in item["value"]["source"]:
         _size = float(item["value"]["source"]["size"])/(1024*1024)

    info = ["canonical_url: " + item["canonical_url"],
            "claim_id: " + item["claim_id"],
            "release_time: " + _time,
            "title: " + item["value"]["title"],
            "stream_type: " + item["value"]["stream_type"],
            "size: {:.4f} MB".format(_size)]

    rem_min = 0
    rem_s = 0
    if "video" in item["value"]:
        length_s = item["value"]["video"]["duration"]
        rem_s = length_s % 60
        rem_min = (length_s - rem_s)/60

    info.append(f"duration: {rem_min} min {rem_s} s")

    [print(line) for line in info]
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
    # elif (not info_get["blobs_in_stream"] or not info_get["download_path"]):
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


def print_items(items=None, show="all",
                title=False, typ=False, path=False,
                cid=True, blobs=True, ch=False, name=True,
                start=1, end=0, channel=None,
                file=None, date=False):
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

        This is slow as it needs to perform an additional search
        for the channel.
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
    date: bool, optional
        It defaults to `False`.
        If it is `True` it will add the date to the name of the summary file.

    Returns
    -------
    bool
        It returns `True` if it printed the summary successfully.
        If there is any error it will return `False`.
    """
    if not items or not isinstance(items, (list, tuple)):
        print("Print information from a list of items "
              "obtained from `lbrynet file list`.")
        print(f"items={items}, "
              f"show={show}, "
              f"title={title}, typ={typ}, path={path}, "
              f"cid={cid}, ch={ch}, name={name}, "
              f"start={start}, end={end}, file={file}")
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

        if date:
            date = time.strftime("%Y%m%d_%H%M", time.localtime()) + "_"
        else:
            date = ""

        file = os.path.join(dirn, date + base)

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
            _channel = find_channel(cid=item["claim_id"], full=True)
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
                  cid=True, blobs=True, ch=False, name=True,
                  start=1, end=0, channel=None,
                  file=None, date=False):
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

        This is slow as it needs to perform an additional search
        for the channel.
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
        It must be a writable path to which the summary will be written.
        Otherwise the summary will be printed to the terminal.
    date: bool, optional
        It defaults to `False`.
        If it is `True` it will add the date to the name of the summary file.

    Returns
    -------
    bool
        It returns `True` if it printed the summary successfully.
        If there is any error it will return `False`.
    """
    items = sort_items()
    status = print_items(items, show=show,
                         title=title, typ=typ, path=path,
                         cid=cid, blobs=blobs, ch=ch, name=name,
                         start=start, end=end, channel=channel,
                         file=file, date=date)
    return status
