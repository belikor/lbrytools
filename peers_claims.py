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
