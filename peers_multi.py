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
"""Functions to get the peer list of all claims from various channels."""
import concurrent.futures as fts
import time

import lbrytools.funcs as funcs
import lbrytools.peers as prs
import lbrytools.channels as chs


def process_chs_peers(base_chs_peers_info, print_msg=False):
    """Process the base results from the channels peer search."""
    if not base_chs_peers_info or len(base_chs_peers_info) < 0:
        return False

    n_channels = len(base_chs_peers_info)

    chs_n_streams = 0
    chs_total_size = 0
    chs_total_seconds = 0
    chs_streams_with_hosts = 0
    chs_streams_with_hosts_all = 0
    chs_total_peers = 0
    chs_total_peers_all = 0
    u_nodes_id = []
    chs_unique_nodes = []
    u_trackers_addr = []
    chs_unique_trackers = []

    peer_ratio_sum = 0.0
    peer_ratio_all_sum = 0.0
    hosting_coverage_sum = 0.0
    hosting_coverage_all_sum = 0.0

    chs_local_node = False

    for peers_info in base_chs_peers_info:
        if not peers_info:
            continue

        n_streams = peers_info["n_streams"]
        total_size = peers_info["total_size"]
        total_seconds = peers_info["total_duration"]
        streams_with_hosts = peers_info["streams_with_hosts"]
        streams_with_hosts_all = peers_info["streams_with_hosts_all"]
        total_peers = peers_info["total_peers"]
        total_peers_all = peers_info["total_peers_all"]
        unique_nodes = peers_info["unique_nodes"]
        unique_trackers = peers_info["unique_trackers"]
        peer_ratio = peers_info["peer_ratio"]
        peer_ratio_all = peers_info["peer_ratio_all"]
        hosting = peers_info["hosting_coverage"]
        hosting_all = peers_info["hosting_coverage_all"]

        chs_n_streams += n_streams
        chs_total_size += total_size
        chs_total_seconds += total_seconds
        chs_streams_with_hosts += streams_with_hosts
        chs_streams_with_hosts_all += streams_with_hosts_all
        chs_total_peers += total_peers
        chs_total_peers_all += total_peers_all

        for peer in unique_nodes:
            node = peer["node_id"]

            if node not in u_nodes_id:
                u_nodes_id.append(node)
                chs_unique_nodes.append(peer)

        for peer in unique_trackers:
            address = peer["address"]

            if address not in u_trackers_addr:
                u_trackers_addr.append(address)
                chs_unique_trackers.append(peer)

        peer_ratio_sum += peer_ratio
        peer_ratio_all_sum += peer_ratio_all
        hosting_coverage_sum += hosting
        hosting_coverage_all_sum += hosting_all
        chs_local_node = chs_local_node or peers_info["local_node"]

    chs_peer_ratio = peer_ratio_sum/n_channels
    chs_peer_ratio_all = peer_ratio_all_sum/n_channels
    chs_hosting_coverage = hosting_coverage_sum/n_channels
    chs_hosting_coverage_all = hosting_coverage_all_sum/n_channels

    return {"base_chs_peers_info": base_chs_peers_info,
            "n_channels": n_channels,
            "chs_n_streams": chs_n_streams,
            "chs_total_size": chs_total_size,
            "chs_total_duration": chs_total_seconds,
            "chs_streams_with_hosts": chs_streams_with_hosts,
            "chs_streams_with_hosts_all": chs_streams_with_hosts_all,
            "chs_total_peers": chs_total_peers,
            "chs_total_peers_all": chs_total_peers_all,
            "chs_unique_nodes": chs_unique_nodes,
            "chs_unique_trackers": chs_unique_trackers,
            "chs_peer_ratio": chs_peer_ratio,
            "chs_peer_ratio_all": chs_peer_ratio_all,
            "chs_hosting_coverage": chs_hosting_coverage,
            "chs_hosting_coverage_all": chs_hosting_coverage_all,
            "chs_local_node": chs_local_node}


