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
"""Functions to help with searching claims in the LBRY network."""
import os
import requests


def check_repost(item):
    """Check if the item is a repost, and return the original item.

    A claim that is just the repost of another cannot be downloaded directly,
    so we replace the input item with the original source item.

    Parameters
    ----------
    item: dict
        A dictionary with the information on an item, obtained
        from `lbrynet resolve` or `lbrynet claim search`.

    Returns
    -------
    dict
        The original `item` dictionary if it is not a repost,
        or its `'reposted_claim'` dictionary, if it is.
    """
    if "reposted_claim" in item:
        _uri = item["canonical_url"]

        item = item["reposted_claim"]
        uri = item["canonical_url"]

        print("This is a repost.")
        print(f"canonical_url:  {_uri}")
        print(f"reposted_claim: {uri}")
        print()

    return item


def search_item_uri(uri=None, print_error=True,
                    server="http://localhost:5279"):
    """Find a single item in the LBRY network, resolving the URI.

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
    print_error: bool, optional
        It defaults to `True`, in which case it will print the error message
        that `lbrynet resolve` returns.
        By setting this value to `False` no messages will be printed;
        this is useful inside other functions when we want to limit
        the terminal output.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        Returns the dictionary that represents the `claim`
        that was found matching the URI.
    False
        If the dictionary has the `'error'` key, it will print the contents
        of this key, and return `False`.
    """
    if not uri or not isinstance(uri, str):
        m = ["Search by URI, full or partial.",
             "lbry://@MyChannel#3/some-video-name#2",
             "       @MyChannel#3/some-video-name#2",
             "                    some-video-name"]
        print("\n".join(m))
        print(f"uri={uri}")
        return False

    cmd = ["lbrynet",
           "resolve",
           uri]

    msg = {"method": cmd[1],
           "params": {"urls": uri}}

    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    item = output["result"][uri]

    if "error" in item:
        if print_error:
            error = item["error"]
            if "name" in error:
                print(">>> Error: {}, {}".format(error["name"], error["text"]))
            else:
                print(">>> Error: {}".format(error))
            print(">>> Check that the URI is correct, "
                  "or that the claim hasn't been removed from the network.")
        return False

    # The found item may be a repost so we check it,
    # and return the original source item.
    item = check_repost(item)
    return item


def search_item_cid(cid=None, name=None, offline=False, print_error=True,
                    server="http://localhost:5279"):
    """Find a single item in the LBRY network, resolving the claim id or name.

    If both `cid` and `name` are given, `cid` is used.

    Parameters
    ----------
    cid: str
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            name = 'some-video-name'
    offline: bool, optional
        It defaults to `False`, in which case it will use
        `lbrynet claim search` to search `cid` or `name` in the online
        database.

        If it is `True` it will use `lbrynet file list` to search
        `cid` or `name` in the offline database.
        This is required for 'invalid' claims, which have been removed from
        the online database and only exist locally.
    print_error: bool, optional
        It defaults to `True`, in which case it will print an error message
        if the claim is not found.
        By setting this value to `False` no messages will be printed;
        this is helpful if this function is used inside other functions,
        and we want to limit the terminal output.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        Returns the dictionary that represents the `claim`
        that was found matching the `name` or `cid`.
    False
        If the dictionary seems to have no items found, it will print
        an error message and return `False`.
    """
    if (name and (not isinstance(name, str)
                  or "#" in name or ":" in name or "@" in name)
            or cid and (not isinstance(cid, str)
                        or "#" in cid or ":" in cid or "@" in cid)
            or not (name or cid)):
        m = ["Search by 'name' or 'claim_id' only.",
             "lbry://@MyChannel#3/some-video-name#2",
             "                    ^-------------^",
             "                          name"]
        print("\n".join(m))
        print(f"cid={cid}")
        print(f"name={name}")
        return False

    if offline:
        cmd = ["lbrynet",
               "file",
               "list",
               "--claim_name='{}'".format(name)]
        if cid:
            cmd[3] = "--claim_id=" + cid

        msg = {"method": cmd[1] + "_" + cmd[2],
               "params": {"claim_name": name}}
    else:
        cmd = ["lbrynet",
               "claim",
               "search",
               "--name={}".format(name)]
        if cid:
            cmd[3] = "--claim_ids=" + cid

        msg = {"method": cmd[1] + "_" + cmd[2],
               "params": {"name": name}}

    if cid:
        msg["params"] = {"claim_id": cid}

    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    data = output["result"]

    if data["total_items"] <= 0:
        if print_error:
            if cid:
                print(">>> No item found.")
                print(">>> Check that the claim ID is correct, "
                      "or that the claim hasn't been removed from "
                      "the network.")
            elif name:
                print(">>> No item found.")
                print(">>> Check that the name is correct, "
                      "or that the claim hasn't been removed from "
                      "the network.")
        return False

    # The list of items may include various reposts;
    # usually the last item is the oldest and thus the original.
    item = data["items"][-1]

    # We still check for a repost.
    item = check_repost(item)
    return item


