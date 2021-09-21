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
"""Functions to measure space and clean downloaded content."""
import os
import shutil

import lbrytools.funcs as funcs
import lbrytools.search_ch as srch_ch
import lbrytools.sort as sort
import lbrytools.clean as clean


def used_space(main_dir=None):
    """Get the space in GB consumed by the main download directory.

    Parameters
    ----------
    main_dir: str
        It defaults to `$HOME`.
        This is the main or root directory that holds both
        the downloaded media files (mp4, mp3, mkv, etc.)
        as well as the downloaded binary blobs.

        On Linux, media files may go to `'$HOME/Downloads'`
        and blobs are normally found in
        `'$HOME/.locals/share/lbry/lbrynet/blobfiles'`
        so `main_dir` would be `$HOME`, or `'/home/user'`

    Moving blobs
    ------------
    The media files can be placed in any directory by specifying
    the appropriate download directory with `lbrynet_get`.

    The blobs may be placed in a different directory only by symbolically
    linking the default blobs directory to another location.
    ::
        ln -s /opt/blobfiles $HOME/.locals/share/lbry/lbrynet/blobfiles

    Then if both files and blobs are outside the default user directory,
    `main_dir` needs to be adjusted accordingly.
      - Downloads `/opt/downloads`
      - Blobs `/opt/blobfiles`
      - `used_space(main_dir='/opt')`

    Returns
    -------
    float
        The size in GB used by the `main_dir`.
    """
    if (not main_dir or not isinstance(main_dir, str)
            or main_dir == "~" or not os.path.exists(main_dir)):
        main_dir = os.path.expanduser("~")
        print("Download directory should exist; "
              f"set to main_dir='{main_dir}'")

    total, used, free = shutil.disk_usage(main_dir)
    size_bytes = used
    size_GB = float(size_bytes)/(1024*1024*1024)
    return size_GB


def pr_bar(size=1000, percent=90, actual_percent=90):
    """Print usage bar with two marks based on percent and actual_percent.

    Parameters
    ----------
    size: float, optional
        It defaults to 1000.
        Maximum size in GB of the bar.
    percent: float, optional
        It defaults to 90.
        Percentage of `size` that indicates a soft limit on the bar.
        One mark is placed here.
    actual_percent: float, optional
        It defaults to 90.
        Percentage of `size` that indicates a variable usage on the bar.
        The second mark is placed here.

        The first number `percent` is normally fixed,
        and `actual_percent` is usually a variable quantity that can be
        calculated from a function such as `used_space` together with
        the value of `size`.
    """
    spaces = 63
    limit = int(percent/100 * spaces)
    m = int(actual_percent/100 * spaces)

    limit_mark = limit * " " + "v"

    # Make sure the bar is full if the usage is more than 99%
    bar = "|"
    if actual_percent >= 99:
        m = spaces + 13
        bar += (spaces-1)*"="
    else:
        bar += m*"=" + (spaces-1-m)*"."
    bar += f"| {size:.1f} GB"

    usage_mark = m*" " + "^"

    print("\n".join([limit_mark, bar, usage_mark]))


def measure_usage(main_dir=None, size=1000, percent=90, bar=True):
    """Calculate whether space is available in the download directory.

    It also prints a visual representation of the available space,
    and how much has been used.

    Parameters
    ----------
    main_dir: str
        It defaults to `$HOME`.
        This is the main or root directory that holds both
        the downloaded media files (mp4, mp3, mkv, etc.)
        as well as the downloaded binary blobs.

        On Linux, media files may go to `'$HOME/Downloads'`
        and blobs are normally found in
        `'$HOME/.locals/share/lbry/lbrynet/blobfiles'`
        so `main_dir` would be `$HOME`, or `'/home/user'`
    size: float, optional
        It defaults to 1000.
        Maximum size in GB of `main_dir`.
        Ideally the downloaded media files and blobs never cross this limit.
    percent: float, optional
        It defaults to 90.
        Percentage of `size` that indicates a soft limit
        for the downloaded files.
        After this limit is crossed we should free space in `main_dir`
        by deleting older files and blobs.
    bar: bool, optional
        It defaults to `True`, in which case it will print a bar
        indicating the usage graphically.

    Returns
    -------
    bool
        It returns `True` if the limit indicated by `size` and `percent`
        was crossed by the downloaded files.
        It returns `False` if they are within limit.
    """
    if (not main_dir or not isinstance(main_dir, str)
            or main_dir == "~" or not os.path.exists(main_dir)):
        main_dir = os.path.expanduser("~")
        print("Download directory should exist; "
              f"set to main_dir='{main_dir}'")

    if not isinstance(size, (int, float)) or size <= 0:
        size = 1000
        print("Max disk usage should be a positive number; "
              f"set to size={size} GB")

    if (not isinstance(percent, (int, float))
            or percent <= 0 or percent > 100):
        percent = 90
        print("Percentage should be a positive number from 0 to 100; "
              f"set to percent={percent} %")

    usage = size * percent / 100

    actual_usage = used_space(main_dir=main_dir)
    actual_percent = actual_usage/size * 100

    print(f"Main directory: {main_dir}")
    print("Limit: {:.2f}% ({:.1f} GB) of {:.1f} GB".format(percent, usage,
                                                           size))
    print("Usage: {:.2f}% ({:.1f} GB)".format(actual_percent, actual_usage))

    above = False
    if actual_percent >= percent:
        above = True

    if above:
        print(">>> Downloads are above the indicated limit.")
    else:
        print("Downloads are within limits.")

    if bar:
        pr_bar(size=size, percent=percent, actual_percent=actual_percent)

    return above


