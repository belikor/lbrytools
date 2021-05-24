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
"""Functions to help use with blobs from LBRY content."""
import os
import requests

from lbrytools.funcs import check_lbry


def get_blobs(blobfiles=None, action="get",
              start=1, end=0,
              server="http://localhost:5279"):
    """Refresh all binary blobs from the blobfiles directory.

    Parameters
    ----------
    blobfiles: str
        The path to the directory that stores all blob files.
        In Linux this is normally
        `'$HOME/.locals/share/lbry/lbrynet/blobfiles'`
        but it can be any other directory if it is symbolically linked
        to it, such as `/opt/lbryblobfiles`
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
        print("Get blobs from the blobfiles directory")
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

    check_lbry()
    list_blobs = os.listdir(blobfiles)
    n_blobs = len(list_blobs)

    for it, item in enumerate(list_blobs, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        out = "{:6d}/{:6d}, ".format(it, n_blobs)

        cmd = ["lbrynet",
               "blob",
               "get",
               item]

        if action in "announce":
            cmd[2] = "announce"

        print(out + " ".join(cmd))
        # output = subprocess.run(cmd,
        #                         capture_output=True,
        #                         check=True,
        #                         text=True)
        # if output.returncode == 1:
        #     print(f"Error: {output.stderr}")
        #     sys.exit(1)

        msg = {"method": cmd[1] + "_" + cmd[2],
               "params": {"blob_hash": item}}
        output = requests.post(server, json=msg).json()

        if "error" in output:
            print(output["error"]["data"]["name"])

        if action in "both":
            cmd[2] = "announce"
            print(out + " ".join(cmd))
            # output = subprocess.run(cmd,
            #                         capture_output=True,
            #                         check=True,
            #                         text=True)
            # if output.returncode == 1:
            #     print(f"Error: {output.stderr}")
            #     sys.exit(1)

            msg = {"method": cmd[1] + "_" + cmd[2],
                   "params": {"blob_hash": item}}
            output = requests.post(server, json=msg).json()

            if "error" in output:
                print(output["error"]["data"]["name"])

    return True