def ch_search_ch_peers(channels=None,
                       number=None, shuffle=True,
                       ch_threads=8, claim_threads=32,
                       server="http://localhost:5279"):
    """Return the summary from the peer search for multiple channels.

    Parameters
    ----------
    channels: list of list
        Each element in the list is a list of two elements.
        The first element is a channel's name, full or partial;
        the second element is an integer that indicates the number
        of newest items from that channel that will be searched for peers.
        ::
            channels = [
                         ['@MyChannel#5', 3],
                         ['GoodChannel#f', 4],
                         ['Fast_channel', 2]
                       ]
    number: int, optional
        It defaults to `None`.
        If this is present, it will override the individual
        numbers in `channels`.
        That is, the number of claims that will be searched
        will be the same for every channel.
    shuffle: bool, optional
        It defaults to `True`, in which case it will shuffle
        the list of channels so that they are not processed in the order
        that they come in the list.
    ch_threads: int, optional
        It defaults to 8.
        It is the number of threads that will be used to process channels,
        meaning that many channels will be searched in parallel.
    claim_threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to search for peers,
        meaning that many claims will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
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
        - 'base_chs_peers_info': list of dict; each element of the list
          is the output of `peers.search_ch_peers` corresponding
          to each channel
        - 'n_channels': total number of channels
        - 'chs_n_streams': number of all streams in all channels searched
        - 'chs_total_size': total size of all streams searched in all channels
        - 'chs_total_duration': total duration of all streams searched
          in all channels
        - 'chs_streams_with_hosts': total number of streams
          with at least one user host in all channels
        - 'chs_streams_with_hosts_all': total number of streams
          with at least one host in all channels
        - 'chs_total_peers': total number of user peers
          in all searched streams in all channels
        - 'chs_total_peers_all': total number of peers
          in all searched streams in all channels
        - 'chs_unique_nodes': list of unique user peers
          in all searched streams in all channels
        - 'chs_unique_trackers': list of unique tracker peers
          in all searched streams in all channels
        - 'chs_peer_ratio': average number of user peers per stream
          per channel
        - 'chs_peer_ratio_all': average number of total peers per stream
          per channel
        - 'chs_hosting_coverage': average user hosting coverage per channel
        - 'chs_hosting_coverage_all': average hosting coverage per channel
        - 'chs_local_node': boolean value that indicates if we are hosting
          at least one stream
    """
    if not funcs.server_exists(server=server):
        return False

    s_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())

    processed_chs = funcs.process_ch_num(channels=channels,
                                         number=number, shuffle=shuffle)

    if not processed_chs or len(processed_chs) < 1:
        return False

    base_chs_peers_info = []

    # Iterables to be passed to the ThreadPoolExecutor
    n_channels = len(processed_chs)
    chns = (processed["channel"] for processed in processed_chs)
    numbers = (processed["number"] for processed in processed_chs)
    c_threads = (claim_threads for n in range(n_channels))
    falses = (False for n in range(n_channels))
    falses2 = (False for n in range(n_channels))
    servers = (server for n in range(n_channels))

    if ch_threads:
        with fts.ThreadPoolExecutor(max_workers=ch_threads) as executor:
            # The input must be iterables
            results = executor.map(prs.search_ch_peers,
                                   chns, numbers, c_threads,
                                   falses, falses2, servers)
            print(f"Channel-peer search; max threads: {ch_threads}")
            base_chs_peers_info = list(results)  # generator to list
    else:
        for num, processed in enumerate(processed_chs, start=1):
            channel = processed["channel"]
            number = processed["number"]

            print(f"Channel {num}/{n_channels}, {channel}")
            peers_info = prs.search_ch_peers(channel=channel,
                                             number=number,
                                             threads=claim_threads,
                                             print_time=False,
                                             print_msg=False,
                                             server=server)
            print()
            base_chs_peers_info.append(peers_info)

    chs_peers_info = process_chs_peers(base_chs_peers_info)

    e_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
    print(f"start: {s_time}")
    print(f"end:   {e_time}")

    return chs_peers_info


