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
"""Functions to help with resolving channels online."""
import requests

import lbrytools.funcs as funcs
import lbrytools.search as srch


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
    if not funcs.server_exists(server=server):
        return False

    if not channel or not isinstance(channel, str):
        print("Channel must be a string.")
        print(f"channel={channel}")
        return False

    # The channel must start with @, otherwise we may resolve a claim
    if not channel.startswith("@"):
        channel = "@" + channel

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


def find_channel(uri=None, cid=None, name=None,
                 full=True, canonical=False, offline=False,
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
    offline: bool, optional
        It defaults to `False`, in which case it will try to resolve
        the channel name from the online database (blockchain).

        If it is `True` it will try to resolve the channel name
        from the offline database. This will be faster but may not
        find a name if the channel was not resolved when the claim
        was initially downloaded.
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
    if not funcs.server_exists(server=server):
        return False

    if not (uri or cid or name):
        print("Find the channel's name from a claim's "
              "'URI', 'claim_id', or 'name'.")
        print(f"uri={uri}, cid={cid}, name={name}")
        return False

    item = srch.search_item(uri=uri, cid=cid, name=name, offline=offline,
                            server=server)
    if not item:
        return False

    if offline:
        return item["channel_name"]

    if ("signing_channel" not in item
            or "canonical_url" not in item["signing_channel"]):
        name = "@_Unknown_"
        return name

    name = item["signing_channel"]["canonical_url"]

    if not canonical:
        name = name.split("lbry://")[1]

        if not full:
            name = name.split("#")[0]

    return name
