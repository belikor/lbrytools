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
"""Functions to perform a few actions with the blobs from LBRY content."""
import os
import requests

import lbrytools.download as dld
import lbrytools.clean as clean
import lbrytools.blobs as blobs


def blob_get(blob=None, action="get", out="",
             server="http://localhost:5279"):
    """Get or announce one blob from the LBRY network.

    At the moment it cannot be used with missing blobs;
    the command hangs and never timeouts.
    It can only be used with a blob that is already downloaded.

    This bug is reported in lbryio/lbry-sdk, issue #2070.

    Therefore, at this moment this function is not very useful.

    Parameters
    ----------
    blob: str
        The 96-alphanumeric character that denotes a blob.
        This will be downloaded to the `blobfiles` directory,
        which in Linux is normally
        `'$HOME/.locals/share/lbry/lbrynet/blobfiles'`
    action: str, optional
        It defaults to `'get'`, in which case it downloads
        the specified `blob`.
        It can be `'get'`, `'announce'`, or `'both'`.
    out: str, optional
        It defaults to an empty string `""`.
        It is an arbitrary string that will be printed before the string
        `'lbrynet blob get <blob>'`.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        It returns `True` if it finished downloading or announcing
        the indicated blob successfully.
        If there is a problem or non existing blob hash,
        it will return `False`.
    """
    if not isinstance(blob, str) or len(blob) < 96:
        print(">>> Error: blob must be a 96-character alphanumeric string")
        print(f"blob={blob}")
        return False

    if (not isinstance(action, str)
            or action not in ("get", "announce", "both")):
        print(">>> Error: action can only be 'announce', 'get', 'both'")
        print(f"action={action}")
        return False

    cmd = ["lbrynet",
           "blob",
           "get",
           blob]

    if action in "announce":
        cmd[2] = "announce"

    print(out + " ".join(cmd))

    msg = {"method": cmd[1] + "_" + cmd[2],
           "params": {"blob_hash": blob}}
    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(output["error"]["data"]["name"])

    if action in "both":
        cmd[2] = "announce"
        print(out + " ".join(cmd))

        msg = {"method": cmd[1] + "_" + cmd[2],
               "params": {"blob_hash": blob}}
        output = requests.post(server, json=msg).json()

        if "error" in output:
            print(output["error"]["data"]["name"])

    return True


def blobs_action(blobfiles=None, action="get",
                 start=1, end=0,
                 server="http://localhost:5279"):
    """Get or announce all binary blobs from the blobfiles directory.

    Parameters
    ----------
    blobfiles: str
        It defaults to `'$HOME/.local/share/lbry/lbrynet/blobfiles'`.
        The path to the directory where the blobs were downloaded.
        This is normally seen with `lbrynet settings get`, under `'data_dir'`.
        It can be any other directory if it is symbolically linked
        to it, such as `'/opt/lbryblobfiles'`
    action: str, optional
        It defaults to `'get'`, in which case it re-downloads all blobs
        in the `blobfiles` directory.
        It can be `'get'`, `'announce'`, or `'both'`.
    start: int, optional
        It defaults to 1.
        Operate on the blob starting from this index in the
        directory of blobs `blobfiles`.
    end: int, optional
        It defaults to 0.
        Operate until and including this index in the list of blobs
        in the directory of blobs `blobfiles`.
        If it is 0, it is the same as the last index in the list.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        It returns `True` if it finished refreshing all blobs successfully
        although this may take some time if all blobs are considered.
        If there is a problem or non existing blobfiles directory,
        it will return `False`.
    """
    if (not blobfiles or not isinstance(blobfiles, str)
            or not os.path.exists(blobfiles)):
        print("Perform an action with the blobs from the blobfiles directory")
        print(f"blobfiles={blobfiles}, action={action}")
        print("This is typically '$HOME/.local/share/lbry/lbrynet/blobfiles'")

        home = os.path.expanduser("~")
        blobfiles = os.path.join(home,
                                 ".local", "share",
                                 "lbry", "lbrynet", "blobfiles")

        if not os.path.exists(blobfiles):
            print(f"Blobfiles directory does not exist: {blobfiles}")
            return False

    if (not isinstance(action, str)
            or action not in ("get", "announce", "both")):
        print(">>> Error: action can only be 'announce', 'get', 'both'")
        print(f"action={action}")
        return False

    list_blobs = os.listdir(blobfiles)
    n_blobs = len(list_blobs)

    for it, blob in enumerate(list_blobs, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        out = "{:6d}/{:6d}, ".format(it, n_blobs)

        blob_get(blob=blob, action=action, out=out,
                 server=server)

    return True


def redownload_blobs(uri=None, cid=None, name=None,
                     ddir=None, own_dir=True,
                     blobfiles=None, print_each=False,
                     server="http://localhost:5279"):
    """Redownload the blobs from a claim.

    If all blobs from a given claim are present, the function does nothing.

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
    ddir: str, optional
        It defaults to `$HOME`.
        The path to the download directory.
    own_dir: bool, optional
        It defaults to `True`, in which case it places the downloaded
        content inside a subdirectory named after the channel in `ddir`.
    blobfiles: str, optional
        It defaults to `'$HOME/.local/share/lbry/lbrynet/blobfiles'`.
        The path to the directory where the blobs were downloaded.
        This is normally seen with `lbrynet settings get`, under `'data_dir'`.
        It can be any other directory if it is symbolically linked
        to it, such as `'/opt/lbryblobfiles'`
    print_each: bool, optional
        It defaults to `False`.
        If it is `True` it will not print all blobs
        that belong to the claim, and whether each of them is already
        in `blobfiles`.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        It returns `True` if all blobs are already present in the system
        so nothing needs to be downloaded.
        It returns `False` if the item does not exist,
        of if at least one blob was downloaded.

    Bug
    ---
    At the moment downloading missing blobs is not possible;
    the command hangs and never timeouts.
    ::
        lbrynet blob get <hash>

    This bug is reported in lbryio/lbry-sdk, issue #2070.

    If the bug is solved, `blob_get` could be called with the missing blob
    hash to only get that piece.
    """
    blob_info = blobs.count_blobs(uri=uri, cid=cid, name=name,
                                  blobfiles=blobfiles,
                                  print_each=print_each,
                                  server=server)

    if "error_not_found" in blob_info:
        return False

    print(80 * "-")
    if "error_no_sd_hash" in blob_info:
        print(blob_info["error_no_sd_hash"]
              + "; start download from the start.")
    elif blob_info["all_present"]:
        print("All blobs files present, nothing to download.")
        return True
    else:
        print("Blobs missing; redownload claim.")
    print()

    # If the bug #2070 is solved, this could be run.
    # print("Blobs missing; redownload blobs")
    # for blob in blob_info["missing"]:
    #     out = f"{blob[0]}, "
    #     blob_get(blob=blob[1], action="get", out=out,
    #              server=server)

    # The missing blobs will only be downloaded if the media file
    # is not present so we must make sure it is deleted.
    # print("Blobs missing; redownload claim")
    print("Ensure the media file is deleted.")
    clean.delete_single(cid=blob_info["claim_id"], what="media",
                        server=server)
    print()
    dld.download_single(cid=blob_info["claim_id"],
                        ddir=ddir, own_dir=own_dir,
                        server=server)

    return False
