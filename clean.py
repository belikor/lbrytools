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
"""Functions to clean downloaded content from the LBRY network."""
import os
import requests

import lbrytools.funcs as funcs
import lbrytools.search as srch


def lbrynet_del(claim_id=None, claim_name=None, what="blobs",
                server="http://localhost:5279"):
    """Run the lbrynet file delete command on the given claim ID.

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
            name = 'some-video-name'
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        It returns `True` if the files were deleted successfully.
        It returns `False` if there is an error.
    """
    if not funcs.server_exists(server=server):
        return False

    if not claim_id:
        print("No input claim ID, using default value.")
        claim_id = "70dfefa510ca6eee7023a2a927e34d385b5a18bd"
        claim_name = "04-S"

    cmd_name = ["lbrynet",
                "file",
                "delete",
                "--claim_name=" + "'" + claim_name + "'"]
    if "'" in claim_name:
        cmd_name[3] = "--claim_name=" + '"' + claim_name + '"'

    cmd_id = cmd_name[:]
    cmd_id[3] = "--claim_id=" + claim_id

    if what in "blobs":
        print("Remove blobs")
    elif what in "both":
        print("Remove both, blobs and file")
        cmd_id.append("--delete_from_download_dir")
        cmd_name.append("--delete_from_download_dir")

    print("Remove: " + " ".join(cmd_id))
    print("Remove: " + " ".join(cmd_name))

    msg = {"method": cmd_id[1] + "_" + cmd_id[2],
           "params": {"claim_id": claim_id}}

    if what in "both":
        msg["params"]["delete_from_download_dir"] = True

    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    print("Blobs deleted")

    return True


def delete_single(uri=None, cid=None, name=None, invalid=False,
                  what="media",
                  server="http://localhost:5279"):
    """Delete a single file, and optionally the downloaded blobs.

    As long as the blobs are present, the content can be seeded
    to the network, and the full file can be restored.
    That is, while the blobs exist the file is not completely deleted.

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
    what: str, optional
        It defaults to `'media'`, in which case only the full media file
        (mp4, mp3, mkv, etc.) is deleted.
        If it is `'blobs'`, it will delete only the blobs.
        If it is `'both'`, it will delete both the media file
        and the blobs.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        It returns `True` if the claim was deleted successfully.
        If there is a problem or non existing claim, it will return `False`.
    """
    if not (uri or cid or name):
        print("Delete item by 'URI', 'claim_id', or 'name'.")
        print(f"uri={uri}, cid={cid}, name={name}")
        return False

    if (not isinstance(what, str)
            or what not in ("media", "blobs", "both")):
        print(">>> Error: what can only be 'media', 'blobs', 'both'")
        print(f"what={what}")
        return False

    # Searching online, with `offline=False`, will allow us to get the
    # `canonical_url` and full channel's name, otherwise we can only obtain
    # the `claim_name` and a simple channel name.
    item = srch.search_item(uri=uri, cid=cid, name=name, offline=invalid,
                            server=server)
    if not item:
        return False

    claim_id = item["claim_id"]

    if invalid:
        claim_name = item["claim_name"]
        channel = item["channel_name"]
    else:
        claim_uri = item["canonical_url"]
        claim_name = item["name"]
        if ("signing_channel" in item
                and "canonical_url" in item["signing_channel"]):
            channel = item["signing_channel"]["canonical_url"]
            channel = channel.split("lbry://")[1]
        else:
            channel = "@_Unknown_"

    # Searching offline is necessary to get the download path,
    # and blob information.
    item = srch.search_item(cid=claim_id, offline=True,
                            server=server)

    if not item:
        print("No claim found locally, probably already deleted.")
        return True

    path = item["download_path"]
    blobs = int(item["blobs_completed"])
    blobs_full = int(item["blobs_in_stream"])

    if invalid:
        print(f"claim_name: {claim_name}")
    else:
        print(f"canonical_url: {claim_uri}")

    print(f"claim_id: {claim_id}")
    print(f"Blobs found: {blobs} of {blobs_full}")

    if what in "media":
        print(f"Remove media file: {path}")

        if path:
            os.remove(path)
            print("Media file deleted")
        else:
            print("No media found locally, probably already deleted.")
        return True

    status = lbrynet_del(claim_id, claim_name=claim_name, what=what,
                         server=server)
    return status


if __name__ == "__main__":
    delete_single("1M")  # assuming it was downloaded first
