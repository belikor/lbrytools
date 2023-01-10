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
import concurrent.futures as fts
import os
import json
import time

import requests

import lbrytools.funcs as funcs
import lbrytools.search as srch


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


def process_claims_peers(base_peers_info,
                         channel=False,
                         print_msg=False):
    """Process results from the peer search of multiple claims."""
    if channel:
        ch = base_peers_info.get("channel", None)

    n_claims = base_peers_info["n_claims"]
    n_streams = base_peers_info["n_streams"]
    streams_info = base_peers_info["streams_info"]

    total_size = 0
    total_duration = 0
    streams_with_hosts = 0
    streams_with_hosts_all = 0
    total_peers = 0
    total_peers_all = 0
    u_nodes_id = []
    unique_nodes = []
    u_trackers_addr = []
    unique_trackers = []
    peer_ratio = 0.0
    peer_ratio_all = 0.0
    hosting_coverage = 0.0
    hosting_coverage_all = 0.0
    local_node = False

    if n_streams < 1:
        peers_info = {"n_claims": n_claims,
                      "n_streams": n_streams,
                      "streams_info": streams_info,
                      "total_size": total_size,
                      "total_duration": total_duration,
                      "streams_with_hosts": streams_with_hosts,
                      "streams_with_hosts_all": streams_with_hosts_all,
                      "total_peers": total_peers,
                      "total_peers_all": total_peers_all,
                      "unique_nodes": unique_nodes,
                      "unique_trackers": unique_trackers,
                      "peer_ratio": peer_ratio,
                      "peer_ratio_all": peer_ratio_all,
                      "hosting_coverage": hosting_coverage,
                      "hosting_coverage_all": hosting_coverage_all,
                      "local_node": local_node}

        if channel and ch:
            peers_info["channel"] = ch

        return peers_info

    for num, info in enumerate(streams_info, start=1):
        if "stream" not in info:
            continue

        stream = info["stream"]
        peers_all = info["peers"]
        peers_user = info["peers_user"]
        total_size += info["size"]
        total_duration += info["duration"]
        loc_node = info["local_node"]
        local_node = local_node or loc_node

        name = stream["name"]
        claim_id = stream["claim_id"]
        vtype = stream["value_type"]

        if "source" not in stream["value"]:
            sd_hash = 8 * "_"
        else:
            sd_hash = stream["value"]["source"]["sd_hash"]

        n_peers_user = len(peers_user)
        n_peers_all = len(peers_all)

        if print_msg:
            print(f"Stream {num}/{n_claims}")
            print(f"claim_name: {name}")
            print(f"claim_id: {claim_id}")
            print(f"sd_hash: {sd_hash}")
            print(f"Claim type: {vtype}")
            print(f"User peers: {n_peers_user}")
            print(f"Total peers: {n_peers_all}")

        if not peers_all:
            peer_ratio = total_peers/num
            peer_ratio_all = total_peers_all/num

            if print_msg:
                print(f"Average user peers per stream: {peer_ratio:.4f}")
                print(f"Average peers per stream: {peer_ratio_all:.4f}")
                print(f"Locally hosted: {loc_node}")
                print()
            continue

        total_peers += n_peers_user
        total_peers_all += n_peers_all

        peer_ratio = total_peers/num
        peer_ratio_all = total_peers_all/num

        if print_msg:
            print(f"Average user peers per stream: {peer_ratio:.4f}")
            print(f"Average peers per stream: {peer_ratio_all:.4f}")
            print(f"Locally downloaded: {loc_node}")
            print()

        if n_peers_user > 0:
            streams_with_hosts += 1

        streams_with_hosts_all += 1

        for peer in peers_all:
            node = peer["node_id"]
            address = peer["address"]

            if node and node not in u_nodes_id:
                u_nodes_id.append(node)
                unique_nodes.append(peer)

            if node is None and address not in u_trackers_addr:
                u_trackers_addr.append(address)
                unique_trackers.append(peer)

    peer_ratio = total_peers/n_streams
    peer_ratio_all = total_peers_all/n_streams

    hosting_coverage = streams_with_hosts/n_streams
    hosting_coverage_all = streams_with_hosts_all/n_streams

    peers_info = {"n_claims": n_claims,
                  "n_streams": n_streams,
                  "streams_info": streams_info,
                  "total_size": total_size,
                  "total_duration": total_duration,
                  "streams_with_hosts": streams_with_hosts,
                  "streams_with_hosts_all": streams_with_hosts_all,
                  "total_peers": total_peers,
                  "total_peers_all": total_peers_all,
                  "unique_nodes": unique_nodes,
                  "unique_trackers": unique_trackers,
                  "peer_ratio": peer_ratio,
                  "peer_ratio_all": peer_ratio_all,
                  "hosting_coverage": hosting_coverage,
                  "hosting_coverage_all": hosting_coverage_all,
                  "local_node": local_node}

    if channel and ch:
        peers_info["channel"] = ch

    return peers_info