def cleanup_space(main_dir=None, size=1000, percent=90,
                  never_delete=None, what="media",
                  server="http://localhost:5279"):
    """Clean up space in the download drive when it is sufficiently full.

    Parameters
    ----------
    main_dir: str
        It defaults to `$HOME`.
        This is the main or root directory that holds both
        the downloaded media files (mp4, mp3, mkv, etc.)
        as well as the downloaded binary blobs.

        On Linux, media files may go to `'$HOME/Downloads'`
        and blobs are normally found in
        `'$HOME/.locals/share/lbry/lbrynet/blobfiles'`
        so `main_dir` would be `$HOME`, or `'/home/user'`
    size: int, optional
        It defaults to 1000.
        Maximum size in GB of `main_dir`.
        Ideally the downloaded media files and blobs never cross this limit.
    percent: float, optional
        It defaults to 90.
        Percentage of `size` that indicates a soft limit
        for the downloaded files.
        After this limit is crossed it will try to free space in `main_dir`
        by deleting older files and blobs, depending on the value
        of `which_delete`.
    never_delete: list of str, optional
        It defaults to `None`.
        If it exists it is a list with channel names.
        The content produced by these channels will not be deleted
        so the media files and blobs will remain in `main_dir`.

        This is slow as it needs to perform an additional search
        for the channel.
    what: str, optional
        It defaults to `'media'`, in which case only the full media file
        (mp4, mp3, mkv, etc.) is deleted.
        If it is `'blobs'` it will delete only the binary blobs.
        If it is `'both'` it will delete both the media file
        and the blobs.

        As long as the blobs are present, the content can be seeded
        to the network, and the full file can be restored.
        That is, while the blobs exist the file is not completely deleted.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        It returns `True` if the limit indicated by `size` and `percent`
        was crossed by the downloaded files, and some of the older files
        were successfully deleted to bring usage of `main_dir` within limits.

        It returns `False` if there is a problem, or if the limit
        was not crossed and thus there is nothing to clean up,
        or if after going through all claims, it failed to clear
        enough space to bring usage within limits.
    """
    if not funcs.server_exists(server=server):
        return False

    if (not main_dir or not isinstance(main_dir, str)
            or main_dir == "~" or not os.path.exists(main_dir)):
        main_dir = os.path.expanduser("~")
        print("Download directory should exist; "
              f"set to main_dir='{main_dir}'")

    if not isinstance(size, (int, float)) or size <= 0:
        size = 1000
        print("Max disk usage should be a positive number; "
              f"set to size={size} GB")

    if (not isinstance(percent, (int, float))
            or percent <= 0 or percent > 100):
        percent = 90
        print("Percentage should be a positive number from 0 to 100; "
              f"set to percent={percent} %")

    if never_delete and not isinstance(never_delete, (list, tuple)):
        print("Must be a list of channels that should never be deleted.")
        print(f"never_delete={never_delete}")
        return False

    if (not isinstance(what, str)
            or what not in ("media", "blobs", "both")):
        print(">>> Error: what can only be 'media', 'blobs', 'both'")
        print(f"what={what}")
        return False

    limit_crossed = measure_usage(main_dir=main_dir,
                                  size=size, percent=percent)
    if not limit_crossed:
        print("Nothing to clean up.")
        return False

    sorted_items = sort.sort_items(server=server)
    n_items = len(sorted_items)

    for it, item in enumerate(sorted_items, start=1):
        print(80 * "-")
        out = "{:4d}/{:4d}, {}, ".format(it, n_items, item["claim_name"])

        if never_delete:
            channel = srch_ch.find_channel(cid=item["claim_id"],
                                           full=False,
                                           server=server)
            if channel in never_delete:
                print(out + f"item from {channel} will not be deleted. "
                      "Skipping.")
                continue

        print(out + "item will be deleted.")
        clean.delete_single(cid=item["claim_id"], what=what,
                            server=server)

        limit_crossed = measure_usage(main_dir=main_dir, size=size,
                                      percent=percent)
        if not limit_crossed:
            print("Usage below limit. Stop deleting.")
            print()
            break
        print()

    if limit_crossed:
        print(">>> Went through all downloaded claims, "
              "and failed to clear enough space.")
        print("Terminating.")
        return False

    return True
