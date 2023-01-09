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

    cl_time = "0"
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


def print_multi_list(multi_ch_info=None, sep=";"):
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
    if not multi_ch_info or not isinstance(multi_ch_info, (list, tuple)):
        print("Print information from a list of lists from multiple "
              "channels obtained from `ch_download_latest_multi`.")
        return False

    if len(multi_ch_info) < 1:
        print("Empty list.")
        return False

    # flat_list = [item for sublist in list_ch_info for item in sublist]
    flat_list = []
    for sublist in multi_ch_info:
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
    out = []

    for it, item in enumerate(flat_list, start=1):
        line = "{:2d}/{:2d}".format(it, n_items) + f"{sep} "

        if not item:
            line += "empty item. Failure establishing server connection?"
            out.append(line)
            continue

        if "claim_id" in item:
            line += "{}".format(item["claim_id"]) + f"{sep} "
            line += "{:3d}/{:3d}".format(item["blobs_completed"],
                                         item["blobs_in_stream"]) + f"{sep} "
            line += '"{}"'.format(item["channel_name"])
            line += f"{sep} "
            line += '"{}"'.format(item["claim_name"])
            out.append(line)
        elif "error" in item:
            out.append(line + '"{}"'.format(item["error"]))
        else:
            out.append(line + "not downloaded")

    funcs.print_content(out, file=None, fdate=False)

    return True
