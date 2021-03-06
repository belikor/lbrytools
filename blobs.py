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

import lbrytools.funcs as funcs
import lbrytools.search as srch
import lbrytools.sort as sort


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
    if not funcs.server_exists(server=server):
        return False

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


def count_blobs_all(blobfiles=None, channel=None,
                    start=1, end=0,
                    print_msg=False, print_each=False,
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
    channel: str, optional
        It defaults to `None`.
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    print_msg: bool, optional
        It defaults to `True`, in which case it will print information
        on the found claim.
        If `print_msg=False`, it also implies `print_each=False`.
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
    False
        If there is a problem, like non existing blobfiles directory,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

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

    if channel:
        print(f"Count all blob files for: {channel}")
    else:
        print("Count all blob files")
    print(80 * "-")
    print(f"Blobfiles: {blobfiles}")

    blob_all_info = []
    claims_blobs_complete = 0
    claims_blobs_incomplete = 0
    claims_no_sd_hash = 0
    claims_not_found = 0
    claims_other_error = 0
    n_blobs = 0

    for it, item in enumerate(items, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        if print_msg:
            print(f"Claim {it}/{n_items}, {item['claim_name']}")
        blob_info = count_blobs(cid=item["claim_id"],
                                blobfiles=blobfiles, print_msg=print_msg,
                                print_each=print_each,
                                server=server)
        if print_msg or "error_not_found" in blob_info:
            print()

        info = {"num": it,
                "blob_info": blob_info}
        blob_all_info.append(info)

        if blob_info:
            if "all_present" in blob_info and blob_info["all_present"]:
                claims_blobs_complete += 1
                n_blobs += 1  # for the 'sd_hash'
                n_blobs += len(blob_info["blobs"])
            elif "all_present" in blob_info and not blob_info["all_present"]:
                claims_blobs_incomplete += 1
                n_blobs += 1  # for the 'sd_hash'
                n_blobs += len(blob_info["blobs"])

            if "error_no_sd_hash" in blob_info:
                claims_no_sd_hash += 1
            if "error_not_found" in blob_info:
                claims_not_found += 1
        else:
            claims_other_error += 1

    print(f"claims with complete blobs: {claims_blobs_complete}")
    print(f"claims with incomplete blobs: {claims_blobs_incomplete} "
          "(continue download)")
    print(f"claims with no 'sd_hash' present: {claims_no_sd_hash} "
          "(restart download)")
    print(f"invalid claims: {claims_not_found} "
          "(no valid URI or claim ID; possibly removed from the network)")
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
    print(f"blobs that should exist for these claims: {n_blobs}")

    return blob_all_info
