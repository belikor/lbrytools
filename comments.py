#!/usr/bin/env python3
# --------------------------------------------------------------------------- #
# The MIT License (MIT)                                                       #
#                                                                             #
# Copyright (c) 2022 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de>       #
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
"""List and add comments to the comment server, normally Odysee."""
import os
import time

import requests

import lbrytools.search as srch


def jsonrpc_post(comm_server, method, params=None, **kwargs):
    """General RPC interface for interacting with the comment server.

    Parameters
    ----------
    comm_server: str
        Address of the comment server, for example,
        `https://comments.odysee.com/api/v2`
    method: str
        Method that the comment server accepts, for example,
        `comment.List`
    params: dict, optional
        It defaults to `None`.
        Dictionary with key-value pairs of options
        that are accepted by the specific `method`.
    kwargs: key-value pairs, optional
        Additional arguments which are added to the `params` dictionary.

    Returns
    -------
    dict
        It is the output of the `requests.post(comm_server, json=msg).json()`
        where `msg` includes the `method` and `params`.
    """
    params = params or {}
    params.update(kwargs)

    msg = {"jsonrpc": "2.0",
           "id": 1,
           "method": method,
           "params": params}

    output = requests.post(comm_server, json=msg).json()
    return output


def augment_replies(base_comments):
    """Add a new key for each comment on the list for sub replies."""
    augmented_comments = []
    for base in base_comments:
        base["sub_replies"] = []
        augmented_comments.append(base)
    return augmented_comments


def find_replies(all_replies, base_comments):
    """Find the replies belonging to base_comments."""
    lvl_comment = []
    for rep in all_replies:
        for base in base_comments:
            if rep["parent_id"] == base["comment_id"]:
                # Each reply may have more sub-replies.
                # We allocate the space for them.
                rep["sub_replies"] = []
                lvl_comment.append(rep)
    return lvl_comment


def print_r_comments(comments, sub_replies=True, full=False,
                     indent=0, fd=None):
    """Print the comments included in the comment list.

    This function calls itself recursively in order to get
    the replies from the inspected comments.

    Parameters
    ----------
    comments: list of dict
        Each dict is a comment that may have the `'sub_replies'` key
        with the replies to this comment.
    sub_replies: bool, optional
        It defaults to `True`, in which case it will recursively print
        the replies under each comment, if the `'sub_replies'` key is found
        in the comment.
        If it is `False` only the root level comments (1st level)
        will be printed.
    indent: int, optional
        It defaults to 0, which indicates that the comment will be printed
        with no indentation.
        As this function is called recursively, it will print each level
        with more indentation (2, 4, 6, etc.).
    full: bool, optional
        It defaults to `False`, in which case only 80 characters
        of the first line of the comment will be printed.
        If it is `True` it will print the full comment, which may be
        as big as 2000 characters.
    fd: io.StringIO, optional
        It defaults to `None`, in which case the output will be printed
        to the terminal.
        If it is present, it is an object created by `open()`
        ready to be used for writting text.
        After calling this function, we must `fd.close()`
        to close the object.
    """
    n_base = len(comments)
    indentation = indent * " "

    for num, comment in enumerate(comments, start=1):
        ch = comment.get("channel_url", "lbry://_Unknown_#000")
        ch = ch.lstrip("lbry://").split("#")
        ch_name = ch[0] + "#" + ch[1][0:3]

        comm = comment["comment"]
        if full:
            cmmnt = f'"{comm}"'
        else:
            comm = comm.splitlines()[0]
            if len(comm) > 80:
                cmmnt = f'"{comm:.80s}..."'
            else:
                cmmnt = f'"{comm}"'

        line = (f"{indentation}"
                + f"{num:2d}/{n_base:2d}; {ch_name:30s}; {cmmnt}")
        if fd:
            print(line, file=fd)
        else:
            print(line)

        if (sub_replies
                and "replies" in comment
                and "sub_replies" in comment
                and comment["sub_replies"]):
            print_r_comments(comment["sub_replies"], sub_replies=True,
                             indent=indent+2, fd=fd)


def print_f_comments(comments, sub_replies=True, full=False,
                     file=None, fdate=None):
    """Open a file description or print to the terminal."""
    fd = 0
    if file:
        dirn = os.path.dirname(file)
        base = os.path.basename(file)

        if fdate:
            fdate = time.strftime("%Y%m%d_%H%M", time.localtime()) + "_"
        else:
            fdate = ""

        file = os.path.join(dirn, fdate + base)

        try:
            fd = open(file, "w")
        except (FileNotFoundError, PermissionError) as err:
            print(f"Cannot open file for writing; {err}")

    print_r_comments(comments, sub_replies=sub_replies, full=full, fd=fd)

    if file and fd:
        fd.close()


