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
"""Based methods for handling comments in the comment server."""
import requests


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
