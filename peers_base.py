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
"""Base functions to get the list of peers of a downloadable claim (stream).

It uses `peer_list` with the `sd_hash` of a claim to find the peers online.

These methods are used by other methods that find the list of peers
of a single claim, multiple claims, a channel, or multiple channels.

Originally based on @miko:f/peer-lister:9
"""
import os
import json

import requests

import lbrytools.funcs as funcs


def get_peers(blob,
              server="http://localhost:5279"):
    """Get a list of peers from the given blob hash."""
    msg = {"method": "peer_list",
           "params": {"blob_hash": blob,
                      "page_size": 9999}}

    output = requests.post(server, json=msg).json()
    if not output or "error" in output:
        return False

    peers = output["result"]["items"]

    return peers


def search_own_node(sd_hash,
                    server="http://localhost:5279"):
    """Return peer information on the first data blob."""
    blobdir = funcs.get_bdir(server=server)
    blob_file = os.path.join(blobdir, sd_hash)

    if not os.path.isfile(blob_file):
        return False

    with open(blob_file) as fd_sd_hash:
        data = json.load(fd_sd_hash)
        first = data["blobs"][0]["blob_hash"]

    return get_peers(first, server=server)


def calculate_peers(claim=None, print_msg=True,
                    server="http://localhost:5279"):
    """Return peer information for a given stream claim."""
    if not claim or "source" not in claim["value"]:
        return {"stream": claim,
                "peers": [],
                "peers_tracker": [],
                "peers_user": [],
                "size": 0,
                "duration": 0,
                "local_node": False}

    name = claim["name"]
    claim_id = claim["claim_id"]
    sd_hash = claim["value"]["source"]["sd_hash"]
    peers = get_peers(sd_hash, server=server)

    local = False

    blobdir = funcs.get_bdir(server=server)
    blob_file = os.path.join(blobdir, sd_hash)

    if os.path.isfile(blob_file):
        local = True

    first_blob_peers = search_own_node(sd_hash, server=server)

    if first_blob_peers:
        for fpeer in first_blob_peers:
            if fpeer not in peers:
                peers.append(fpeer)

    peers_tracker = []
    peers_user = []

    for peer in peers:
        if peer.get("node_id", None):
            peers_user.append(peer)
        else:
            peers_tracker.append(peer)

    n_peers_tracker = len(peers_tracker)
    n_peers_user = len(peers_user)

    source_info = claim["value"]
    size = int(source_info["source"].get("size", 0))

    seconds = 0
    if "video" in source_info:
        seconds = source_info["video"].get("duration", 0)
    elif "audio" in source_info:
        seconds = source_info["audio"].get("duration", 0)

    if print_msg:
        print(f"claim_name: {name}")
        print(f"claim_id: {claim_id}")
        print(f"sd_hash: {sd_hash}")
        print(f"tracker peers: {n_peers_tracker}")
        print(f"user peers: {n_peers_user}")
        print(f"locally hosted: {local}")

    return {"stream": claim,
            "peers": peers,
            "peers_tracker": peers_tracker,
            "peers_user": peers_user,
            "size": size,
            "duration": seconds,
            "local_node": local}