def search_peers_th(claim, server):
    """Wrapper to use with threads to search for multiple claim peers."""
    stream_info = claim

    if "resolved" in claim and not claim["resolved"]:
        return stream_info

    if "resolved" in claim and claim["resolved"]:
        claim = claim["resolved"]

    stream_info = calculate_peers(claim=claim, print_msg=False,
                                  server=server)

    return stream_info


def search_m_claim_peers(claims=None, resolve=True, threads=32,
                         print_msg=False,
                         server="http://localhost:5279"):
    """Search the peers for the given list of claims.

    Parameters
    ----------
    claims: list of str or list of dict
        Each element of the list is a claim name or claim ID
        that we wish to examine for peers.
        It can also be a list of resolved dictionaries if `resolve=False`.
    resolve: bool, optional
        It defaults to `True`, in which case `claims` is assumed
        to be a list of claim URIs or claim IDs, and each of them will be
        individually resolved.
        If it is `False` then we assume `claims` already has
        the resolved claims, so we don't need to resolve them again.
    threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to search for peers,
        meaning that many claims will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
    print_msg: bool, optional
        It defaults to `False`, in which case only the final result
        will be shown.
        If it is `True` a summary of each claim will be printed.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        It has many keys:
        - 'n_claims': size of the input `claims` list.
        - 'n_streams': number of actual streams, that is,
          claims that can be downloaded. It may be the same as `n_claims`
          or even zero.
        - 'streams_info': list of dict; each dictionary has information
          on each claim searched for peers; the keys are
          - 'stream': the resolved information of the claim, or `None`
          - 'peers': list of peers for the claim; each peer is a dict
            with keys 'address'  (IP), 'node_id', 'tcp_port', and 'udp_port'
          - 'peers_tracker': list of peers corresponding to fixed trackers,
            for which the 'node_id' is `None`.
          - 'peers_user': list of peers corresponding to user nodes
            running their own `lbrynet` daemons. For these the 'node_id'
            is a 96-character string.
          - 'size': size in bytes of the claim; could be zero
          - 'duration': duration in seconds of the claim; could be zero
          - 'local_node': boolean indicating if the claim is hosted
            in our `lbrynet` client or not
        - 'total_size': total size in bytes of all `n_streams` together
        - 'total_duration': total duration in seconds of all `n_streams`
          together
        - 'streams_with_hosts': number of streams that have at least
          one user peer hosting the stream; the value goes from 0
          to `n_streams`.
          A stream is counted as having a host if it has either
          the manifest blob `sd_hash` or the first data blob.
        - 'streams_with_hosts_all': number of streams that have any type
          of peer (user or tracker).
        - 'total_peers': total number of user peers found for all `n_streams`
        - 'total_peers_all': total number of peers (user and tracker).
        - 'unique_nodes': list with dictionaries of unique peers
          as calculated from their node IDs, meaning that a single node ID
          only appears once.
        - 'unique_trackers': list with dictionaries of unique tracker peers
          as calculated from their IP addresses, meaning that a single
          IP address only appears once. Tracker peers have an empty node ID.
        - 'peer_ratio': it is the ratio `total_peers/n_streams`,
          approximately how many user peers are in each downloadable claim;
          it should be larger than 1.0 to indicate a well seeded group
          of claims.
        - 'peer_ratio_all': it is the ratio `total_peers_all/n_streams`,
          approximately how many peers in total are in each downloadable claim.
        - 'hosting_coverage': it is the ratio `streams_with_hosts/n_streams`,
          how much of the group of claims is seeded by users;
          if it's 0.0 no stream is seeded by users, if it's 1.0 all streams
          are seeded at least by one user peer.
        - 'hosting_coverage_all': ratio `streams_with_hosts_all/n_streams`
          how much of the group of claims is seeded by any type of peer.
        - 'local_node': it is `True` if our `lbrynet` client is hosting
          at least one of the claims, meaning that the initial blobs
          are found in our system.
          Our local node is not counted when calculating 'streams_with_hosts',
          'total_peers', 'unique_nodes', 'peer_ratio', nor 'hosting_coverage'.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if resolve:
        resolved_claims = srch.resolve_claims(claims)
    else:
        resolved_claims = claims

    n_claims = len(claims)
    n_streams = 0

    streams_info = []

    # Iterables to be passed to the ThreadPoolExecutor
    servers = (server for n in range(n_claims))

    if threads:
        with fts.ThreadPoolExecutor(max_workers=threads) as executor:
            results = executor.map(search_peers_th,
                                   resolved_claims,
                                   servers)

            print("Waiting for peer search to finish; "
                  f"max threads: {threads}")
            streams_info = list(results)  # generator to list
    else:
        for claim in resolved_claims:
            print("Waiting for peer search to finish")
            result = search_peers_th(claim, server)

            streams_info.append(result)

    for info in streams_info:
        if "stream" not in info:
            continue
        elif info["stream"]["value_type"] in ("stream"):
            n_streams += 1

    base_peers_info = {"n_claims": n_claims,
                       "n_streams": n_streams,
                       "streams_info": streams_info}

    peers_info = process_claims_peers(base_peers_info,
                                      channel=False,
                                      print_msg=print_msg)

    return peers_info


def get_summary(peers_info, channel=False):
    """Calculate a summary paragraph of the results from the peer search."""
    if channel:
        ch = peers_info.get("channel", None)

    n_claims = peers_info["n_claims"]
    n_streams = peers_info["n_streams"]
    total_size = peers_info["total_size"]
    total_seconds = peers_info["total_duration"]
    streams_with_hosts = peers_info["streams_with_hosts"]
    streams_with_hosts_all = peers_info["streams_with_hosts_all"]
    total_peers = peers_info["total_peers"]
    total_peers_all = peers_info["total_peers_all"]

    n_nodes = len(peers_info["unique_nodes"])
    n_trackers = len(peers_info["unique_trackers"])

    if peers_info["local_node"]:
        n_nodes = f"{n_nodes} + 1"

    peer_ratio = peers_info["peer_ratio"]
    peer_ratio_all = peers_info["peer_ratio_all"]
    hosting_coverage = peers_info["hosting_coverage"] * 100
    hosting_coverage_all = peers_info["hosting_coverage_all"] * 100

    total_size_gb = total_size / (1024**3)
    days = (total_seconds / 3600) / 24
    hr = total_seconds // 3600
    mi = (total_seconds % 3600) // 60
    sec = (total_seconds % 3600) % 60
    duration = f"{hr} h {mi} min {sec} s, or {days:.4f} days"

    out = [f"Claims searched: {n_claims}",
           f"Downloadable streams: {n_streams}",
           f"- Streams with at least one user host: {streams_with_hosts}",
           f"- Streams with all types of host: {streams_with_hosts_all}",
           f"- Size of streams: {total_size_gb:.4f} GiB",
           f"- Duration of streams: {duration}",
           "",
           f"Total user peers in all searched claims: {total_peers}",
           f"Total peers in all searched claims: {total_peers_all}",
           f"Total unique user peers (nodes) hosting streams: {n_nodes}",
           f"Total unique tracker peers hosting streams: {n_trackers}",
           f"Average number of user peers per stream: {peer_ratio:.4f}",
           f"Average number of total peers per stream: {peer_ratio_all:.4f}",
           f"User hosting coverage: {hosting_coverage:.2f}%",
           f"Total hosting coverage: {hosting_coverage_all:.2f}%"]

    if channel and ch:
        out.insert(0, f"Channel: {ch}")

    summary = "\n".join(out)

    return summary


def get_claim_summary(stream_info,
                      cid=False, typ=True, title=False,
                      inline=False, sanitize=False,
                      sep=";"):
    """Calculate a line of text or paragraph of a single claim peer search."""
    stream = stream_info["stream"]
    size = stream_info["size"]
    seconds = stream_info["duration"]
    local_node = stream_info["local_node"]
    local_node = f"{local_node}"

    uri = stream["canonical_url"]
    name = stream["name"]
    claim_id = stream["claim_id"]
    n_peers_tracker = len(stream_info["peers_tracker"])
    n_peers_user = len(stream_info["peers_user"])

    if inline:
        time_fmt = funcs.TFMTp
    else:
        time_fmt = funcs.TFMT

    rels_time = int(stream["value"].get("release_time", 0))

    if not rels_time:
        rels_time = 8 * "_"
    else:
        rels_time = time.strftime(time_fmt, time.gmtime(rels_time))

    create_time = stream["meta"].get("creation_timestamp", 0)
    create_time = time.strftime(time_fmt, time.gmtime(create_time))

    if "source" not in stream["value"]:
        sd_hash = 8 * "_"
    else:
        sd_hash = stream["value"]["source"]["sd_hash"]

    claim_title = stream["value"].get("title", "(no title)")

    if title:
        name = stream["value"].get("title") or name

    if sanitize:
        name = funcs.sanitize_text(name)
        claim_title = funcs.sanitize_text(claim_title)

    vtype = stream["value_type"]

    stream_type = stream["value"].get("stream_type", 8 * "_")

    name = f'"{name}"'
    mi = seconds // 60
    sec = seconds % 60
    duration = f"{mi:3d}:{sec:02d}"
    size_mb = size / (1024**2)

    if rels_time == 8 * "_":
        line = create_time + f"{sep} "
    else:
        line = rels_time + f"{sep} "

    if cid:
        line += f"{claim_id}" + f"{sep} "

    if typ:
        line += f"{vtype:10s}" + f"{sep} "
        line += f"{stream_type:9s}" + f"{sep} "

    line += f"{duration}" + f"{sep} "
    line += f"{size_mb:9.4f} MB" + f"{sep} "

    line += f"peers: {n_peers_user:2d} ({n_peers_tracker:2d})" + f"{sep} "
    line += f"hosted: {local_node:5s}" + f"{sep} "
    line += f"{name}"

    if inline:
        out = [line]
    else:
        out = [f"canonical_url: {uri}",
               f"claim_id: {claim_id}",
               f"title: {claim_title}",
               f"release_time:  {rels_time}",
               f"creation_time: {create_time}",
               f"value_type: {vtype}",
               f"stream_type: {stream_type}",
               f"size: {size_mb:.4f} MB",
               f"duration: {mi} min {sec} s",
               f"sd_hash: {sd_hash}",
               f"user peers: {n_peers_user}",
               f"tracker peers: {n_peers_tracker}",
               f"locally hosted: {local_node}"]

    summary = "\n".join(out)

    return summary


def print_claims_lines(peers_info,
                       inline=True,
                       cid=False, typ=True, title=False,
                       sanitize=False,
                       file=None, fdate=False, sep=";"):
    """Print a summary text for each claim of the peer search."""
    n_claims = peers_info["n_claims"]
    streams_info = peers_info["streams_info"]

    content = []

    for num, info in enumerate(streams_info, start=1):
        if "resolved" in info:
            original = info["original"]
            text = f"Claim does not exist: {original}"
        else:
            text = get_claim_summary(info,
                                     cid=cid, typ=typ, title=title,
                                     inline=inline, sanitize=sanitize,
                                     sep=sep)

        if inline:
            content.append(f"{num:4d}/{n_claims:4d}" + f"{sep} " + text)
        else:
            content.append(f"Claim {num}/{n_claims}" + "\n" + text)

    if inline:
        out = content
    else:
        paragraphs = []

        for par in content:
            paragraphs.append(par + "\n")

        out = paragraphs

    funcs.print_content(out, file=file, fdate=fdate)
