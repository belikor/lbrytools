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

import lbrytools.funcs as funcs


def check_repost(item):
    """Check if the item is a repost, and return the original item.

    A claim that is just the repost of another cannot be downloaded directly,
    so we replace the input item with the reposted (original) item.

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

    funcs.check_lbry(server=server)
    cmd = ["lbrynet",
           "resolve",
           uri]
    # output = subprocess.run(cmd,
    #                         capture_output=True,
    #                         check=True,
    #                         text=True)
    # if output.returncode == 1:
    #     print(f"Error: {output.stderr}")
    #     sys.exit(1)

    # data = json.loads(output.stdout)

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
    # and return the original item.
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


def ch_search_latest(channel=None, number=2,
                     server="http://localhost:5279"):
    """Search for the latest claims published by a specific channel.

    Parameters
    ----------
    channel: str
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    number: int, optional
        It defaults to 2.
        The number of items to search that were last posted by `channel`.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary represents a claim
        by `channel`. The newest claims will be first.
    False
        If there is a problem, or no existing channel,
        it will return False.
    """
    if not channel or not isinstance(channel, str):
        print("Search items by channel name (string), "
              "and number of items (int).")
        print(f"channel={channel}, number={number}")
        return False

    if not number or not isinstance(number, int):
        number = 2
        print(f"Number set to default value, number={number}")

    if not channel.startswith("@"):
        channel = "@" + channel

    funcs.check_lbry(server=server)
    search_cmd = ["lbrynet",
                  "claim",
                  "search",
                  "--channel=" + channel,
                  # "--stream_type=video",
                  "--page_size=" + str(number),
                  "--order_by=release_time"]

    search_cmd2 = search_cmd[:]
    search_cmd2[3] = "--channel=" + "'" + channel + "'"

    print("Search: " + " ".join(search_cmd2))
    print(80 * "-")
    # output = subprocess.run(search_cmd,
    #                         capture_output=True,
    #                         check=True,
    #                         text=True)

    # if output.returncode == 1:
    #     print(f"Error: {output.stderr}")
    #     sys.exit(1)

    # data = json.loads(output.stdout)

    msg = {"method": search_cmd[1] + "_" + search_cmd[2],
           "params": {"channel": channel,
                      "page_size": number,
                      "order_by": "release_time"}}

    # A bug (lbryio/lbry-sdk #3316) prevents the `lbrynet file list`
    # command from finding the channel, therefore the channel must be
    # resolved with `lbrynet resolve` before it becomes known by other
    # functions.
    ch = resolve_channel(channel=channel, server=server)
    if not ch:
        return False

    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    items = output["result"]["items"]

    if len(items) < 1:
        print(">>> No items found; "
              f"check that the name is correct, channel={channel}")

    return items


def find_channel(uri=None, cid=None, name=None,
                 full=True, canonical=False,
                 server="http://localhost:5279"):
    """Return the channel's name to which the given claim belongs.

    If `uri`, `cid`, and `name` are provided, `uri` is used.
    If `cid` and `name` are given, `cid` is used.

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
    full: bool, optional
        It defaults to `True`, in which case the returned
        name includes the digits after `'#'` or `':'` that uniquely identify
        that channel in the network.
        If it is `False` it will return just the base name.
        This parameter only works when `canonical=False`.
    canonical: bool, optional
        It defaults to `False`.
        If it is `True`, the `'canonical_url'` of the channel is returned
        regardless of the value of `full`.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    str
        The name of the channel.
        If `full=False` it returns the common name
        ::
            @MyChannel
        If `full=True` it returns the unique name
        ::
            @MyChannel#3
        If `canonical=True` it returns
        ::
            lbry://@MyChannel#3
    False
        If there is a problem or non existing claim, it will return `False`.
    """
    if not (uri or cid or name):
        print("Find the channel's name from a claim's "
              "'URI', 'claim_id', or 'name'.")
        print(f"uri={uri}, cid={cid}, name={name}")
        return False

    item = search_item(uri=uri, cid=cid, name=name,
                       server=server)
    if not item:
        return False

    if ("signing_channel" not in item
            or "canonical_url" not in item["signing_channel"]):
        name = "@_Unknown_"
        return name

    name = item["signing_channel"]["canonical_url"]

    if not canonical:
        name = name.lstrip("lbry://")

        if not full:
            name = name.split("#")[0]

    return name


def sort_items(channel=None,
               server="http://localhost:5279"):
    """Return a list of claims that were downloaded, sorted by time.

    If `channel` is provided it will list the downloaded claims
    by this channel only.
    Otherwise it will list all claims.

    Parameters
    ----------
    channel: str, optional
        It defaults to `None`.
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        A list of dictionaries that represent the claims that were previously
        downloaded fully or partially.
        Each dictionary is filled with information from the standard output
        of the `lbrynet file list` command.

        The dictionaries are ordered by `'release_time'`, with older claims
        appearing first.
        Certain claims don't have `'release_time'` so for them we add
        this key, and use the value of `'timestamp'` for it.
    False
        If there is a problem it will return False.
    """
    funcs.check_lbry(server=server)
    page_size = 99000
    list_cmd = ["lbrynet",
                "file",
                "list",
                "--page_size=" + str(page_size)]

    if channel and not isinstance(channel, str):
        print("Channel must be a string. Set to 'None'.")
        print(f"channel={channel}")
        channel = None

    if channel:
        if not channel.startswith("@"):
            channel = "@" + channel
        list_cmd.append("--channel_name=" + channel)

    print("List: " + " ".join(list_cmd))
    print(80 * "-")
    # output = subprocess.run(list_cmd,
    #                         capture_output=True,
    #                         check=True,
    #                         text=True)
    # if output.returncode == 1:
    #     print(f"Error: {output.stderr}")
    #     sys.exit(1)

    # data = json.loads(output.stdout)

    msg = {"method": list_cmd[1] + "_" + list_cmd[2],
           "params": {"page_size": page_size}}
    if channel:
        msg["params"]["channel_name"] = channel

        # A bug (lbryio/lbry-sdk #3316) prevents the `lbrynet file list`
        # command from finding the channel, therefore the channel must be
        # resolved with `lbrynet resolve` before it becomes known by other
        # functions.
        ch = resolve_channel(channel=channel, server=server)
        if not ch:
            return False

    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    items = output["result"]["items"]

    n_items = len(items)

    if n_items < 1:
        if channel:
            print("No items found; at least one item must be downloaded; "
                  f"check that the name is correct, channel={channel}")
        else:
            print("No items found; at least one item must be downloaded.")
        return False

    print(f"Number of items {n_items}")

    new_items = []

    # Older claims may not have 'release_time'; we use the 'timestamp' instead
    for it, item in enumerate(items, start=1):
        if "release_time" not in item["metadata"]:
            print(f"{it}/{n_items}, {item['claim_name']}, using 'timestamp'")
            item["metadata"]["release_time"] = item["timestamp"]
        new_items.append(item)

    # Sort by using the original 'release_time'; older items first
    sorted_items = sorted(new_items,
                          key=lambda v: int(v["metadata"]["release_time"]))

    return sorted_items


def sort_invalid(channel=None,
                 server="http://localhost:5279"):
    """Return a list of invalid claims that were previously downloaded.

    Certain claims that were downloaded in the past may be invalid now because
    they were removed by their authors from the network after
    they were initially downloaded. This can be confirmed by looking up
    the claim ID in the blockchain explorer, and finding the 'unspent'
    transaction.

    Parameters
    ----------
    channel: str, optional
        It defaults to `None`.
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        A list of dictionaries that represent 'invalid claims'
        that were previously downloaded fully or partially.

        Each dictionary is filled with information from the standard output
        of the `lbrynet file list` command, but filtered in such a way
        that it only includes claims which are no longer searchable online
        by `lbrynet resolve` or `lbrynet claim search`.

        The dictionaries are ordered by `'release_time'`, with older claims
        appearing first.
        Certain claims don't have `'release_time'` so for them we add
        this key, and use the value of `'timestamp'` for it.
    False
        If there is a problem it will return False.
    """
    items = sort_items(channel=channel,
                       server=server)
    if not items:
        return False

    n_items = len(items)

    invalid_items = []

    for it, item in enumerate(items, start=1):
        online_item = search_item(cid=item["claim_id"], offline=False,
                                  print_error=False,
                                  server=server)
        if not online_item:
            if len(invalid_items) == 0:
                print()
            claim_id = item["claim_id"]
            claim_name = item["claim_name"]
            channel = item["channel_name"]
            print(f"Claim {it:4d}/{n_items:4d}, "
                  f"{claim_id}, {channel}, {claim_name}")
            invalid_items.append(item)

    n_invalid = len(invalid_items)
    print(f"Invalid items found: {n_invalid} "
          "(possibly deleted from the network)")

    return invalid_items


def parse_claim_file(file=None, start=1, end=0):
    """Parse a CSV file containing claim_ids.

    Parameters
    ----------
    file: str
        The path to a comma-separated-values (CSV) file with claim_ids.
        Each row indicates a particular claim, and at least one
        value in a row must be a 40 character `'claim_id'`.

        This file can be produced by `print_summary(file='summary.txt')`
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
        print("File must exist, and be a valid CSV list of items with claim ids")
        print(f"file={file}")
        print("Example file:")
        print("1/435, 20200609_23:14:47-0500, 70dfefa510ca6eee7023a2a927e34d385b5a18bd,  5/ 5")
        print("2/435, 20210424_18:01:05-0500, 0298c56e0593b140c231229a065cc1647d4fedae, 24/24")
        print("3/435, 20210427_18:07:26-0500, d30002fec25bff804f144655b3fe4495e00439de, 15/15")
        return False

    with open(file, "r") as fd:
        lines = fd.readlines()

    n_lines = len(lines)
    claims = []

    if n_lines < 1:
        print(">>> Empty file.")
        return False

    print(80 * "-")
    print(f"Parsing file with claims, {file}")

    for it, line in enumerate(lines, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        out = "{:4d}/{:4d}, ".format(it, n_lines)

        # Split by using the comma, and remove whitespaces
        parts = line.strip().split(",")
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

    print(f"Effective claims found: {len(claims)}")
    return claims


def resolve_channel(channel=None,
                    server="http://localhost:5279"):
    """Resolve a channel name so that it can be found by file_list.

    lbrio/lbry-sdk, issue #3316
    Currently when we use some functions like `sort_items`
    the channel will not be found by the internal call to `lbrynet file list`
    if the channel isn't resolved first.

    Therefore, this function must be called before we try to search by channel.

    Parameters
    ----------
    channel: str
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        Returns the dictionary that represents the channel that was found
        matching the `channel` address.
    False
        If the dictionary has the `'error'` key, it will print the contents
        of this key, and return `False`.
    """
    if not channel or not isinstance(channel, str):
        print("Channel must be a string.")
        print(f"channel={channel}")
        return False

    # The channel must start with @, otherwise we may resolve a claim
    if not channel.startswith("@"):
        channel = "@" + channel

    funcs.check_lbry(server=server)
    cmd = ["lbrynet",
           "resolve",
           channel]

    msg = {"method": cmd[1],
           "params": {"urls": channel}}

    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    ch_item = output["result"][channel]

    if "error" in ch_item:
        error = ch_item["error"]
        if "name" in error:
            print(">>> Error: {}, {}".format(error["name"], error["text"]))
        else:
            print(">>> Error: {}".format(error))
        print(f">>> Check that the name is correct, channel={channel}")
        return False

    return ch_item
