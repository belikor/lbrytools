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
"""Functions to help with downloading content from the LBRY network."""
import os
import requests

import lbrytools.search as srch
import lbrytools.search_ch as srch_ch
import lbrytools.print as prnt


def lbrynet_get(uri=None, ddir=None,
                server="http://localhost:5279"):
    """Run the lbrynet get command and return the information that it shows.

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
    ddir: str, optional
        It defaults to `$HOME`.
        The path to the download directory.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        Returns the dictionary that represents the standard output
        of the `lbrynet get` command.
    """
    if not uri:
        print("No input claim by canonical url (URI).")
        print(f"uri={uri}")
        return False

    if (not ddir or not isinstance(ddir, str)
            or ddir == "~" or not os.path.exists(ddir)):
        ddir = os.path.expanduser("~")
        print(f"Download directory should exist; set to ddir='{ddir}'")

    # At the moment we cannot download a claim by `'claim_id'` directly.
    # Hopefully in the future `lbrynet` will be extended in this way.
    # get_cmd_id = ["lbrynet",
    #               "get",
    #               "--claim_id=" + claim_id]

    get_cmd = ["lbrynet",
               "get",
               uri,
               "--download_directory=" + "'" + ddir + "'"]

    # This is just to print the command that can be used on the terminal.
    # The URI is surrounded by single or double quotes.
    if "'" in uri:
        get_cmd[2] = '"' + uri + '"'
    else:
        get_cmd[2] = "'" + uri + "'"

    print("Download: " + " ".join(get_cmd))

    msg = {"method": "get",
           "params": {"uri": uri,
                      "download_directory": ddir}}

    output = requests.post(server, json=msg).json()
    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    info_get = output["result"]

    return info_get


def download_single(uri=None, cid=None, name=None, invalid=False,
                    ddir=None, own_dir=True,
                    server="http://localhost:5279"):
    """Download a single item and place it in the download directory.

    If `uri`, `cid`, and `name` are provided, `uri` is used.
    If `cid` and `name` are given, `cid` is used.

    This function is also used to resume the download of a partially
    downloaded claim, that is, one that for any reason didn't complete
    the first time.
    It will download the missing blobs in order to produce
    the full media file (mp4, mp3, mkv, etc.).

    If all blobs are already available, then the media file
    will be recreated (if it doesn't already exist) in the download directory.

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
    invalid: bool, optional
        It defaults to `False`, in which case it will assume the claim
        is still valid in the online database.
        It will use `lbrynet claim search` to search `cid` or `name`.

        If it is `True` it will assume the claim is no longer valid,
        that is, that the claim has been removed from the online database
        and only exists locally.
        In this case, it will use `lbrynet file list` to resolve
        `cid` or `name`.

        This has no effect on `uri`, so if this input is used,
        it will always try to resolve it from the online database.
    ddir: str, optional
        It defaults to `$HOME`.
        The path to the download directory.
    own_dir: bool, optional
        It defaults to `True`, in which case it places the downloaded
        content inside a subdirectory named after the channel in `ddir`.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        Returns the dictionary that represents the standard output
        of the `lbrynet_get` function.
    False
        If there is a problem or non existing claim, it will return `False`.
    """
    if not (uri or cid or name):
        print("No input claim by 'URI', 'claim_id', or 'name'.")
        print(f"uri={uri}, cid={cid}, name={name}")
        return False

    if (not ddir or not isinstance(ddir, str)
            or ddir == "~" or not os.path.exists(ddir)):
        ddir = os.path.expanduser("~")
        print(f"Download directory should exist; set to ddir='{ddir}'")

    # Canonical URLs cannot be treated as 'invalid', they are resolved online
    if not uri and invalid:
        info_get = download_invalid(cid=cid, name=name, ddir=ddir,
                                    own_dir=own_dir,
                                    server=server)
        return info_get

    # It also checks if it's a reposted claim, and returns the original
    # claim in case it is.
    item = srch.search_item(uri=uri, cid=cid, name=name, offline=False,
                            server=server)
    if not item:
        return False

    uri = item["canonical_url"]

    if "signing_channel" in item and "name" in item["signing_channel"]:
        # A bug (lbryio/lbry-sdk #3316) prevents
        # the `lbrynet file list --channel_name=@Channel`
        # command from finding the channel, therefore the channel must be
        # resolved with `lbrynet resolve` before it becomes known by other
        # functions.
        #
        # Both the short `@Name` and the canonical `@Name#7` are resolved.
        # The second form is necessary to get the exact channel, in case
        # it has the same base name as another channel.
        channel = item["signing_channel"]["name"]
        ch_full = item["signing_channel"]["canonical_url"].lstrip("lbry://")

        srch_ch.resolve_channel(channel=channel, server=server)
        srch_ch.resolve_channel(channel=ch_full, server=server)

        # Windows doesn't like # or : in the subdirectory; use a _
        # channel = ch_full.replace("#", ":")
        channel = ch_full.replace("#", "_")
    else:
        channel = "@_Unknown_"

    subdir = os.path.join(ddir, channel)
    if own_dir:
        if not os.path.exists(subdir):
            try:
                os.mkdir(subdir)
            except (FileNotFoundError, PermissionError) as err:
                print(f"Cannot open directory for writing; {err}")
                return False
        ddir = subdir

    prnt.print_info_pre_get(item, offline=False)
    info_get = lbrynet_get(uri=uri, ddir=ddir,
                           server=server)

    if not info_get:
        print(">>> Empty information from `lbrynet get`")
        return False

    prnt.print_info_post_get(info_get)

    return info_get


