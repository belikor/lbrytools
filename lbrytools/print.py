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
import time

import lbrytools.funcs as funcs
import lbrytools.search_ch as srch_ch


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

    cl_time = 0
    if "release_time" in item["value"]:
        cl_time = int(item["value"]["release_time"])
        cl_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                                time.localtime(cl_time))

    cl_size = 0
    if "source" in item["value"] and "size" in item["value"]["source"]:
        cl_size = float(item["value"]["source"]["size"])/(1024**2)  # to MiB

    if offline:
        cl_title = item["claim_name"]
    else:
        cl_title = item["name"]

    if "title" in item["value"]:
        cl_title = item["value"]["title"]

    if offline:
        cl_type = item["mime_type"]
    else:
        cl_type = item["type"]

    if "stream_type" in item["value"]:
        cl_type = item["value"]["stream_type"]

    if offline:
        cl_vtype = "stream"
    else:
        cl_vtype = item["value_type"]

    length_s = 0
    rem_s = 0
    rem_min = 0

    if "video" in item["value"] and "duration" in item["value"]["video"]:
        length_s = item["value"]["video"]["duration"]
    if "audio" in item["value"] and "duration" in item["value"]["audio"]:
        length_s = item["value"]["audio"]["duration"]

    rem_s = length_s % 60  # remainder
    rem_min = length_s // 60  # integer part

    if offline:
        info = ["claim_name: " + item["claim_name"]]
    else:
        info = ["canonical_url: " + item["canonical_url"]]

    info2 = ["claim_id: " + item["claim_id"],
             "release_time: " + cl_time,
             "value_type: " + cl_vtype,
             "stream_type: " + cl_type,
             "title: " + cl_title,
             f"size: {cl_size:.4f} MB",
             f"duration: {rem_min} min {rem_s} s"]
    info.extend(info2)

    print("\n".join(info))
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


def print_multi_list(list_ch_info=None, sep=";"):
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
    sep: str, optional
        It defaults to `;`. It is the separator character between
        the data fields in the printed summary. Since the claim name
        can have commas, a semicolon `;` is used by default.

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
    out_list = []

    for it, item in enumerate(flat_list, start=1):
        out = "{:2d}/{:2d}".format(it, n_items) + f"{sep} "

        if not item:
            out += "empty item. Failure establishing server connection?"
            out_list.append(out)
            continue

        if "claim_id" in item:
            out += "{}".format(item["claim_id"]) + f"{sep} "
            out += "{:3d}/{:3d}".format(item["blobs_completed"],
                                        item["blobs_in_stream"]) + f"{sep} "
            out += '"{}"'.format(item["channel_name"])
            out += f"{sep} "
            out += '"{}"'.format(item["claim_name"])
            out_list.append(out)
        elif "error" in item:
            out_list.append(out + '"{}"'.format(item["error"]))
        else:
            out_list.append(out + "not downloaded")

    print("\n".join(out_list))
    return True