def print_ch_p_lines(chs_peers_info,
                     file=None, fdate=False, sep=";"):
    """Print a summary for each channel in a peer search."""
    if not chs_peers_info or len(chs_peers_info) < 0:
        return False

    base_ch_peers_info = chs_peers_info["base_chs_peers_info"]
    n_channels = chs_peers_info["n_channels"]

    out = []

    for num, peers_info in enumerate(base_ch_peers_info, start=1):
        if not peers_info:
            line = f"{num:4d}/{n_channels:4d}" + f"{sep} "
            line += '"None"'
            out.append(line)
            continue

        channel = peers_info["channel"]
        channel = f'"{channel}"'
        n_streams = peers_info["n_streams"]
        total_size = peers_info["total_size"]
        total_seconds = peers_info["total_duration"]
        streams_with_hosts = peers_info["streams_with_hosts"]
        unique_nodes = peers_info["unique_nodes"]
        n_nodes = len(unique_nodes)

        if peers_info["local_node"]:
            n_nodes = f"{n_nodes:3d} + 1"
        else:
            n_nodes = f"{n_nodes:3d}"

        total_size_gb = total_size / (1024**3)
        hr = total_seconds // 3600
        mi = (total_seconds % 3600) // 60
        sec = (total_seconds % 3600) % 60
        duration = f"{hr:3d} h {mi:2d} min {sec:2d} s"

        peer_ratio = peers_info["peer_ratio"]
        hosting_coverage = peers_info["hosting_coverage"] * 100

        line = f"{num:4d}/{n_channels:4d}" + f"{sep} "
        line += f"{channel:42s}" + f"{sep} "
        line += f"streams: {streams_with_hosts:3d}/{n_streams:3d}" + f"{sep} "
        line += f"{total_size_gb:9.4f} GB" + f"{sep} "
        line += f"{duration}" + f"{sep} "
        line += f"peers/stream: {peer_ratio:7.4f}" + f"{sep} "
        line += f"coverage: {hosting_coverage:6.2f}%" + f"{sep} "
        line += f"unique peers: {n_nodes}"
        out.append(line)

    funcs.print_content(out, file=file, fdate=fdate)


def print_ch_p_summary(chs_peers_info,
                       file=None, fdate=False):
    """Print a summary of the results for all peers searched in channels."""
    if not chs_peers_info or len(chs_peers_info) < 0:
        return False

    base_ch_peers_info = chs_peers_info["base_chs_peers_info"]
    n_channels = chs_peers_info["n_channels"]

    n_streams_t = 0
    total_size_t = 0
    total_seconds_t = 0
    streams_with_hosts_t = 0
    total_peers_t = 0
    unique_peers_t = []
    peer_ratio_sum = 0
    hosting_coverage_sum = 0
    local_node_t = False

    for peers_info in base_ch_peers_info:
        if not peers_info:
            continue

        channel = peers_info["channel"]
        channel = f'"{channel}"'
        n_streams = peers_info["n_streams"]
        total_size = peers_info["total_size"]
        total_seconds = peers_info["total_duration"]
        streams_with_hosts = peers_info["streams_with_hosts"]
        total_peers = peers_info["total_peers"]
        unique_nodes = peers_info["unique_nodes"]
        peer_ratio = peers_info["peer_ratio"]
        hosting = peers_info["hosting_coverage"]

        n_streams_t += n_streams
        total_size_t += total_size
        total_seconds_t += total_seconds
        streams_with_hosts_t += streams_with_hosts
        total_peers_t += total_peers

        for p in unique_nodes:
            if p not in unique_peers_t:
                unique_peers_t.append(p)

        peer_ratio_sum += peer_ratio
        hosting_coverage_sum += hosting
        local_node_t = local_node_t or peers_info["local_node"]

    total_size_gb_t = total_size_t / (1024**3)
    hr_t = total_seconds_t // 3600
    mi_t = (total_seconds_t % 3600) // 60
    sec_t = (total_seconds_t % 3600) % 60
    duration_t = f"{hr_t} h {mi_t} min {sec_t} s"

    n_nodes_t = len(unique_peers_t)

    if local_node_t:
        n_nodes_t = f"{n_nodes_t} + 1"

    peer_ratio_t = peer_ratio_sum/n_channels
    hosting_coverage_t = hosting_coverage_sum/n_channels * 100

    out = [f"Channels: {n_channels}",
           f"Total streams: {n_streams_t}",
           "- Total streams that have at least one host: "
           f"{streams_with_hosts_t}",
           f"- Total size of streams: {total_size_gb_t:.4f} GiB",
           f"- Total duration of streams: {duration_t}",
           "",
           f"Total peers in all searched claims: {total_peers_t}",
           f"Total unique peers (nodes) hosting streams: {n_nodes_t}",
           "Total average number of peers per stream: "
           f"{peer_ratio_t:.4f}",
           f"Total hosting coverage: {hosting_coverage_t:.2f}%"]

    funcs.print_content(out, file=file, fdate=fdate)


