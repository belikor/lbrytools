#!/usr/bin/env python3
# --------------------------------------------------------------------------- #
# The MIT License (MIT)                                                       #
#                                                                             #
# Copyright (c) 2023 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de>       #
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
"""Add comments to the comment server, normally Odysee."""
import time

import lbrytools.funcs as funcs
import lbrytools.search as srch
import lbrytools.comments_base as comm


def print_cmnt_result(result, file=None, fdate=False):
    """Print the response of the comment server when successful."""
    cmt_time = result["timestamp"]
    cmt_time = time.strftime(funcs.TFMT, time.gmtime(cmt_time))

    sig_ts = int(result["signing_ts"])
    sig_ts = time.strftime(funcs.TFMT, time.gmtime(sig_ts))

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

    rels_time = int(item["value"].get("release_time", 0))

    if not rels_time:
        rels_time = item["meta"].get("creation_timestamp", 0)

    rels_time = time.strftime(funcs.TFMT, time.gmtime(rels_time))

    ch = srch.search_item(uri=author_uri, cid=author_cid, name=author_name,
                          server=server)
    if not ch:
        return False

    out = [f"canonical_url: {uri}",
           f"claim_id: {claim_id}",
           f"release_time: {rels_time}",
           f"title: {title}",
           "comment author:", ch["name"],
           "comment author ID:", ch["claim_id"],
           f"comment server: {comm_server}",
           40 * "-"]

    funcs.print_content(out, file=None, fdate=False)

    sign = comm.sign_comment(comment, ch["name"],
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

    output = comm.jsonrpc_post(comm_server, "comment.Create", params)

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
    output = comm.jsonrpc_post(comm_server,
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

    sign = comm.sign_comment(field, ch["channel_name"],
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
        If there is a problem, such as non-existing `wallet_id`,
        or empty `comment` or `comment_id`, it will return `False`.
    """
    print("Update comment")
    print(80 * "-")

    if not comment or not comment_id:
        print(">>> Empty comment or comment_id.")
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

    output = comm.jsonrpc_post(comm_server, "comment.Edit", edited_comment)
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
        If there is a problem, such as non-existing `wallet_id`,
        or empty `comment_id`, it will return `False`.
    """
    print("Abandon comment")
    print(80 * "-")

    if not comment_id:
        print(">>> Empty comment_id.")
        return False

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

    output = comm.jsonrpc_post(comm_server, "comment.Abandon", params)
    if "error" in output:
        print(">>> Error:", output["error"].get("message", None))
        return False

    result = output["result"]

    print_cmnt_result(result, file=None, fdate=False)

    return result


def hide_comment(comment_id=None,
                 wallet_id="default_wallet",
                 comm_server="https://comments.odysee.com/api/v2",
                 server="http://localhost:5279"):
    """Hide a previously created comment in a claim we control.

    NOTE: it does not work. It should have worked in the past,
    but nowadays the 'comment.Hide' method doesn't exist in the comment server
    so this method does nothing.
    """
    print("Hide comment")
    print(80 * "-")

    if not comment_id:
        print(">>> Empty comment_id.")
        return False

    # comment_ids = [comment_id]

    print(f"comment_id: {comment_id} ({len(comment_id)} bit)")
    print(f"comment server: {comm_server}")

    print(40 * "-")

    # output = jsonrpc_post(comm_server,
    #                       "get_comments_by_id",
    #                       comment_ids=comment_ids)
    output = comm.jsonrpc_post(comm_server,
                               "comment.ByID",
                               comment_id=comment_id,
                               with_ancestors=True)

    comment = output["result"]["items"]

    pieces = []
    piece = {'comment_id': comment['comment_id']}
    pieces.append(piece)

    # Does no longer exist
    output = comm.jsonrpc_post(comm_server, 'comment.Hide', pieces=pieces)

    if "error" in output:
        print(">>> Error:", output["error"].get("message", None))
        return False

    result = output["result"]

    return result
