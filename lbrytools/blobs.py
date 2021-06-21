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
import json
import os
import requests
import shutil

import lbrytools.clean as clean
import lbrytools.download as dld
import lbrytools.funcs as funcs
import lbrytools.search as srch


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
    # output = subprocess.run(cmd,
    #                         capture_output=True,
    #                         check=True,
    #                         text=True)
    # if output.returncode == 1:
    #     print(f"Error: {output.stderr}")
    #     sys.exit(1)

    msg = {"method": cmd[1] + "_" + cmd[2],
           "params": {"blob_hash": blob}}
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

    funcs.check_lbry(server=server)
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


def count_blobs(uri=None, cid=None, name=None,
                blobfiles=None, print_msg=True, print_each=True,
                server="http://localhost:5279"):
    """Count blobs that have been downloaded from a claim.

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
    blobfiles: str, optional
        It defaults to `'$HOME/.local/share/lbry/lbrynet/blobfiles'`.
        The path to the directory where the blobs were downloaded.
        This is normally seen with `lbrynet settings get`, under `'data_dir'`.
        It can be any other directory if it is symbolically linked
        to it, such as `'/opt/lbryblobfiles'`
    print_msg: bool, optional
        It defaults to `True`, in which case it will print information
        on the found claim.
        If `print_msg=False`, it also implies `print_each=False`.
    print_each: bool, optional
        It defaults to `True`, in which case it will print all blobs
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
    dict
        A dictionary with several keys with information about the claim,
        and its blobs.
        - `'canonical_url'`, `'claim_id'`, `'name'`, `'channel'`, `'sd_hash'`:
          strings with the appropriate information of the claim.
        - `'all_present'`: a boolean value that is `True` if all blobs
          exist in the `blobfiles` path. It will be `False` if at least
          one blob is missing.
        - `'blobs'`: a list of lists, where each internal list refers to
          one blob of the claim. The internal lists have three elements,
          the first is the blob number, the second is a string with
          the 96-alphanumeric hash of the blob, and the third is a boolean
          value indicating if the blob is present `True` or not `False`
          in the `blobfiles` path.
          ::
              [0, "21d4258adcdde04c1f6416fdb537076ad54eb1...", True]
        - `'missing'`: a list of lists, similar to the `'blobs'` key.
          However, this list will only contain those sublists for missing
          blobs. If all blobs are already present, this is an empty list.
    dict
        If `uri`, `cid`, or `name` do not resolve to a valid claim
        that exists in the network, it will return a dictionary that holds
        the key `'error_not_found'`, and also keys for the input
        arguments, `'canonical_url'`, `'claim_id'`, and `'name'`.
        This may be the case if a mispelled URI or claim ID was input, or
        if a previously existing claim was removed from the network,
        which can be checked with the blockchain explorer.
    dict
        If the input resolves to a valid claim but the `'sd_hash'`
        is not present in the system, it will return a dictionary that holds
        the key `'error_no_sd_hash'`, and also keys for `'canonical_url'`,
        `'claim_id'`, `'name'`, `'channel'`, and `'sd_hash'`.
        This may be the case if for a previously downloaded claim
        the `'sd_hash'` blob was deleted.
    False
        If there is a problem, like non existing blobfiles directory,
        it will return `False`.
    """
    if (not blobfiles or not isinstance(blobfiles, str)
            or not os.path.exists(blobfiles)):
        print("Count the blobs of the claim from the blobfiles directory")
        print(f"blobfiles={blobfiles}")
        print("This is typically '$HOME/.local/share/lbry/lbrynet/blobfiles'")

        home = os.path.expanduser("~")
        blobfiles = os.path.join(home,
                                 ".local", "share",
                                 "lbry", "lbrynet", "blobfiles")

        if not os.path.exists(blobfiles):
            print(f"Blobfiles directory does not exist: {blobfiles}")
            return False

    item = srch.search_item(uri=uri, cid=cid, name=name,
                            server=server)
    if not item:
        return {"error_not_found": "item was not found in the network",
                "canonical_url": uri,
                "claim_id": cid,
                "name": name}

    c_uri = item["canonical_url"]
    c_cid = item["claim_id"]
    c_name = item["name"]

    if "signing_channel" in item and "name" in item["signing_channel"]:
        ch_full = item["signing_channel"]["canonical_url"].lstrip("lbry://")
        c_channel = ch_full.replace("#", ":")
    else:
        c_channel = "@_Unknown_"

    sd_hash = item["value"]["source"]["sd_hash"]

    if print_msg:
        print(f"canonical_url: {c_uri}")
        print(f"claim_id: {c_cid}")
        print(f"name: {c_name}")
        print(f"channel: {c_channel}")
        print(f"sd_hash: {sd_hash}")

    sd_hash_f = os.path.join(blobfiles, sd_hash)

    # if not os.path.exists(sd_hash_f) or sd_hash not in list_all_blobs:
    if not os.path.exists(sd_hash_f):
        print(f">>> 'sd_hash' blob not in directory: {blobfiles}")
        print(">>> Start downloading the claim, or redownload it.")
        return {"error_no_sd_hash": "'sd_hash' blob not in directory "
                                    f"{blobfiles}",
                "canonical_url": c_uri,
                "claim_id": c_cid,
                "name": c_name,
                "channel": c_channel,
                "sd_hash": sd_hash}

    fd = open(sd_hash_f)
    lines = fd.readlines()
    fd.close()

    blobs = json.loads(lines[0])
    n_blobs = len(blobs["blobs"]) - 1

    if print_msg:
        print(f"Total blobs: {n_blobs}")

    present_list = []
    blob_list = []
    blob_missing = []

    for blob in blobs["blobs"]:
        if "blob_hash" not in blob:
            continue

        num = blob["blob_num"]
        blob_hash = blob["blob_hash"]
        present = os.path.exists(os.path.join(blobfiles, blob_hash))
        present_list.append(present)
        blob_list.append([num, blob_hash, present])

        if not present:
            blob_missing.append([num, blob_hash, present])

        if print_msg and print_each:
            print("{:3d}/{:3d}, {}, {}".format(num, n_blobs,
                                               blob_hash,
                                               present))

    all_present = all(present_list)

    if print_msg:
        print(f"All blob files present: {all_present}")

    blob_info = {"canonical_url": c_uri,
                 "claim_id": c_cid,
                 "name": c_name,
                 "channel": c_channel,
                 "sd_hash": sd_hash,
                 "all_present": all_present,
                 "blobs": blob_list,
                 "missing": blob_missing}
    return blob_info


