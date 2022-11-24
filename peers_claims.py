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
"""Functions to get the peer list of a single claim."""
import lbrytools.funcs as funcs
import lbrytools.search as srch
import lbrytools.peers_base as prs


def search_claim_peers(uri=None, cid=None, name=None,
                       server="http://localhost:5279"):
    """Search the peers for a single claim; only streams have peers.

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
        - 'stream': the resolved information of the claim, or `None`
          if this is not a downloadable stream, like a channel
        - 'size': size in bytes of the claim; could be zero
        - 'duration': duration in seconds of the claim; could be zero
        - 'peers': list of peers for the claim; each peer is a dict
          with keys 'address'  (IP), 'node_id', 'tcp_port', and 'udp_port'
        - 'peers_user': list of peers corresponding to user nodes
          running their own `lbrynet` daemons. For these the 'node_id'
        - 'peers_tracker': list of peers corresponding to fixed trackers,
          for which the 'node_id' is `None`.
        - 'local_node': boolean indicating if the claim is hosted
          in our `lbrynet` client or not
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    claim = srch.search_item(uri=uri, cid=cid, name=name,
                             offline=False, repost=True,
                             print_error=True,
                             server=server)

    stream_info = prs.calculate_peers(claim=claim, print_msg=False,
                                      server=server)

    return stream_info


def list_peers(uri=None, cid=None, name=None,
               inline=False,
               claim_id=False, typ=True, title=False,
               sanitize=False,
               file=None, fdate=False, sep=";",
               server="http://localhost:5279"):
    """Print the peers for the given claim.

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
    inline: bool, optional
        It defaults to `False`, in which case the output of the search
        will be a paragraph of information on the peer search.
        If `inline` is `True`, it will print the information
        only in a single line.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim ID for the claim.
        This only works if `inline=True`.
    typ: bool, optional
        It defaults to `True`, in which case the claim type and stream type
        will be printed for the claim.
        This only works if `inline=True`.
    title: bool, optional
        It defaults to `False`, in which case the claim name will be printed.
        If it is `True` it will print the claim title instead.
        This only works if `inline=True`.
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
        This only works if `inline=True`.
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
        - 'stream': the resolved information of the claim, or `None`
          if this is not a downloadable stream, like a channel
        - 'size': size in bytes of the claim; could be zero
        - 'duration': duration in seconds of the claim; could be zero
        - 'peers': list of peers for the claim; each peer is a dict
          with keys 'address'  (IP), 'node_id', 'tcp_port', and 'udp_port'
        - 'peers_user': list of peers corresponding to user nodes
          running their own `lbrynet` daemons. For these the 'node_id'
        - 'peers_tracker': list of peers corresponding to fixed trackers,
          for which the 'node_id' is `None`.
        - 'local_node': boolean indicating if the claim is hosted
          in our `lbrynet` client or not
        - 'summary': a paragraph of text with the summary of the peer search
          for this claim. It can be printed to the terminal or displayed
          in other types of graphical interface.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    stream_info = search_claim_peers(uri=uri, cid=cid, name=name,
                                     server=server)

    if not stream_info["stream"]:
        return False

    summary = prs.get_claim_summary(stream_info,
                                    cid=claim_id, typ=typ, title=title,
                                    inline=inline, sanitize=sanitize,
                                    sep=sep)

    funcs.print_content([summary], file=file, fdate=fdate)

    stream_info["summary"] = summary

    return stream_info


def list_m_peers(claims=None, threads=32, inline=True,
                 print_msg=False,
                 claim_id=False, typ=True, title=False,
                 sanitize=False,
                 file=None, fdate=False, sep=";",
                 server="http://localhost:5279"):
    """Print the peers for the given list of claims.

    Parameters
    ----------
    claims: list of str
        Each element of the list is a claim name or claim ID
        that we wish to examine for peers.
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
        - 'summary': a paragraph of text with the summary of the peer search
          for the input list. It can be printed to the terminal or displayed
          in other types of graphical interface.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if not claims:
        print("Input must be a list of URIs or claim IDs.")
        return False

    peers_info = prs.search_m_claim_peers(claims=claims, resolve=True,
                                          threads=threads,
                                          print_msg=print_msg,
                                          server=server)

    summary = prs.get_summary(peers_info, channel=False)

    if peers_info["n_streams"] > 0:
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
    list_peers("vim-alchemy-with-macros#b", inline=False)
    print()
    list_peers("ai-generated-artwork-takes-first-place:1", inline=True)
    print()
    list_peers("@pi:2")
    print()
    list_peers("@pi:2", inline=True)
    print()
    list_peers("dsnt-exist")
    print()
    list_m_peers(["did-elon-musk-just-save-free-speech",
                  "dsnt-exist"])
    print()
    list_m_peers(["vim-alchemy-with-macros#b",
                  "ai-generated-artwork-takes-first-place:1",
                  "thanksgivingroundup:7",
                  "did-elon-musk-just-save-free-speech:1",
                  "83a23b2e2f20bf9af0d46ad38132e745c35d9ff4",
                  "uncharted-expleened:b",
                  "@pi:2",
                  "dsnt-existt"])
