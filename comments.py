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

import lbrytools.funcs as funcs
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
                     indent=0, sanitize=False, fd=None):
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
    full: bool, optional
        It defaults to `False`, in which case only 80 characters
        of the first line of the comment will be printed.
        If it is `True` it will print the full comment, which may be
        as big as 2000 characters.
    indent: int, optional
        It defaults to 0, which indicates that the comment will be printed
        with no indentation.
        As this function is called recursively, it will print each level
        with more indentation (2, 4, 6, etc.).
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the comments.
        If it is `True` it will remove these unicode characters.
        This option requires the `emoji` package to be installed.
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

        if sanitize:
            comm = funcs.sanitize_text(comm)

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
                             indent=indent+2, sanitize=sanitize, fd=fd)


def print_f_comments(comments, sub_replies=True, full=False,
                     sanitize=False,
                     file=None, fdate=False):
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

    print_r_comments(comments, sub_replies=sub_replies, full=full,
                     sanitize=sanitize, fd=fd)

    if file and fd:
        fd.close()


def list_comments(uri=None, cid=None, name=None,
                  sub_replies=True,
                  hidden=False, visible=False,
                  full=False,
                  sanitize=False,
                  file=None, fdate=False,
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
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the comments.
        If it is `True` it will remove these unicode characters.
        This option requires the `emoji` package to be installed.
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
                     sanitize=sanitize,
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


def print_cmnt_result(result, file=None, fdate=False):
    """Print the response of the comment server when successful."""
    cmt_time = result["timestamp"]
    cmt_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                             time.localtime(cmt_time))

    sig_ts = int(result["signing_ts"])
    sig_ts = time.strftime("%Y-%m-%d_%H:%M:%S%z %A",
                           time.localtime(sig_ts))

    out = ["claim_id: " + result["claim_id"],
           "timestamp:  " + cmt_time,
           "signing_ts: " + sig_ts,
           "comment author: " + result["channel_name"],
           "comment author ID: " + result["channel_id"],
           "comment_id: " + result["comment_id"],
           "parent_id:  " + result.get("parent_id", "(None)"),
           "currency: " + result.get("currency", "(None)"),
           "support_amount: " + str(result.get("support_amount", 0)),
           "is_fiat: " + str(result.get("is_fiat", "")),
           "is_hidden: " + str(result.get("is_hidden", "")),
           "is_pinned: " + str(result.get("is_pinned", "")),
           "abandoned: " + str(result.get("abandoned", "")),
           "comment:",
           "'''",
           result["comment"],
           "'''"]

    funcs.print_content(out, file=file, fdate=fdate)


