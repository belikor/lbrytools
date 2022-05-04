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
"""Functions to get the peer list of all claims from a single channel.

It uses `peer_list` to get the peers that have the blobs of a single claim.
In this way we can determine if many users are currently seeding the claims
from a channel.

Originally based on @miko:f/peer-lister:9
"""
import concurrent.futures as fts
import os
import json
import time

import requests

import lbrytools.funcs as funcs
import lbrytools.search_ch as srch_ch


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

    n_peers = len(peers)

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
        print(f"peers: {n_peers}")

    return {"stream": claim,
            "peers": peers,
            "size": size,
            "duration": seconds,
            "local_node": local}


def process_results(base_peers_info, print_msg=False):
    """Process results from the peer search."""
    channel = base_peers_info["channel"]
    n_claims = base_peers_info["n_claims"]
    n_streams = base_peers_info["n_streams"]
    streams_info = base_peers_info["streams_info"]

    total_size = 0
    total_duration = 0
    streams_with_hosts = 0
    total_peers = 0
    unique_nodes = []
    peer_ratio = 0.0
    hosting_coverage = 0
    local_node = False
    g_local_node = False

    if n_streams < 1:
        return {"channel": channel,
                "n_claims": n_claims,
                "n_streams": n_streams,
                "streams_info": streams_info,
                "total_size": total_size,
                "total_duration": total_duration,
                "streams_with_hosts": streams_with_hosts,
                "total_peers": total_peers,
                "unique_nodes": unique_nodes,
                "peer_ratio": peer_ratio,
                "hosting_coverage": hosting_coverage,
                "local_node": g_local_node}

    for num, info in enumerate(streams_info, start=1):
        stream = info["stream"]
        peers = info["peers"]
        total_size += info["size"]
        total_duration += info["duration"]
        local_node = info["local_node"]
        g_local_node = g_local_node or local_node

        name = stream["name"]
        claim_id = stream["claim_id"]

        if "source" not in stream["value"]:
            sd_hash = "0"
        else:
            sd_hash = stream["value"]["source"]["sd_hash"]

        n_peers = len(peers)

        if print_msg:
            print(f"Stream {num}/{n_claims}")
            print(f"claim_name: {name}")
            print(f"claim_id: {claim_id}")
            print(f"sd_hash: {sd_hash}")
            print(f"peers: {n_peers}")

        if not peers:
            peer_ratio = total_peers/num
            if print_msg:
                print(f"Average peers per stream: {peer_ratio:.4f}")
                print(f"Locally hosted: {local_node}")
                print()
            continue

        total_peers += len(peers)
        peer_ratio = total_peers/num
        if print_msg:
            print(f"Average peers per stream: {peer_ratio:.4f}")
            print(f"Locally downloaded: {local_node}")
            print()
        streams_with_hosts += 1

        for p in peers:
            if p["node_id"] not in unique_nodes:
                unique_nodes.append(p["node_id"])

    peer_ratio = total_peers/n_streams
    hosting_coverage = streams_with_hosts/n_streams

    return {"channel": channel,
            "n_claims": n_claims,
            "n_streams": n_streams,
            "streams_info": streams_info,
            "total_size": total_size,
            "total_duration": total_duration,
            "streams_with_hosts": streams_with_hosts,
            "total_peers": total_peers,
            "unique_nodes": unique_nodes,
            "peer_ratio": peer_ratio,
            "hosting_coverage": hosting_coverage,
            "local_node": g_local_node}