def search_item(uri=None, cid=None, name=None, offline=False,
                print_error=True,
                server="http://localhost:5279"):
    """Find a single item in the LBRY network resolving URI, claim id, or name.

    If all inputs are provided, `uri` is used.
    If only `cid` and `name` are given, `cid` is used.

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
    offline: bool, optional
        It defaults to `False`, in which case it will use
        `lbrynet claim search` to search `cid` or `name` in the online
        database.

        If it is `True` it will use `lbrynet file list` to search
        `cid` or `name` in the offline database.
        This is required for 'invalid' claims, which have been removed from
        the online database and only exist locally.
    print_error: bool, optional
        It defaults to `True`, in which case it will print the error message
        that `lbrynet resolve` or `lbrynet claim search` returns.
        By setting this value to `False` no messages will be printed;
        this is useful inside other functions when we want to limit
        the terminal output.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        Returns the dictionary that represents the `claim` that was found
        matching the URI, `'claim_id'` or `'name'`.
    False
        If the dictionary seems to have no items found, it will print
        an error message and return `False`.
    """
    if not (uri or cid or name):
        print("Search by 'URI', 'claim_id' or 'name'.")
        print(f"uri={uri}")
        print(f"cid={cid}")
        print(f"name={name}")
        return False

    if uri:
        item = search_item_uri(uri=uri, print_error=print_error,
                               server=server)
    else:
        item = search_item_cid(cid=cid, name=name, offline=offline,
                               print_error=print_error,
                               server=server)

    if not item and print_error:
        print(f">>> uri={uri}")
        print(f">>> cid={cid}")
        print(f">>> name={name}")

    return item


def parse_claim_file(file=None, sep=";", start=1, end=0):
    """Parse a CSV file containing claim_ids.

    Parameters
    ----------
    file: str
        The path to a comma-separated-values (CSV) file with claim_ids.
        Each row indicates a particular claim, and at least one
        value in a row must be a 40 character `'claim_id'`.

        This file can be produced by `print_summary(file='summary.txt')`
    sep: str, optional
        It defaults to `;`. It is the separator character between
        the data fields in the read file. Since the claim name
        can have commas, a semicolon `;` is used by default.
    start: int, optional
        It defaults to 1.
        Operate on the item starting from this index in `file`.
    end: int, optional
        It defaults to 0.
        Operate until and including this index in `file`.
        If it is 0, it is the same as the last index.

    Returns
    -------
    list of dict
        It returns a list of dictionaries with the claims.
        Each dictionary has a single key, 'claim_id',
        whose value is the 40-character alphanumeric string
        which can be used with `download_single` to get that claim.
    False
        If there is a problem or non existing `file`,
        it will return `False`.
    """
    if not file or not isinstance(file, str) or not os.path.exists(file):
        print("File must exist, and be a valid CSV list of items "
              "with claim ids")
        print(f"file={file}")
        print("Example file:")
        print("  1/435; 70dfefa510ca6eee7023a2a927e34d385b5a18bd;  5/ 5")
        print("  2/435; 0298c56e0593b140c231229a065cc1647d4fedae; 24/24")
        print("  3/435; d30002fec25bff804f144655b3fe4495e00439de; 15/15")
        return False

    with open(file, "r") as fd:
        lines = fd.readlines()

    n_lines = len(lines)
    claims = []

    if n_lines < 1:
        print(">>> Empty file.")
        return False

    print(80 * "-")
    print(f"Parsing file with claims, '{file}'")

    for it, line in enumerate(lines, start=1):
        # Skip lines with only whitespace, and starting with # (comments)
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if it < start:
            continue
        if end != 0 and it > end:
            break

        out = "{:4d}/{:4d}".format(it, n_lines) + f"{sep} "

        # Split by using the separator, and remove whitespaces
        parts = line.split(sep)
        clean_parts = [i.strip() for i in parts]

        found = True
        for part in clean_parts:
            # Find the 40 character long alphanumeric string
            # without confusing it with an URI like 'lbry://@some/video#4'
            if (len(part) == 40
                    and "/" not in part
                    and "@" not in part
                    and "#" not in part
                    and ":" not in part):
                found = True
                claims.append({"claim_id": part})
                break
            found = False

        if found:
            print(out + f"claim_id: {part}")
        else:
            print(out + "no 'claim_id' found, "
                  "it must be a 40-character alphanumeric string "
                  "without special symbols like '/', '@', '#', ':'")

    n_claims = len(claims)
    print(f"Effective claims found: {n_claims}")
    return claims