def create_comment(comment=None,
                   uri=None, cid=None, name=None,
                   parent_id=None,
                   author_uri=None, author_cid=None, author_name=None,
                   wallet_id="default_wallet",
                   comm_server="https://comments.odysee.com/api/v2",
                   server="http://localhost:5279"):
    """Create a comment or reply to an existing comment.

    Parameters
    ----------
    comment: str
        String that represents the comment. It should be a string,
        and may include newlines, and markdown formatting.
    uri, cid, name: str
        A unified resource identifier (URI), a `'claim_id'`,
        or a `'claim_name'` for a claim on the LBRY network.
        It is the claim under which the comment will be created.
    parent_id: str, optional
        It defaults to `None`.
        If it exists, it is an identification string for an existing comment,
        meaning that our `comment` will be a reply to it.
    author_uri, author_cid, author_name: str
        A unified resource identifier (URI), a `'claim_id'`,
        or a `'claim_name'` for a claim on the LBRY network.
        This will be the channel that we control which will be the author
        of the comment or reply.
    wallet_id: str, optional
        It defaults to 'default_wallet' which is the default wallet
        created by `lbrynet`. It will be used for searching the channel
        and its private key which will be the author of the comment.
    comm_server: str, optional
        It defaults to `'https://comments.odysee.com/api/v2'`
        It is the address of the comment server.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the local `lbrynet` daemon used to resolve
        the claims and sign the comment.

    Returns
    -------
    dict
        A dictionary with many keys
        - 'comment': the same `comment` information.
        - 'comment_id': the 64-character ID of the successful comment.
        - 'claim_id': the claim ID corresponding to the input `uri`, `cid`,
          or `name`.
        - 'timestamp': the timestamp in seconds since 1970-01-01
          known as the Unix epoch.
        - 'parent_id': the 64-character ID of the parent comment
          to this comment, if it is a reply.
          If our comment is not a reply, that is, it has no parent comment,
          then this key won't exist.
        - 'signature': the 128-character signature of the transaction
        - 'signing_ts': the signing timestamp in seconds since 1970-01-01
          known as the Unix epoch.
        - 'channel_id': 40-character ID of the channel
          '44660089c9cb227d65c403a4328606173042cadc'
        - 'channel_name': string indicating the generic channel name
          `'@MyChannel'`
        - 'channel_url': string indicating the signing channel; it includes
          the `channel_name` and then the `channel_id`
          `'lbry://@MyChannel#44660089c9cb227d65c403a4328606173042cadc'`
        - 'currency': string indicating the currency, for example, 'LBC'
        - 'support_amount': integer value indicating whether the comment
          has a support
        - 'is_hidden': boolean value indicating whether the comment is hidden
        - 'is_pinned': boolean value indicating whether the comment is pinned
        - 'is_fiat': boolean value indicating whether fiat currency was sent
    False
        If there is a problem, such as non-existing `wallet_id`, or empty
        `comment`, or invalid claim, or invalid channel,
        it will return `False`.

    Signed data
    -----------
    The comment server requires various parameters.
    ::
        {
          "method": "comment.Create",
          "id": 1,
          "jsonrpc": "2.0",
          "params": {
            "channel_id": "90abc0b66ff34a1378581751958f5b98f9043d17",
            "channel_name": "@some-channel",
            "claim_id": "4ba7ec34033a42c76468cdfc463943e5de7e364a",
            "parent_id": "", # Optional, for replies
            "comment": "some test comment",
            "signature": signature,
            "signing_ts": signing_timestamp
          }
        }

    The `signature` and `signing_timestamp` are obtained from signing the
    hexadecimal representation of the comment.
    These values are provided by `sign_comment`.
    """
    print("Create comment")
    print(80 * "-")

    if not comment:
        print(">>> Empty comment.")
        return False

    comment = comment.strip()

    if not comment:
        print(">>> Empty comment.")
        return False

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

    ch = srch.search_item(uri=author_uri, cid=author_cid, name=author_name,
                          server=server)
    if not ch:
        return False

    print(f"canonical_url: {uri}")
    print(f"claim_id: {claim_id}")
    print(f"release_time: {cl_time}")
    print(f"title: {title}")
    print("comment author:", ch["name"])
    print("comment author ID:", ch["claim_id"])
    print(f"comment server: {comm_server}")

    print(40 * "-")

    sign = sign_comment(comment, ch["name"],
                        wallet_id=wallet_id,
                        server=server)

    if not sign:
        print(">>> Unable to sign; "
              "we must have the private keys of this channel "
              "for this operation to succeed.")
        return False

    params = {"comment": comment,
              "claim_id": claim_id,
              "parent_id": parent_id,
              "channel_id": ch["claim_id"],
              "channel_name": ch["name"],
              "signature": sign["signature"],
              "signing_ts": sign["signing_ts"]}

    output = jsonrpc_post(comm_server, "comment.Create", params)

    if "error" in output:
        print(">>> Error:", output["error"].get("message", None))
        return False

    result = output["result"]

    print_cmnt_result(result, file=None, fdate=False)

    return result


def get_ch_and_sign(comment=None,
                    comment_id=None,
                    wallet_id="default_wallet",
                    comm_server="https://comments.odysee.com/api/v2",
                    server="http://localhost:5279"):
    """Get the channel from a comment ID and sign the comment ID."""
    output = jsonrpc_post(comm_server,
                          "comment.GetChannelFromCommentID",
                          comment_id=comment_id)

    if "error" in output:
        print(">>> Error:", output["error"].get("message", None))
        return False

    ch = output["result"]

    if comment:
        field = comment
    else:
        field = comment_id

    sign = sign_comment(field, ch["channel_name"],
                        wallet_id=wallet_id,
                        server=server)

    if not sign:
        print("channel_name:", ch["channel_name"])
        print("channel_id:", ch["channel_id"])
        print(">>> Unable to sign; "
              "we must have the private keys of this channel "
              "for this operation to succeed.")
        return False

    return {"channel": ch,
            "sign": sign}