def count_blobs_all(blobfiles=None, print_each=False,
                    start=1, end=0,
                    server="http://localhost:5279"):
    """Count all blobs from all downloaded claims.

    Parameters
    ----------
    blobfiles: str
        It defaults to `'$HOME/.local/share/lbry/lbrynet/blobfiles'`.
        The path to the directory where the blobs were downloaded.
        This is normally seen with `lbrynet settings get`, under `'data_dir'`.
        It can be any other directory if it is symbolically linked
        to it, such as `'/opt/lbryblobfiles'`
    print_each: bool, optional
        It defaults to `False`.
        If it is `True` it will print all blobs
        that belong to the claim, and whether each of them is already
        in `blobfiles`.
    start: int, optional
        It defaults to 1.
        Count the blobs from claims starting from this index
        in the list of items.
    end: int, optional
        It defaults to 0.
        Count the blobs from claims until and including this index
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
    list of dict
        It returns a list of dicts where each dictionary corresponds
        to the information from a single claim.
        The dictionary contains two keys
        - `'num'`: an integer from 1 up to the last item processed.
        - `'blob_info'`: the dictionary output from the `count_blobs` method.
          In rare cases this may be a single boolean value `False`.
    """
    if (not blobfiles or not isinstance(blobfiles, str)
            or not os.path.exists(blobfiles)):
        print("Count the blobs of the claim from the blobfiles directory")
        print(f"blobfiles={blobfiles}")
        print("This is typically '$HOME/.local/share/lbry/lbrynet/blobfiles'")

        home = os.path.expanduser("~")
        blobfiles = os.path.join(home,
                                 ".local", "share",
                                 "lbry", "lbrynet", "blobfiles")

        if not os.path.exists(blobfiles):
            print(f"Blobfiles directory does not exist: {blobfiles}")
            return False

    items = srch.sort_items(server=server)
    n_items = len(items)
    print()

    print("Count all blob files")
    print(80 * "-")

    blob_all_info = []
    claims_blobs_complete = 0
    claims_blobs_incomplete = 0
    claims_no_sd_hash = 0
    claims_not_found = 0
    claims_other_error = 0

    for it, item in enumerate(items, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        print(f"Claim {it}/{n_items}, {item['claim_name']}")
        blob_info = count_blobs(cid=item["claim_id"],
                                blobfiles=blobfiles,
                                print_each=print_each,
                                server=server)

        info = {"num": it,
                "blob_info": blob_info}
        blob_all_info.append(info)

        if blob_info:
            if "all_present" in blob_info and blob_info["all_present"]:
                claims_blobs_complete += 1
            elif "all_present" in blob_info and not blob_info["all_present"]:
                claims_blobs_incomplete += 1

            if "error_no_sd_hash" in blob_info:
                claims_no_sd_hash += 1
            if "error_not_found" in blob_info:
                claims_not_found += 1
        else:
            claims_other_error += 1
        print()

    print(f"claims with complete blobs: {claims_blobs_complete}")
    print(f"claims with incomplete blobs: {claims_blobs_incomplete}")
    print(f"claims with no 'sd_hash' present: {claims_no_sd_hash} "
          "(restart download)")
    print(f"invalid claims: {claims_not_found} "
          "(no valid URI or claim_id, maybe removed from the network)")
    print(f"claims with other errors: {claims_other_error}")
    print(8*"-")
    total = (claims_blobs_complete + claims_blobs_incomplete
             + claims_no_sd_hash + claims_not_found + claims_other_error)
    total_valid = (claims_blobs_complete + claims_blobs_incomplete
                   + claims_no_sd_hash)
    total_invalid = claims_not_found + claims_other_error
    print(f"total claims processed: {total}")
    print(f"total valid claims: {total_valid} "
          "(minimum number of 'sd_hash' blobs that must exist)")
    print(f"invalid claims: {total_invalid} "
          "(should be deleted including all their blobs)")

    return blob_all_info


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
    blob_info = count_blobs(uri=uri, cid=cid, name=name,
                            blobfiles=blobfiles, print_each=print_each,
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

    blob_info = count_blobs(uri=uri, cid=cid, name=name,
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

    items = srch.sort_items(channel=channel,
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