def lbrynet_save(claim_id=None, claim_name=None, ddir=None,
                 server="http://localhost:5279"):
    """Run the lbrynet file save command and return the information.

    This is mostly intended to be used with 'invalid' claims, that is,
    those which have been removed from the online database (blockchain),
    and thus cannot be redownloaded.

    Parameters
    ----------
    claim_id: str
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    claim_name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            claim_name = 'some-video-name'
    ddir: str, optional
        It defaults to `$HOME`.
        The path to the download directory.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        Returns the dictionary that represents the standard output
        of the `lbrynet file save` command.
    """
    if not (claim_id or claim_name):
        print("No input claim by 'claim_id' or 'claim_name'.")
        print(f"claim_id={claim_id}, claim_name={claim_name}")
        return False

    if (not ddir or not isinstance(ddir, str)
            or ddir == "~" or not os.path.exists(ddir)):
        ddir = os.path.expanduser("~")
        print(f"Download directory should exist; set to ddir='{ddir}'")

    cmd_name = ["lbrynet",
                "file",
                "save",
                "--claim_name=" + claim_name,
                "--download_directory=" + "'" + ddir + "'"]

    # This is just to print the command that can be used on the terminal.
    # The URI is surrounded by single or double quotes.
    if "'" in claim_name:
        cmd_name[3] = "--claim_name=" + '"' + claim_name + '"'
    else:
        cmd_name[3] = "--claim_name=" + "'" + claim_name + "'"

    cmd_id = cmd_name[:]
    cmd_id[3] = "--claim_id=" + claim_id

    print("Download: " + " ".join(cmd_id))
    print("Download: " + " ".join(cmd_name))

    msg = {"method": cmd_id[1] + "_" + cmd_id[2],
           "params": {"claim_id": claim_id,
                      "download_directory": ddir}}

    output = requests.post(server, json=msg).json()
    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    info_save = output["result"]

    return info_save


def download_invalid(cid=None, name=None,
                     ddir=None, own_dir=True,
                     server="http://localhost:5279"):
    """Download a claim that is invalid, no longer online, only offline.

    This will no longer download new blobs, only reconstitute the media file
    (mp4, mp3, mkv, etc.) if all blobs are present offline.
    This is necessary for 'invalid' claims that can no longer be found online
    because they were removed by its author.

    This only works for claim IDs and claim names, it does not work with
    full canonical URLs, as these need to be resolved online.

    Parameters
    ----------
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
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        Returns the dictionary that represents the standard output
        of the `lbrynet_save` function.
    False
        If there is a problem or non existing claim, it will return `False`.
    """
    if not (cid or name):
        print("No input claim by 'claim_id' or 'name'.")
        print(f"cid={cid}, name={name}")
        return False

    if (not ddir or not isinstance(ddir, str)
            or ddir == "~" or not os.path.exists(ddir)):
        ddir = os.path.expanduser("~")
        print(f"Download directory should exist; set to ddir='{ddir}'")

    # It also checks if it's a reposted claim, although 'invalid' claims
    # cannot be reposts, as the original claim is already downloaded.
    item = srch.search_item(cid=cid, name=name, offline=True,
                            server=server)
    if not item:
        return False

    claim_id = item["claim_id"]
    claim_name = item["claim_name"]
    channel = item["channel_name"]

    if not channel:
        channel = "@_Unknown_"

    subdir = os.path.join(ddir, channel)
    if own_dir:
        if not os.path.exists(subdir):
            try:
                os.mkdir(subdir)
            except (FileNotFoundError, PermissionError) as err:
                print(f"Cannot open directory for writing; {err}")
                return False
        ddir = subdir

    prnt.print_info_pre_get(item, offline=True)
    info_save = lbrynet_save(claim_id=claim_id, claim_name=claim_name,
                             ddir=ddir,
                             server=server)

    if not info_save:
        print(">>> Empty information from `lbrynet file save`")
        return False

    prnt.print_info_post_get(info_save)

    return info_save