def print_ch_peers_info(chs_peers_info,
                        file=None, fdate=False, sep=";"):
    """Print the summary for the peer search of various channels."""
    print_ch_p_lines(chs_peers_info,
                     file=file, fdate=fdate, sep=sep)

    print_ch_p_summary(chs_peers_info, file=None, fdate=fdate)


def list_chs_peers(channels=None,
                   number=None, shuffle=True,
                   ch_threads=8, claim_threads=32,
                   file=None, fdate=False, sep=";",
                   server="http://localhost:5279"):
    """Print the summary from the peer search for multiple channels.

    Parameters
    ----------
    channels: list of list
        Each element in the list is a list of two elements.
        The first element is a channel's name, full or partial;
        the second element is an integer that indicates the number
        of newest items from that channel that will be searched for peers.
        ::
            channels = [
                         ['@MyChannel#5', 3],
                         ['GoodChannel#f', 4],
                         ['Fast_channel', 2]
                       ]
    number: int, optional
        It defaults to `None`.
        If this is present, it will override the individual
        numbers in `channels`.
        That is, the number of claims that will be searched
        will be the same for every channel.
    shuffle: bool, optional
        It defaults to `True`, in which case it will shuffle
        the list of channels so that they are not processed in the order
        that they come in the list.
    ch_threads: int, optional
        It defaults to 8.
        It is the number of threads that will be used to process channels,
        meaning that many channels will be searched in parallel.
    claim_threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to search for peers,
        meaning that many claims will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
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
        - 'base_chs_peers_info': list of dict; each element of the list
          is the output of `peers.search_ch_peers` corresponding
          to each channel
        - 'n_channels': total number of channels
        - 'chs_n_streams': number of all streams in all channels searched
        - 'chs_total_size': total size of all streams searched in all channels
        - 'chs_total_duration': total duration of all streams searched
          in all channels
        - 'chs_streams_with_hosts': total number of streams
          with at least one user host in all channels
        - 'chs_streams_with_hosts_all': total number of streams
          with at least one host in all channels
        - 'chs_total_peers': total number of user peers
          in all searched streams in all channels
        - 'chs_total_peers_all': total number of peers
          in all searched streams in all channels
        - 'chs_unique_nodes': list of unique user peers
          in all searched streams in all channels
        - 'chs_unique_trackers': list of unique tracker peers
          in all searched streams in all channels
        - 'chs_peer_ratio': average number of user peers per stream
          per channel
        - 'chs_peer_ratio_all': average number of total peers per stream
          per channel
        - 'chs_hosting_coverage': average user hosting coverage per channel
        - 'chs_hosting_coverage_all': average hosting coverage per channel
        - 'chs_local_node': boolean value that indicates if we are hosting
          at least one stream
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    chs_peers_info = ch_search_ch_peers(channels=channels,
                                        number=number, shuffle=shuffle,
                                        ch_threads=ch_threads,
                                        claim_threads=claim_threads,
                                        server=server)

    print_ch_peers_info(chs_peers_info,
                        file=file, fdate=fdate, sep=sep)

    return chs_peers_info


def list_ch_subs_peers(number=2, shuffle=False,
                       start=1, end=0,
                       shared=True, valid=True,
                       ch_threads=32, claim_threads=16,
                       file=None, fdate=False, sep=";",
                       server="http://localhost:5279"):
    """Print the summary of peers for claims for subscribed channels.

    The list of channels to which we are subscribed is found
    in the wallet file in the local machine, assuming it is synchronized
    with Odysee.

    Parameters
    ----------
    number: int, optional
        It defaults to 2.
        The maximum number of claims that will be searched for peers
        for every subscribed channel.
    shuffle: bool, optional
        It defaults to `False`, in which case it will process
        the channels in the order that they are found in the wallet file.
        If it is `True`, the list of channels is shuffled
        so that they are processed in random order.
    start: int, optional
        It defaults to 1.
        Process channels starting from this index in the list of channels.
    end: int, optional
        It defaults to 0.
        Process channels until and including this index in the list
        of channels.
        If it is 0, it is the same as the last index in the list.
    shared: bool, optional
        It defaults to `True`, in which case it uses the shared database
        synchronized with Odysee online.
        If it is `False` it will use only the local database
        to `lbrynet`, for example, used by the LBRY Desktop application.
    valid: bool, optional
        It defaults to `True`, in which case it will only list the valid
        channels which can be resolved online.
        If it is `False` it will list all channels in the wallet, even those
        that do not resolve online, meaning that probably they were deleted.
        These invalid channels will be shown with brackets around
        the channel's name, for example, `[@channel]`.
    ch_threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to process channels,
        meaning that many channels will be searched in parallel.
    claim_threads: int, optional
        It defaults to 16.
        It is the number of threads that will be used to search for peers,
        meaning that many claims will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
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
        - 'base_chs_peers_info': list of dict; each element of the list
          is the output of `peers.search_ch_peers` corresponding
          to each channel
        - 'n_channels': total number of channels
        - 'chs_n_streams': number of all streams in all channels searched
        - 'chs_total_size': total size of all streams searched in all channels
        - 'chs_total_duration': total duration of all streams searched
          in all channels
        - 'chs_streams_with_hosts': total number of streams
          with at least one user host in all channels
        - 'chs_streams_with_hosts_all': total number of streams
          with at least one host in all channels
        - 'chs_total_peers': total number of user peers
          in all searched streams in all channels
        - 'chs_total_peers_all': total number of peers
          in all searched streams in all channels
        - 'chs_unique_nodes': list of unique user peers
          in all searched streams in all channels
        - 'chs_unique_trackers': list of unique tracker peers
          in all searched streams in all channels
        - 'chs_peer_ratio': average number of user peers per stream
          per channel
        - 'chs_peer_ratio_all': average number of total peers per stream
          per channel
        - 'chs_hosting_coverage': average user hosting coverage per channel
        - 'chs_hosting_coverage_all': average hosting coverage per channel
        - 'chs_local_node': boolean value that indicates if we are hosting
          at least one stream
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    sub_channels = chs.list_ch_subs(shared=shared,
                                    show_all=not valid,
                                    filtering="valid", valid=True,
                                    threads=32,
                                    claim_id=False,
                                    file=None, fdate=False, sep=sep,
                                    server=server)

    channels = []

    for num, channel in enumerate(sub_channels, start=1):
        if num < start:
            continue
        if end != 0 and num > end:
            break

        name, cid = channel["uri"].lstrip("lbry://").split("#")
        c_name = name + "#" + cid[0:3]

        if not channel["valid"]:
            c_name = "[" + c_name + "]"

        channels.append([c_name, number])

    chs_peers_info = list_chs_peers(channels=channels,
                                    number=None, shuffle=shuffle,
                                    ch_threads=ch_threads,
                                    claim_threads=claim_threads,
                                    file=file, fdate=fdate, sep=sep,
                                    server=server)

    return chs_peers_info


if __name__ == "__main__":
    list_chs_peers(["@Luke"])
    list_chs_peers(["@Luke", "@rossmanngroup"])
    list_chs_peers([["@Luke", 3], "@rossmanngroup"])
    list_chs_peers([["@Luke", 3], ["@rossmanngroup", 5]])
    list_chs_peers(["@Luke", "@rossmanngroup"], number=3)
    list_chs_peers([["@Luke", 3], ["@rossmanngroup", 5]], number=4)
