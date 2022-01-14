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
"""Functions to help move the blobs from downloaded LBRY content."""
import os
import shutil

import lbrytools.funcs as funcs
import lbrytools.sort as sort
import lbrytools.blobs as blobs


def blobs_move(uri=None, cid=None, name=None,
               move_dir=None, blobfiles=None, print_missing=False,
               action="copy",
               server="http://localhost:5279"):
    """Copy or move the binary blobs of a downloaded claim.

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
    move_dir: str, optional
        It defaults to `$HOME`.
        The path to where the blobs will be copied or moved.
        They will be placed inside their own subdirectory which will be named
        after the channel's name, and the claim's name.
    blobfiles: str, optional
        It defaults to `'$HOME/.local/share/lbry/lbrynet/blobfiles'`.
        The path to the directory where the blobs were downloaded.
        This is normally seen with `lbrynet settings get`, under `'data_dir'`.
        It can be any other directory if it is symbolically linked
        to it, such as `'/opt/lbryblobfiles'`
    print_missing: bool, optional
        It defaults to `False`.
        If it is `True` it will print all blobs
        that don't exist in `blobfiles`, and thus that cannot be copied
        or moved to `move_dir`.
    action: str, optional
        It defaults to `'copy'`, in which case the blobs are copied to the
        `move_dir` path.
        If it is `'move'` the blobs will be moved, so they won't be
        in `blobfiles` any more.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        Returns `True` if the blobs were copied successfully.

        It returns `False` if the claim does not exist,
        or if the `'sd_hash'` does not exist in the `blobfiles` directory,
        of if at least one blob is missing.

        The last point may mean that the claim was not downloaded fully,
        so it needs to be redownloaded.
    """
    if not funcs.server_exists(server=server):
        return False

    if (not move_dir or not isinstance(move_dir, str)
            or move_dir == "~" or not os.path.exists(move_dir)):
        move_dir = os.path.expanduser("~")
        print("Destination directory should exist; "
              f"set to move_dir='{move_dir}'")

    if (not blobfiles or not isinstance(blobfiles, str)
            or not os.path.exists(blobfiles)):
        print("Copy or move the blobs from the blobfiles directory")
        print(f"blobfiles={blobfiles}")
        print("This is typically '$HOME/.local/share/lbry/lbrynet/blobfiles'")

        home = os.path.expanduser("~")
        blobfiles = os.path.join(home,
                                 ".local", "share",
                                 "lbry", "lbrynet", "blobfiles")

        if not os.path.exists(blobfiles):
            print(f"Blobfiles directory does not exist: {blobfiles}")
            return False

    if (not isinstance(action, str)
            or action not in ("copy", "move")):
        print(">>> Error: action can only be 'copy', 'move'")
        print(f"action={action}")
        return False

    blob_info = blobs.count_blobs(uri=uri, cid=cid, name=name,
                                  blobfiles=blobfiles, print_each=False,
                                  server=server)

    print(80 * "-")
    if "error_not_found" in blob_info or "error_no_sd_hash" in blob_info:
        print("Not copying or moving blobs.")
        return False

    name = blob_info["name"]
    channel = blob_info["channel"]
    subdir = os.path.join(move_dir, channel + "_" + name)

    if not os.path.exists(subdir):
        try:
            os.mkdir(subdir)
        except (FileNotFoundError, PermissionError) as err:
            print(f"Cannot open directory for writing; {err}")
            return False

    sd_hash_f = os.path.join(blobfiles, blob_info["sd_hash"])

    if "copy" in action:
        shutil.copy(sd_hash_f, subdir)

        for blob in blob_info["blobs"]:
            num = blob[0]
            hsh = blob[1]

            blob_f = os.path.join(blobfiles, hsh)
            if os.path.exists(blob_f):
                shutil.copy(blob_f, subdir)
            else:
                if print_missing:
                    print(f"{num:3d}, {hsh}, missing, not copied")
        print("Finished copying blobs.")

    elif "move" in action:
        shutil.move(sd_hash_f, subdir)

        for blob in blob_info["blobs"]:
            num = blob[0]
            hsh = blob[1]

            blob_f = os.path.join(blobfiles, hsh)
            if os.path.exists(blob_f):
                shutil.move(blob_f, subdir)
            else:
                if print_missing:
                    print(f"{num:3d}, {hsh}, missing, not moved")
        print("Finished moving blobs.")

    if not blob_info["all_present"]:
        print("Some blobs are missing, wait for the download to complete, "
              "or redownload this claim.")
        return False

    return True