def print_items(items=None, show="all",
                blocks=False, cid=True, blobs=True, size=True,
                typ=False, ch=False, ch_online=True,
                name=True, title=False, path=False,
                sanitize=False,
                start=1, end=0, channel=None,
                file=None, fdate=False, sep=";",
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
    blocks: bool, optional
        It defaults to `False`, in which case it won't print
        the `height` block of the claims.
        If it is `True` it will print this value, which gives some idea
        of when the claim was registered in the blockchain.
    cid: bool, optional
        It defaults to `True`.
        Show the `'claim_id'` of the claim.
        It is a 40 character alphanumeric string.
    blobs: bool, optional
        It defaults to `True`.
        Show the number of blobs in the file, and how many are complete.
    size: bool, optional
        It defaults to `True`.
        Show the length of the stream in minutes and seconds, like `14:12`,
        when possible (audio and video), and also the size in mebibytes (MB).
    typ: bool, optional
        It defaults to `False`.
        Show the type of stream (video, audio, document, etc.).
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
    title: bool, optional
        It defaults to `False`.
        Show the title of the claim.
    path: bool, optional
        It defaults to `False`.
        Show the full path of the saved media file.
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
    if not funcs.server_exists(server=server):
        return False

    if not items or not isinstance(items, (list, tuple)):
        print("No input item list. "
              "A list of items must be obtained from `lbrynet file list`.")
        print(f"items={items}, "
              f"show={show}, "
              f"title={title}, typ={typ}, path={path}, "
              f"cid={cid}, blobs={blobs}, ch={ch}, ch_online={ch_online}, "
              f"name={name}, start={start}, end={end}, "
              f"channel={channel}, file={file}, fdate={fdate}, sep={sep}")
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

    out = []

    for num, item in enumerate(items, start=1):
        if num < start:
            continue
        if end != 0 and num > end:
            break

        st_path = item["download_path"]
        st_blobs = item["blobs_completed"]
        st_blobs_in_stream = item["blobs_in_stream"]
        # st_completed = item["completed"]

        # Skip printing an item depending on the value of `show`,
        # and whether the blobs or media files exist or not
        if show in "media" and not st_path:
            continue
        elif show in "missing" and st_path:
            continue
        elif show in "incomplete" and st_blobs == st_blobs_in_stream:
            continue
        elif show in "full" and st_blobs < st_blobs_in_stream:
            continue

        meta = item["metadata"]

        st_height = item["height"]
        st_time = int(meta["release_time"])
        st_time = time.strftime("%Y%m%d_%H:%M:%S%z",
                                time.localtime(st_time))

        st_claim_id = item["claim_id"]
        st_type = meta.get("stream_type", 8 * "_")
        st_claim_name = item["claim_name"]
        st_title = meta["title"]

        length_s = 0

        if ("video" in meta and "duration" in meta["video"]):
            length_s = meta["video"]["duration"]
        if ("audio" in meta and "duration" in meta["audio"]):
            length_s = meta["audio"]["duration"]

        rem_s = length_s % 60
        rem_min = length_s // 60

        st_size = 0
        if ("source" in meta and "size" in meta["source"]):
            st_size = float(meta["source"]["size"])
            st_size = st_size/(1024**2)  # to MB

        if ch:
            if ch_online:
                # Searching online is slower but it gets the full channel name
                st_channel = srch_ch.find_channel(cid=item["claim_id"],
                                                  full=True,
                                                  server=server)
                if not st_channel:
                    print(st_claim_name)
                    print()
                    continue
            else:
                # Searching offline is necessary for "invalid" claims
                # that no longer exist as active claims online.
                # We don't want to skip this item so we force a channel name.
                st_channel = item["channel_name"]
                if not st_channel:
                    st_channel = "_Unknown_"

            # Skip if the item is not published by the specified channel
            if channel and channel not in st_channel:
                continue

        if sanitize:
            st_claim_name = funcs.sanitize_name(st_claim_name)
            st_title = funcs.sanitize_name(st_title)
            st_channel = funcs.sanitize_name(st_channel)

        line = f"{num:4d}/{n_items:4d}" + f"{sep} "

        if blocks:
            line += f"{st_height:8d}" + f"{sep} "

        line += f"{st_time}" + f"{sep} "

        if cid:
            line += f"{st_claim_id}" + f"{sep} "

        if blobs:
            line += f"{st_blobs:3d}/{st_blobs_in_stream:3d}" + f"{sep} "

        if size:
            line += f"{rem_min:3d}:{rem_s:02d}" + f"{sep} "
            line += f"{st_size:9.4f} MB" + f"{sep} "

        if typ:
            line += f"{st_type:9s}" + f"{sep} "

        if st_path:
            line += "media   " + f"{sep} "
        else:
            line += "no-media" + f"{sep} "

        if ch:
            line += f"{st_channel}" + f"{sep} "

        if name:
            line += f'"{st_claim_name}"' + f"{sep} "

        if title:
            line += f'"{st_title}"' + f"{sep} "

        if path:
            line += f'"{st_path}"'

        out.append(line)

    print(f"Number of shown items: {len(out)}")

    funcs.print_content(out, file=file, fdate=fdate)

    return True