def list_comments(uri=None, cid=None, name=None,
                  sub_replies=True,
                  hidden=False, visible=False,
                  full=False,
                  file=None, fdate=None,
                  page=1, page_size=999,
                  comm_server="https://comments.odysee.com/api/v2",
                  server="http://localhost:5279"):
    """List comments for a specific claim on a comment server.

    Parameters
    ----------
    uri, cid, name: str
        A unified resource identifier (URI), a `'claim_id'`,
        or a `'claim_name'` for a claim on the LBRY network.
    sub_replies: bool, optional
        It defaults to `True`, in which case it will print
        the replies (2nd, 3rd, 4th,... levels).
        If it is `False` it will only print the root level comments
        (1st level).
    hidden: bool, optional
        It defaults to `False`.
        If it is `True` it will only show the hidden comments.
    visible: bool, optional
        It defaults to `False`.
        If it is `True` it will only show the visible comments.
    full: bool, optional
        It defaults to `False`, in which case only 80 characters
        of the first line of the comment will be printed.
        If it is `True` it will print the full comment, which may be
        as big as 2000 characters.
    file: str, optional
        It defaults to `None`.
        It must be a writable path to which the summary will be written.
        Otherwise the summary will be printed to the terminal.
    fdate: bool, optional
        It defaults to `False`.
        If it is `True` it will add the date to the name of the summary file.
    comm_server: str, optional
        It defaults to `'https://comments.odysee.com/api/v2'`
        It is the address of the comment server.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the local `lbrynet` daemon.

    Returns
    -------
    dict
        It has three keys.
        - `'root_comments'`: a list of dict, where each dictionary represents
          a comment at the root level (1st level).

          Each dictionary representing a comment has the text of the comment
          under the `'comment'` key.
          The `'sub_replies'` key has a list of the replies to that comment.
          ::
              output['root_comments'][0]['sub_replies'] -> [{..., ...}]

          If the comment has no replies, the `'sub_replies'` value is an empty
          list.
          ::
              output['root_comments'][0]['sub_replies'] -> []
        - `'replies'`: a list of dict, where each dictionary represents
          a reply to any comment. These replies are not ordered,
          so they correspond to comments at any level except at the root level
          (1st level).
        - `'levels'`: a dictionary with `n` keys, where each key is an integer
          starting from `1`, and up to `n`. Each key represents
          a comment level, so `1` is for the root level comments,
          `2` is for the replies to the root level comments,
          `3` is for the replies to 2nd level comments, etc.
          Each value in the dictionary is a list of dict
          with the comments at that level.
          The first level list is the same as `'root_comments'`.
          ::
              output['root_comments'] == output['levels'][0]
              output['root_comments'][5] == output['levels'][0][5]
    False
        If there is a problem, like a non-existing item,
        it will return `False`.
    """
    item = srch.search_item(uri=uri, cid=cid, name=name,
                            server=server)
    if not item:
        return False

    claim_id = item["claim_id"]
    uri = item["canonical_url"]
    title = item["value"].get("title", "(None)")

    cl_time = 0
    if "release_time" in item["value"]:
        cl_time = int(item["value"]["release_time"])
        cl_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                                time.localtime(cl_time))

    # Only one of them is True
    if hidden ^ visible:
        params = {"claim_id": claim_id,
                  "visible": visible,
                  "hidden": hidden,
                  "page": page,
                  "page_size": page_size}
    else:
        params = {"claim_id": claim_id,
                  "page": page,
                  "page_size": page_size,
                  "top_level": False,
                  "sort_by": 3}

    output = jsonrpc_post(comm_server, "comment.List", params)

    if "error" in output:
        return False

    if output["result"]["total_items"] < 1:
        items = []
    else:
        items = output["result"]["items"]

    root_comments = []
    all_replies = []

    for comment in items:
        if "parent_id" in comment:
            all_replies.append(comment)
        else:
            root_comments.append(comment)

    n_comms = len(items)
    n_base = len(root_comments)
    n_replies = len(all_replies)

    print(f"canonical_url: {uri}")
    print(f"claim_id: {claim_id}")
    print(f"release_time: {cl_time}")
    print(f"title: {title}")
    print(f"comment server: {comm_server}")

    print(80 * "-")
    print(f"Total comments: {n_comms}")
    print(f"Total base comments: {n_base}")
    print(f"Total replies: {n_replies}")

    n = 1
    lvl_comments = {n: augment_replies(root_comments)}

    while True:
        replies_sub = find_replies(all_replies, lvl_comments[n])
        n_lvl = len(replies_sub)

        if n_lvl:
            n += 1
            lvl_comments[n] = replies_sub
            print(f" - Level {n} replies: {n_lvl}")
        else:
            break

    indices = list(range(2, len(lvl_comments) + 1))
    indices.reverse()

    for n in indices:
        for rep in lvl_comments[n]:
            for base in lvl_comments[n-1]:
                if rep["parent_id"] == base["comment_id"]:
                    base["sub_replies"].append(rep)

    print_f_comments(root_comments, sub_replies=sub_replies, full=full,
                     file=file, fdate=fdate)

    return {"root_comments": root_comments,
            "replies": all_replies,
            "levels": lvl_comments}