def blobs_move_all(move_dir=None, blobfiles=None, print_missing=False,
                   action="copy",
                   channel=None, start=1, end=0,
                   server="http://localhost:5279"):
    """Copy or move all blobs of all downloaded claims.

    Parameters
    ----------
    move_dir: str, optional
        It defaults to `$HOME`.
        The path to where the blobs will be copied or moved.
        They will be placed inside their own subdirectory which will be named
        after the channel's name, and the claim's name.
    blobfiles: str, optional
        It defaults to `'$HOME/.local/share/lbry/lbrynet/blobfiles'`.
        The path to the directory where the blobs were downloaded.
        This is normally seen with `lbrynet settings get`, under `'data_dir'`.
        It can be any other directory if it is symbolically linked
        to it, such as `'/opt/lbryblobfiles'`
    print_missing: bool, optional
        It defaults to `False`.
        If it is `True` it will print all blobs
        that don't exist in `blobfiles`, and thus that cannot be copied
        or moved to `move_dir`.
    action: str, optional
        It defaults to `'copy'`, in which case the blobs are copied to the
        `move_dir` path.
        If it is `'move'` the blobs will be moved, so they won't be
        in `blobfiles` any more.
    channel: str, optional
        It defaults to `None`.
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    start: int, optional
        It defaults to 1.
        Move the blobs from claims starting from this index
        in the list of items.
    end: int, optional
        It defaults to 0.
        Move the blobs from claims until and including this index
        in the list of items.
        If it is 0, it is the same as the last index in the list.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of bool
        Each item in the list refers to a claim.

        It is `True` if the blobs were copied successfully.

        It is `False` if the claim does not exist,
        or if the `'sd_hash'` does not exist in the `blobfiles` directory,
        of if at least one blob is missing.

        The last point may mean that the claim was not downloaded fully,
        so it needs to be redownloaded.
    """
    if not funcs.server_exists(server=server):
        return False

    if (not move_dir or not isinstance(move_dir, str)
            or move_dir == "~" or not os.path.exists(move_dir)):
        move_dir = os.path.expanduser("~")
        print("Destination directory should exist; "
              f"set to move_dir='{move_dir}'")

    if (not blobfiles or not isinstance(blobfiles, str)
            or not os.path.exists(blobfiles)):
        print("Copy or move the blobs from the blobfiles directory")
        print(f"blobfiles={blobfiles}")
        print("This is typically '$HOME/.local/share/lbry/lbrynet/blobfiles'")

        home = os.path.expanduser("~")
        blobfiles = os.path.join(home,
                                 ".local", "share",
                                 "lbry", "lbrynet", "blobfiles")

        if not os.path.exists(blobfiles):
            print(f"Blobfiles directory does not exist: {blobfiles}")
            return False

    if channel and not isinstance(channel, str):
        print("Channel must be a string. Set to 'None'.")
        print(f"channel={channel}")
        channel = None

    if channel:
        if not channel.startswith("@"):
            channel = "@" + channel

    items = sort.sort_items(channel=channel,
                            server=server)
    if not items:
        return False

    n_items = len(items)
    print()

    list_blobs_info = []

    print("Copy/move all blob files")
    print(80 * "-")

    for it, item in enumerate(items, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        print(f"Claim {it}/{n_items}, {item['claim_name']}")
        blob_m = blobs_move(cid=item["claim_id"],
                            move_dir=move_dir, blobfiles=blobfiles,
                            print_missing=print_missing,
                            action=action,
                            server=server)
        list_blobs_info.append(blob_m)
        print()

    return list_blobs_info