def update_comment(comment=None, comment_id=None,
                   wallet_id="default_wallet",
                   comm_server="https://comments.odysee.com/api/v2",
                   server="http://localhost:5279"):
    """Update a previously created comment with a new text.

    Parameters
    ----------
    comment: str
        String that represents the comment. It should be a string,
        and may include newlines, and markdown formatting.
    comment_id: str
        The 64-character ID of an existing comment which was published by us.
        The channel that was used to publish the comment will be determined
        from this ID.
    wallet_id: str, optional
        It defaults to 'default_wallet' which is the default wallet
        created by `lbrynet`. It will be used for searching the channel
        and its private key which will be the author of the comment.
    comm_server: str, optional
        It defaults to `'https://comments.odysee.com/api/v2'`
        It is the address of the comment server.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the local `lbrynet` daemon used to resolve
        the claims and sign the comment.

    Returns
    -------
    dict
        A dictionary with many fields of information. See `create_comment`.
    False
        If there is a problem, such as non-existing `wallet_id`, or empty
        `comment`, it will return `False`.
    """
    print("Update comment")
    print(80 * "-")

    if not comment:
        print(">>> Empty comment.")
        return False

    comment = comment.strip()

    if not comment:
        print(">>> Empty comment.")
        return False

    print(f"comment_id: {comment_id} ({len(comment_id)} bit)")
    print(f"comment server: {comm_server}")

    print(40 * "-")

    result = get_ch_and_sign(comment=comment,
                             comment_id=comment_id,
                             wallet_id=wallet_id,
                             comm_server=comm_server,
                             server=server)

    if not result:
        return False

    ch = result["channel"]
    sign = result["sign"]

    edited_comment = {"comment_id": comment_id,
                      "comment": comment,
                      "channel_id": ch["channel_id"],
                      "channel_name": ch["channel_name"],
                      "signature": sign["signature"],
                      "signing_ts": sign["signing_ts"]}

    output = jsonrpc_post(comm_server, "comment.Edit", edited_comment)
    if "error" in output:
        print(">>> Error:", output["error"].get("message", None))
        return False

    result = output["result"]

    print_cmnt_result(result, file=None, fdate=False)

    return result


def abandon_comment(comment_id=None,
                    wallet_id="default_wallet",
                    comm_server="https://comments.odysee.com/api/v2",
                    server="http://localhost:5279"):
    """Remove a previously created comment.

    Parameters
    ----------
    comment_id: str
        The 64-character ID of an existing comment which was published by us.
        The channel that was used to publish the comment will be determined
        from this ID.
    wallet_id: str, optional
        It defaults to 'default_wallet' which is the default wallet
        created by `lbrynet`. It will be used for searching the channel
        and its private key which will be the author of the comment.
    comm_server: str, optional
        It defaults to `'https://comments.odysee.com/api/v2'`
        It is the address of the comment server.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the local `lbrynet` daemon used to resolve
        the claims and sign the comment.

    Returns
    -------
    dict
        A dictionary with many fields of information. See `create_comment`.
        It will contain a unique key
        - 'abandoned': it will be `True` if the comment was successfully
          removed from the comment server.
    False
        If there is a problem, such as non-existing `wallet_id`
        it will return `False`.
    """
    print("Abandon comment")
    print(80 * "-")

    print(f"comment_id: {comment_id} ({len(comment_id)} bit)")
    print(f"comment server: {comm_server}")

    print(40 * "-")

    result = get_ch_and_sign(comment=None,
                             comment_id=comment_id,
                             wallet_id=wallet_id,
                             comm_server=comm_server,
                             server=server)

    if not result:
        return False

    ch = result["channel"]
    sig = result["sign"]

    params = {"comment_id": comment_id,
              "channel_id": ch["channel_id"],
              "channel_name": ch["channel_name"],
              "signature": sig["signature"],
              "signing_ts": sig["signing_ts"]}

    output = jsonrpc_post(comm_server, "comment.Abandon", params)
    if "error" in output:
        print(">>> Error:", output["error"].get("message", None))
        return False

    result = output["result"]

    print_cmnt_result(result, file=None, fdate=False)

    return result
