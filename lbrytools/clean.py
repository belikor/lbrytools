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
"""Functions to clean downloaded content from the LBRY network."""
import os
import requests
import shutil

from lbrytools.search import search_item
from lbrytools.search import sort_items
from lbrytools.search import find_channel


def delete_single(uri=None, cid=None, name=None,
                  what="media",
                  server="http://localhost:5279"):
    """Delete a single file, and optionally the downloaded blobs.

    As long as the blobs are present, the content can be seeded
    to the network, and the full file can be restored.
    That is, while the blobs exist the file is not completely deleted.

    Parameters
    ----------
    uri: str
        A unified resource identifier (URI) to a claim on the LBRY network.
        It can be full or partial.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            uri = '@MyChannel#3/some-video-name#2'
            uri = 'some-video-name'

        The URI is also called the `'canonical_url'` of the claim.
    cid: str, optional
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            name = 'some-video-name'
    what: str, optional
        It defaults to `'media'`, in which case only the full media file
        (mp4, mp3, mkv, etc.) is deleted.
        If it is `'blobs'`, it will delete only the blobs.
        If it is `'both'`, it will delete both the media file
        and the blobs.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        It returns `True` if the claim was deleted successfully.
        If there is a problem or non existing claim, it will return `False`.
    """
    if not (uri or cid or name):
        print("Delete item by 'URI', 'claim_id', or 'name'.")
        print(f"uri={uri}, cid={cid}, name={name}")
        return False

    if (not isinstance(what, str)
            or what not in ("media", "blobs", "both")):
        print(">>> Error: what can only be 'media', 'blobs', 'both'")
        print(f"what={what}")
        return False

    item = search_item(uri=uri, cid=cid, name=name,
                       server=server)
    if not item:
        print(f"uri={uri}, cid={cid}, name={name}")
        return False

    _uri = item["canonical_url"]
    _claim_id = item["claim_id"]
    _name = item["name"]
    # channel = item["signing_channel"]["canonical_url"]

    cmd = ["lbrynet",
           "file",
           "list",
           "--claim_id=" + _claim_id]
    # output = subprocess.run(cmd,
    #                         capture_output=True,
    #                         check=True,
    #                         text=True)
    # if output.returncode == 1:
    #     print(f"Error: {output.stderr}")
    #     sys.exit(1)

    # data = json.loads(output.stdout)

    msg = {"method": cmd[1] + "_" + cmd[2],
           "params": {"claim_id": _claim_id}}
    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    data = output["result"]

    if not data["items"] or data["total_items"] < 1:
        print("No item found locally, probably already deleted.")
        print(f"uri={uri}, cid={cid}, name={name}")
        return False

    item = data["items"][0]

    path = item["download_path"]
    blobs = int(item["blobs_completed"])
    blobs_full = int(item["blobs_in_stream"])

    print(f"canonical_url: {_uri}")
    print(f"claim_id: {_claim_id}")
    print(f"Blobs found: {blobs} of {blobs_full}")

    if what in "media":
        print(f"Remove media file: {path}")

        if path:
            os.remove(path)
            print("Media file deleted")
        else:
            print("No media found locally, probably already deleted.")
        print()
        return True

    cmd_name = ["lbrynet",
                "file",
                "delete",
                "--claim_name=" + _name]
    cmd_id = cmd_name[:]
    cmd_id[3] = "--claim_id=" + _claim_id

    if what in "blobs":
        print("Remove blobs")
    elif what in "both":
        print("Remove both, blobs and file")
        cmd_id.append("--delete_from_download_dir")
        cmd_name.append("--delete_from_download_dir")

    print("Remove: " + " ".join(cmd_id))
    print("Remove: " + " ".join(cmd_name))

    # output = subprocess.run(cmd_id,
    #                         capture_output=True,
    #                         check=True,
    #                         text=True)
    # if output.returncode == 1:
    #     print(f"Error: {output.stderr}")
    #     sys.exit(1)

    # data = json.loads(output.stdout)

    msg = {"method": cmd_id[1] + "_" + cmd_id[2],
           "params": {"claim_id": _claim_id}}

    if what in "both":
        msg["params"]["delete_from_download_dir"] = True

    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    print("Blobs deleted")
    print()

    return True


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

    msg = [limit * " " + "v"]
    msg.append("|" + m*"=" + (spaces-1-m)*"." + "|" + f" {size:.1f} GB")

    if actual_percent > 100:
        m = spaces + 13
        msg[1] = "|" + (spaces-1)*"=" + "|" + f" {size:.1f} GB"

    msg.append(m*" " + "^")

    print("\n".join(msg))


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

    if actual_percent >= percent:
        print(">>> Downloads are above the indicated limit.")
        if bar:
            pr_bar(size=size, percent=percent, actual_percent=actual_percent)
        return True

    print("Downloads are within limits.")
    if bar:
        pr_bar(size=size, percent=percent, actual_percent=actual_percent)
    return False


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

    sorted_items = sort_items(server=server)
    n_items = len(sorted_items)

    for it, item in enumerate(sorted_items, start=1):
        print(80 * "-")
        out = "{:4d}/{:4d}, {}, ".format(it, n_items, item["claim_name"])

        if never_delete:
            channel = find_channel(cid=item["claim_id"], full=False,
                                   server=server)
            if channel in never_delete:
                print(out + f"item from {channel} will not be deleted. "
                      "Skipping.")
                continue

        print(out + "item will be deleted.")
        delete_single(cid=item["claim_id"], what=what,
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


def remove_media(never_delete=None,
                 server="http://localhost:5279"):
    """Remove all media files but leave the binary blobs.

    This function is intended for systems that will only seed content.
    It should be run after downloading various claims, for example,
    with `download_single` or `ch_download_latest_multi`.
    It will delete only the media files (mp4, mp3, mkv, etc.)
    but leave the blobs intact to continue seeding them to the network.

    Parameters
    ----------
    never_delete: list of str, optional
        It defaults to `None`.
        If it exists it is a list with channel names.
        The content produced by these channels will not be deleted
        so the media files and blobs will remain in `main_dir`.

        Using this parameter is slow as it needs to perform
        an additional search for the channel.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        It returns `True` if some of the older files
        were successfully deleted.
        It returns `False` if there is a problem, or if there
        was nothing to clean up.
    """
    if never_delete and not isinstance(never_delete, (list, tuple)):
        print("Must be a list of channels that should never be deleted.")
        print(f"never_delete={never_delete}")
        return False

    print(80 * "-")
    print("Delete all media files")

    items = sort_items(server=server)
    n_items = len(items)

    for it, item in enumerate(items, start=1):
        out = "{:4d}/{:4d}, {}, ".format(it, n_items, item["claim_name"])
        if never_delete:
            channel = find_channel(cid=item["claim_id"], full=False,
                                   server=server)
            if not channel:
                continue

            channel = channel.lstrip("@")
            skip = False

            for safe_channel in never_delete:
                if channel in safe_channel:
                    skip = True
                    break

            if skip:
                print(out + f"item from {channel} will not be deleted. "
                      "Skipping.")
                continue

        path = item["download_path"]
        if path:
            os.remove(path)
            print(out + f"delete {path}")
        else:
            print(out + "no media found locally, probably already deleted.")

    print("Media files deleted")
    return True
