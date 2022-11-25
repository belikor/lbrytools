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
"""Functions to get the peer list of all claims from a single channel."""
import concurrent.futures as fts
import time

import lbrytools.funcs as funcs
import lbrytools.search_ch as srch_ch
import lbrytools.peers_base as prs


def process_ch_peers(base_peers_info, print_msg=False):
    """Process results from the channel peer search."""
    channel = base_peers_info["channel"]
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
        return {"channel": channel,
                "n_claims": n_claims,
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

    for num, info in enumerate(streams_info, start=1):
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
            sd_hash = "0"
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

    return {"channel": channel,
            "n_claims": n_claims,
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
        - 'channel': if no claims were found, it will be the same
          as the input `channel`. If at least one claim was found,
          it will be the canonical name of the channel such as `@channel#2c`
        - 'n_claims': same as input `number`
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
          it should be larger than 1.0 to indicate a well seeded channel.
        - 'peer_ratio_all': it is the ratio `total_peers_all/n_streams`,
          approximately how many peers in total are in each downloadable claim.
        - 'hosting_coverage': it is the ratio `streams_with_hosts/n_streams`,
          how much of the channel is seeded by users; if it's 0.0 no stream
          is seeded by users, if it's 1.0 all streams are seeded at least
          by one user peer.
        - 'hosting_coverage_all': ratio `streams_with_hosts_all/n_streams`
          how much of the channel is seeded by any type of peer.
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
        results = prs.calculate_peers(claim=None, print_msg=False,
                                      server=server)

        base_peers_info = {"channel": channel,
                           "n_claims": number,
                           "n_streams": 0,
                           "streams_info": results}

        peers_info = process_ch_peers(base_peers_info, print_msg=print_msg)
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
            results = executor.map(prs.calculate_peers,
                                   claims, falses,
                                   servers)
            print("Waiting for peer search to finish; "
                  f"max threads: {threads}")
            results = list(results)  # generator to list
    else:
        for claim in claims:
            print("Waiting for peer search to finish")
            result = prs.calculate_peers(claim=claim, print_msg=False,
                                         server=server)
            results.append(result)

    n_streams = 0

    for result in results:
        if "source" not in result["stream"]["value"]:
            continue
        n_streams += 1

    ch = results[0]["stream"]["signing_channel"]["canonical_url"]
    ch = ch.split("lbry://")[1]

    base_peers_info = {"channel": ch,
                       "n_claims": n_claims,
                       "n_streams": n_streams,
                       "streams_info": results}
    print()
    peers_info = process_ch_peers(base_peers_info, print_msg=print_msg)

    if print_time:
        e_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
        print(f"start: {s_time}")
        print(f"end:   {e_time}")

    return peers_info


def get_summary(peers_info):
    """Calculate a summary paragraph of the results from the peer search."""
    channel = peers_info["channel"]

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

    out = [f"Channel: {channel}",
           f"Claims searched: {n_claims}",
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

    summary = "\n".join(out)

    return summary


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
        size = info["size"]
        seconds = info["duration"]
        local_node = info["local_node"]
        local_node = f"{local_node}"

        name = stream["name"]
        claim_id = stream["claim_id"]
        n_peers_tracker = len(info["peers_tracker"])
        n_peers_user = len(info["peers_user"])

        rels_time = int(stream["value"].get("release_time", 0))
        rels_time = time.strftime("%Y-%m-%d_%H:%M:%S%z",
                                  time.localtime(rels_time))

        if title:
            name = stream["value"].get("title") or name

        if sanitize:
            name = funcs.sanitize_text(name)

        vtype = stream["value_type"]

        stream_type = stream["value"].get("stream_type", 8 * "_")

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

        line += f"peers: {n_peers_user:2d} ({n_peers_tracker:2d})" + f"{sep} "
        line += f"hosted: {local_node:5s}" + f"{sep} "
        line += f"{name}"
        out.append(line)

    funcs.print_content(out, file=file, fdate=fdate)


def list_ch_peers(channel=None, number=2, threads=32,
                  print_msg=False,
                  claim_id=False, typ=True, title=False,
                  sanitize=False,
                  file=None, fdate=False, sep=";",
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
        - 'channel': if no claims were found, it will be the same
          as the input `channel`. If at least one claim was found,
          it will be the canonical name of the channel such as `@channel#2c`
        - 'n_claims': same as input `number`
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
          it should be larger than 1.0 to indicate a well seeded channel.
        - 'peer_ratio_all': it is the ratio `total_peers_all/n_streams`,
          approximately how many peers in total are in each downloadable claim.
        - 'hosting_coverage': it is the ratio `streams_with_hosts/n_streams`,
          how much of the channel is seeded by users; if it's 0.0 no stream
          is seeded by users, if it's 1.0 all streams are seeded at least
          by one user peer.
        - 'hosting_coverage_all': ratio `streams_with_hosts_all/n_streams`
          how much of the channel is seeded by any type of peer.
        - 'local_node': it is `True` if our `lbrynet` client is hosting
          at least one of the claims, meaning that the initial blobs
          are found in our system.
          Our local node is not counted when calculating 'streams_with_hosts',
          'total_peers', 'unique_nodes', 'peer_ratio', nor 'hosting_coverage'.
        - 'summary': a paragraph of text with the summary of the peer search
          for this channel. It can be printed to the terminal or displayed
          in other types of graphical interface.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    peers_info = search_ch_peers(channel=channel, number=number,
                                 threads=threads,
                                 print_msg=print_msg,
                                 server=server)

    summary = get_summary(peers_info)

    if peers_info["n_streams"] > 0:
        print()
        print_p_lines(peers_info,
                      cid=claim_id, typ=typ, title=title,
                      sanitize=sanitize,
                      file=file, fdate=fdate, sep=sep)

    print(80 * "-")

    funcs.print_content([summary], file=None, fdate=False)

    peers_info["summary"] = summary

    return peers_info


if __name__ == "__main__":
    list_ch_peers(channel="@Luke", number=53, threads=64)
#    list_ch_peers(channel="@rossmanngroup", number=50, threads=64)
#    list_ch_peers(channel="@AlphaNerd", number=50, threads=64)