def sign_comment(data, channel, hexdata=None,
                 wallet_id="default_wallet",
                 server="http://localhost:5279"):
    """Sign a text message with the channel's private key.

    Parameters
    ----------
    data: str
        The text to sign.
    channel: str
        The channel name that will be used to sign the `data`.
        This channel must be under our control and thus exist in `wallet_id`.
    hexdata: str, optional
        It defaults to `None`.
        If it exists, it is a string representing the hexadecimal encoded
        `data`, that is, `hexdata = data.encoded().hex()`.
        If hexdata is given, `data` is no longer used.
    wallet_id: str, optional
        It defaults to `'default_wallet'`, in which case it will search
        the default wallet created by `lbrynet`, in order to resolve
        `channel` and sign the data with its private key.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the local `lbrynet` daemon used to sign
        the data.

    Returns
    -------
    dict
        There are two keys
        - 'signature': the signature of the data.
        - 'signature_ts': the timestamp used to sign the data.
    False
        If there is a problem, such as non-existing `wallet_id`,
        it will return `False`.
    """
    if not hexdata:
        hexdata = data.encode().hex()

    if not channel.startswith("@"):
        channel = "@" + channel

    msg = {"method": "channel_sign",
           "params": {"channel_name": channel,
                      "hexdata": hexdata,
                      "wallet_id": wallet_id}}

    output = requests.post(server, json=msg).json()
    if "error" in output:
        name = output["error"]["data"]["name"]
        mess = output["error"].get("message", "No error message")
        print(f">>> {name}: {mess}")
        return False

    return output["result"]


def create_comment(comment=None,
                   uri=None, cid=None, name=None,
                   parent_id=None,
                   ch_uri=None, ch_cid=None, ch_name=None,
                   comm_server="https://comments.odysee.com/api/v2",
                   server="http://localhost:5279"):
    """Create a comment or reply to it.

    AT THE MOMENT THIS DOESN'T WORK because we cannot sign the comment
    with the channel key. This is necessary to create the comment
    on the comment server.

    {
      "method": "comment.Create",
      "id": 1,
      "jsonrpc": "2.0",
      "params": {
        "channel_id": "81bec0b66ff34a1378581751958f5b98f9043d17",
        "channel_name": "@vertbyqb",
        "claim_id": "2ba7ec34033a42c76468cdfc463943e5de7e364a",
        "parent_id": "", # Optional, for replies
        "comment": "l test",
        "signature": sig,
        "signing_ts": "1642638072"
      }
    }
    # hexdata is the hex encoded version of the comment
    sig = "lbrynet channel sign --channel_name=@channel --hexdata=hexdata"

    Parameters
    ----------
    comment: str
        String that represents the comment. It should be a string,
        and may include newlines, and markdown text.
    uri, cid, name: str
        A unified resource identifier (URI), a `'claim_id'`,
        or a `'claim_name'` for a claim on the LBRY network.
        It is the claim under which the comment will be created.
    parent_id: str
        Identification string for the.
    ch_uri, ch_cid, ch_name: str
        A unified resource identifier (URI), a `'claim_id'`,
        or a `'claim_name'` for a claim on the LBRY network.
        This will be the channel that we control which will be the author
        of the comment.
    comm_server: str, optional
        It defaults to `'https://comments.odysee.com/api/v2'`
        It is the address of the comment server.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the local `lbrynet` daemon.
    """
    if not comment:
        return False

    comment = comment.strip()

    if not comment:
        return False

    item = srch.search_item(uri=uri, cid=cid, name=name,
                            server=server)
    if not item:
        return False

    claim_id = item["claim_id"]
    uri = item["canonical_url"]
    title = item["value"]["title"]

    cl_time = 0
    if "release_time" in item["value"]:
        cl_time = int(item["value"]["release_time"])
        cl_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                                time.localtime(cl_time))

    ch = srch.search_item(uri=ch_uri, cid=ch_cid, name=ch_name,
                          server=server)
    if not ch:
        return False

    print(f"canonical_url: {uri}")
    print(f"claim_id: {claim_id}")
    print(f"release_time: {cl_time}")
    print(f"title: {title}")
    print(f"comment server: {comm_server}")

    print(80 * "-")

    params = {"comment": comment,
              "claim_id": claim_id,
              "parent_id": parent_id,
              "channel_id": ch["claim_id"],
              "channel_name": ch["name"]}

    output = jsonrpc_post(comm_server, "comment.Create", params)

    if "error" in output:
        print(">>> Error:", output["error"].get("message", None))
        return False

    return output["result"]
