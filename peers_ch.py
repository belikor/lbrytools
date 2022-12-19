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
import time

import lbrytools.funcs as funcs
import lbrytools.search_ch as srch_ch
import lbrytools.peers_base as prs


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

        peers_info = prs.process_claims_peers(base_peers_info,
                                              channel=True,
                                              print_msg=print_msg)
        return peers_info

    print()
    print("Count the number of peers")
    print(80 * "-")

    peers_info = prs.search_m_claim_peers(claims=claims,
                                          resolve=False,
                                          threads=threads,
                                          print_msg=print_msg,
                                          server=server)

    ch = peers_info["streams_info"][0]["stream"]
    ch = ch["signing_channel"]["canonical_url"].split("lbry://")[1]

    peers_info["channel"] = ch

    if print_time:
        e_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
        print(f"start: {s_time}")
        print(f"end:   {e_time}")

    return peers_info


def list_ch_peers(channel=None, number=2, threads=32, inline=True,
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
    inline: bool, optional
        It defaults to `True`, in which case it will print the information
        of each claim in its own line.
        If it is `False` it will print a paragraph of information
        for each claim.
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

    summary = prs.get_summary(peers_info, channel=True)

    print()
    prs.print_claims_lines(peers_info,
                           inline=inline,
                           cid=claim_id, typ=typ, title=title,
                           sanitize=sanitize,
                           file=file, fdate=fdate, sep=sep)

    print(80 * "-")

    funcs.print_content([summary], file=None, fdate=False)

    peers_info["summary"] = summary

    return peers_info


if __name__ == "__main__":
    list_ch_peers(channel="@Luke", number=53, threads=64)
    print()
    list_ch_peers(channel="@rossmanngroup", number=50, threads=64)
    print()
    list_ch_peers(channel="@AlphaNerd", number=50, threads=64)