def search_ch_peers(channel=None, number=2, threads=32,
                    print_time=True, print_msg=False,
                    server="http://localhost:5279"):
    """Search the peers for the claims of a channel.

    Parameters
    ----------
    channel: str
        Channel from which to search claims and find peers.
    number: int, optional
        It defaults to 2.
        It is the number of claims, starting from the newest one
        and going back in time, that will be searched for peers.
    threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to search for peers,
        meaning that many claims will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
    print_time: bool, optional
        It defaults to `True`, in which case the time taken
        to search the peers will be printed.
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
        - 'channel': same as input `channel`
        - 'n_claims': same as input `number`
        - 'n_streams': number of actual streams, that is,
          claims that can be downloaded. It may be the same as `n_claims`
          or even zero.
        - 'streams_info': list of dict; each dictionary has information
          on each claim searched for peers; the keys are
          - 'stream': the resolved information of the claim, or `None`
          - 'peers': list of peers for the claim; each peer is a dict
            with keys 'address'  (IP), 'node_id', 'tcp_port', and 'udp_port'
          - 'size': size in bytes of the claim; could be zero
          - 'duration': duration in seconds of the claim; could be zero
          - 'local_node': boolean indicating if the claim is hosted
            in our `lbrynet` client or not
        - 'total_size': total size in bytes of all `n_streams` together
        - 'total_duration': total duration in seconds of all `n_streams`
          together
        - 'streams_with_hosts': number of streams that have at least
          one peer hosting the stream; the value goes from 0 to `n_streams`.
          A stream is counted as having a host if it has either
          the manifest blob `sd_hash` or the first data blob.
        - 'total_peers': total number of peers found for all `n_streams`
        - 'unique_peers': list with node IDs from the peers
          found in all `n_streams`; the nodes are unique, so a node ID
          only appears once in the list
        - 'peer_ratio': it is the ratio total_peers/n_streams,
          approximately how many peers are in each downloadable claim;
          it should be larger than 1.0 to indicate a well seeded channel
        - 'hosting_coverage': it is the ratio streams_with_hosts/n_streams,
          how much of the channel is seeded; if it's 0.0 no stream is seeded,
          if it's 1.0 all streams are seeded at least by one peer.
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

    if print_time:
        s_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())

    # Ideally, it should return only stream claims.
    # srch_ch.get_streams(...)
    claims = srch_ch.ch_search_latest(channel=channel, number=number,
                                      server=server)
    if not claims:
        results = calculate_peers(claim=None, print_msg=False,
                                  server=server)

        base_peers_info = {"channel": channel,
                           "n_claims": number,
                           "n_streams": 0,
                           "streams_info": results}

        peers_info = process_results(base_peers_info, print_msg=print_msg)
        return peers_info

    results = []

    print()
    print("Count the number of peers")
    print(80 * "-")

    # Iterables to be passed to the ThreadPoolExecutor
    n_claims = len(claims)
    falses = (False for n in range(n_claims))
    servers = (server for n in range(n_claims))

    if threads:
        with fts.ThreadPoolExecutor(max_workers=threads) as executor:
            # The input must be iterables
            results = executor.map(calculate_peers,
                                   claims, falses,
                                   servers)
            print("Waiting for peer search to finish; "
                  f"max threads: {threads}")
            results = list(results)  # generator to list
    else:
        for claim in claims:
            print("Waiting for peer search to finish")
            result = calculate_peers(claim=claim, print_msg=False,
                                     server=server)
            results.append(result)

    n_streams = 0
    for result in results:
        if "source" not in result["stream"]["value"]:
            continue
        n_streams += 1

    b_peers_info = {"channel": channel,
                    "n_claims": n_claims,
                    "n_streams": n_streams,
                    "streams_info": results}
    print()
    peers_info = process_results(b_peers_info, print_msg=print_msg)

    if print_time:
        e_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
        print(f"start: {s_time}")
        print(f"end:   {e_time}")

    return peers_info


def print_p_lines(peers_info,
                  cid=False, typ=True, title=False,
                  sanitize=False,
                  file=None, fdate=False, sep=";"):
    """Print a summary for each claim of the peer search."""
    n_claims = peers_info["n_claims"]
    streams_info = peers_info["streams_info"]

    out = []

    for num, info in enumerate(streams_info, start=1):
        stream = info["stream"]
        peers = info["peers"]
        size = info["size"]
        seconds = info["duration"]
        local_node = info["local_node"]
        local_node = f"{local_node}"

        name = stream["name"]
        rels_time = int(stream["value"].get("release_time", 0))
        rels_time = time.strftime("%Y-%m-%d_%H:%M:%S%z",
                                  time.localtime(rels_time))

        if title and "title" in stream["value"]:
            name = stream["value"]["title"]

        if sanitize:
            name = funcs.sanitize_text(name)

        vtype = stream["value_type"]

        if "stream_type" in stream["value"]:
            stream_type = stream["value"].get("stream_type")
        else:
            stream_type = 8 * "_"

        claim_id = stream["claim_id"]
        n_peers = len(peers)

        name = f'"{name}"'
        mi = seconds // 60
        sec = seconds % 60
        duration = f"{mi:3d}:{sec:02d}"
        size_mb = size / (1024**2)

        line = f"{num:4d}/{n_claims:4d}" + f"{sep} "
        line += rels_time + f"{sep} "

        if cid:
            line += f"{claim_id}" + f"{sep} "

        if typ:
            line += f"{vtype:10s}" + f"{sep} "
            line += f"{stream_type:9s}" + f"{sep} "

        line += f"{duration}" + f"{sep} "
        line += f"{size_mb:9.4f} MB" + f"{sep} "

        line += f"peers: {n_peers:2d}" + f"{sep} "
        line += f"hosted: {local_node:5s}" + f"{sep} "
        line += f"{name}"
        out.append(line)

    funcs.print_content(out, file=file, fdate=fdate)


def print_p_summary(peers_info,
                    file=None, fdate=False):
    """Print a summary paragraph of the results from the peer search."""
    channel = peers_info["channel"]
    n_claims = peers_info["n_claims"]
    n_streams = peers_info["n_streams"]
    total_size = peers_info["total_size"]
    total_seconds = peers_info["total_duration"]
    streams_with_hosts = peers_info["streams_with_hosts"]
    total_peers = peers_info["total_peers"]
    n_nodes = len(peers_info["unique_nodes"])

    if peers_info["local_node"]:
        n_nodes = f"{n_nodes} + 1"

    peer_ratio = peers_info["peer_ratio"]
    hosting_coverage = peers_info["hosting_coverage"] * 100

    total_size_gb = total_size / (1024**3)
    days = (total_seconds / 3600) / 24
    hr = total_seconds // 3600
    mi = (total_seconds % 3600) // 60
    sec = (total_seconds % 3600) % 60
    duration = f"{hr} h {mi} min {sec} s, or {days:.4f} days"

    out_list = [f"Channel: {channel}",
                f"Claims searched: {n_claims}",
                f"Downloadable streams: {n_streams}",
                f"- Streams that have at least one host: {streams_with_hosts}",
                f"- Size of streams: {total_size_gb:.4f} GiB",
                f"- Duration of streams: {duration}",
                "",
                f"Total peers in all searched claims: {total_peers}",
                f"Total unique peers (nodes) hosting streams: {n_nodes}",
                f"Average number of peers per stream: {peer_ratio:.4f}",
                f"Hosting coverage: {hosting_coverage:.2f}%"]

    funcs.print_content(out_list, file=file, fdate=fdate)


def print_peers_info(peers_info,
                     claim_id=False, typ=False, title=False,
                     sanitize=False,
                     file=None, fdate=None, sep=";"):
    """Print the summary lines and paragraph of the peer search."""
    print_p_lines(peers_info,
                  cid=claim_id, typ=typ, title=title,
                  sanitize=sanitize,
                  file=file, fdate=fdate, sep=sep)

    print_p_summary(peers_info, file=None, fdate=fdate)


def list_peers(channel=None, number=2, threads=32,
               print_msg=False,
               claim_id=False, typ=True, title=False,
               sanitize=False,
               file=None, fdate=None, sep=";",
               server="http://localhost:5279"):
    """Print the peers for the claims of a given channel.

    Parameters
    ----------
    channel: str
        Channel from which to search peers that are hosting its claims.
    number: int, optional
        It defaults to 2.
        It is the number of claims, starting from the newest one
        and going back in time, that will be searched for peers.
    threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to search for peers,
        meaning that many claims will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
    print_msg: bool, optional
        It defaults to `False`, in which case only the final result
        will be shown.
        If it is `True` a summary of each claim will be printed.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim ID for the individual claims.
    typ: bool, optional
        It defaults to `True`, in which case the claim type and stream type
        will be printed for the individual claims.
    title: bool, optional
        It defaults to `False`, in which case the claim name will be printed.
        If it is `True` it will print the claim title instead.
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the claim name nor claim title.
        If it is `True` it will remove these unicode characters.
        This option requires the `emoji` package to be installed.
    file: str, optional
        It defaults to `None`.
        It must be a user writable path to which the summary will be written.
        Otherwise the summary will be printed to the terminal.
    fdate: bool, optional
        It defaults to `False`.
        If it is `True` it will add the date to the name of the summary file.
    sep: str, optional
        It defaults to `;`. It is the separator character between
        the data fields in the printed summary. Since the claim name
        can have commas, a semicolon `;` is used by default.
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
        - 'channel': same as input `channel`
        - 'n_claims': same as input `number`
        - 'n_streams': number of actual streams, that is,
          claims that can be downloaded. It may be the same as `n_claims`
          or even zero.
        - 'streams_info': list of dict; each dictionary has information
          on each claim searched for peers; the keys are
          - 'stream': the resolved information of the claim, or `None`
          - 'peers': list of peers for the claim; each peer is a dict
            with keys 'address'  (IP), 'node_id', 'tcp_port', and 'udp_port'
          - 'size': size in bytes of the claim; could be zero
          - 'duration': duration in seconds of the claim; could be zero
          - 'local_node': boolean indicating if the claim is hosted
            in our `lbrynet` client or not
        - 'total_size': total size in bytes of all `n_streams` together
        - 'total_duration': total duration in seconds of all `n_streams`
          together
        - 'streams_with_hosts': number of streams that have at least
          one peer hosting the stream; the value goes from 0 to `n_streams`.
          A stream is counted as having a host if it has either
          the manifest blob `sd_hash` or the first data blob.
        - 'total_peers': total number of peers found for all `n_streams`
        - 'unique_peers': list with node IDs from the peers
          found in all `n_streams`; the nodes are unique, so a node ID
          only appears once in the list
        - 'peer_ratio': it is the ratio total_peers/n_streams,
          approximately how many peers are in each downloadable claim;
          it should be larger than 1.0 to indicate a well seeded channel
        - 'hosting_coverage': it is the ratio streams_with_hosts/n_streams,
          how much of the channel is seeded; if it's 0.0 no stream is seeded,
          if it's 1.0 all streams are seeded at least by one peer.
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

    peers_info = search_ch_peers(channel=channel, number=number,
                                 threads=threads,
                                 print_msg=print_msg,
                                 server=server)

    if peers_info["n_streams"] < 1:
        return peers_info

    print_peers_info(peers_info,
                     claim_id=claim_id, typ=typ, title=title,
                     sanitize=sanitize,
                     file=file, fdate=fdate, sep=sep)

    return peers_info


if __name__ == "__main__":
    list_peers(channel="@Luke", number=53, threads=64)
#    list_peers(channel="@rossmanngroup", number=50, threads=64)
#    list_peers(channel="@AlphaNerd", number=50, threads=64)
