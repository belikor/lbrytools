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
"""Functions to display information on our own claims."""
import requests

import lbrytools.funcs as funcs
import lbrytools.print_claims as prntc


def claims_bids(show_controlling=False, show_non_controlling=True,
                skip_repost=False, channels_only=False,
                show_claim_id=False,
                show_repost_status=True,
                show_competing=True, show_reposts=True,
                compact=False,
                file=None, fdate=False, sep=";",
                server="http://localhost:5279"):
    """Display the claims that are competing in name and LBC bidding.

    This is based on an original script by `@BrendonBrewer:3/vanity:8`

    Parameters
    ----------
    show_controlling: bool, optional
        It defaults to `False`, in which case it will not show
        the 'controlling' claims, that is, those which have the highest bid.
        If it is `True` it will show controlling claims.
    show_non_controlling: bool, optional
        It defaults to `True`, in which case it will show
        the 'non-controlling' claims, that is, those which have a lower bid.
        If it is `False` it will not show non-controlling claims.
    skip_repost: bool, optional
        It defaults to `False`, in which case it will process all claims
        whether they are reposts or not.
        If it is `True` it will not process reposts.
    channels_only: bool, optional
        It defaults to `False`, in which case it will process all claims
        whether they are channels or not.
        If it is `True` it will only process the claims that are channels.
    show_claim_id: bool, optional
        It defaults to `False`.
        If it is `True`, the claim ID will be printed for all claims.
        This option only has an effect when `compact=True`.
    show_repost_status: bool, optional
        It defaults to `True`, in which case it will show whether the claims
        are reposts or not.
        This option only has an effect when `compact=True`.
    show_competing: bool, optional
        It defaults to `True`, in which case it will show the number
        of competing claims, that is, those that share the same name
        with the claim being inspected.
        This option only has an effect when `compact=True`.
    show_reposts: bool, optional
        It defaults to `True`, in which case it will show the number
        of reposts for the claim being inspected.
        This option only has an effect when `compact=True`.
    compact: bool, optional
        It defaults to `False`, in which case each claim's information
        will be printed in a paragraph.
        If it is `True` there will be one claim per row, so the summary
        will be more compact.
    file: str, optional
        It defaults to `None`.
        It must be a writable path to which the summary will be written.
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
    list of dict
        It returns the list of dictionaries representing the processed claims.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    msg = {"method": "claim_list",
           "params": {"page_size": 99000,
                      "resolve": True}}

    output = requests.post(server, json=msg).json()
    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    print("Analysis of the bidding amounts for claims, "
          "including channels, videos, reposts, playlists, etc.")

    num_claims = output["result"]["total_items"]
    print(f"Number of claims: {num_claims}")

    if (not show_controlling and not show_non_controlling):
        print(f"show_controlling: {bool(show_controlling)}")
        print(f"show_non_controlling: {bool(show_non_controlling)}")
        print("Won't show any item; at least one option must be True.")
        return False

    if show_controlling:
        print("- Controlling claims (highest bids) will be considered")
    if show_non_controlling:
        print("- Non-controlling claims (low bids) will be considered")

    if skip_repost:
        print("- Reposts will be omitted")
    else:
        print("- Reposts will be considered")

    if channels_only:
        print("- Only channels will be considered")

    print(80 * "-")

    claims = output["result"]["items"]

    out = []
    claims_filtered = []

    for it, claim in enumerate(claims, start=1):
        is_repost = claim["value_type"] == "repost"
        is_channel = claim["value_type"] == "channel"
        is_controlling = claim["meta"]["is_controlling"]

        if show_controlling and show_non_controlling:
            # Show regardless of controlling status
            if ((skip_repost and is_repost)
                    or (channels_only and not is_channel)):
                # Skip claim depending on whether it is a repost or a channel
                continue
            else:
                # Show everything
                pass
        elif (not show_controlling and not show_non_controlling):
            # Show nothing, regardless of controlling status
            continue
        elif ((show_controlling and not is_controlling)
                or (show_non_controlling and is_controlling)
                or (skip_repost and is_repost)
                or (channels_only and not is_channel)):
            # Skip claim depending on controlling status
            # or whether it is a repost or a channel
            continue

        claims_filtered.append(claim)

        uri = claim["canonical_url"]
        claim_id = claim["claim_id"]
        name = claim["name"]
        staked = float(claim["amount"])
        staked += float(claim["meta"]["support_amount"])

        # It's unlikely that more than 1000 items will share the same name
        msg2 = {"method": "claim_search",
                "params": {"name": name,
                           "page_size": 1000}}

        output2 = requests.post(server, json=msg2).json()
        if "error" in output2:
            print(">>> No 'result' in the JSON-RPC server output")
            return False

        max_lbc = 0
        competitors = 0
        comp_reposts = 0
        items = output2["result"]["items"]

        for item in items:
            item_lbc = float(item["amount"])
            item_lbc += float(item["meta"]["support_amount"])

            rep_claim_id = ("reposted_claim_id" in item
                            and item["reposted_claim_id"] == claim_id)

            if item["claim_id"] != claim_id or rep_claim_id:
                if max_lbc == 0 or item_lbc > max_lbc:
                    max_lbc = float(item_lbc)

                if item["value_type"] == "repost":
                    comp_reposts += 1
                else:
                    competitors += 1

        name = f'"{name}"'

        if compact:
            line = f"{it:3d}/{num_claims:3d}" + f"{sep} "
            if show_claim_id:
                line += f"{claim_id}" + f"{sep} "

            line += (f"{name:58s}" + f"{sep} " +
                     f"staked: {staked:8.2f}" + f"{sep} " +
                     f"highest_bid: {max_lbc:8.2f}" + f"{sep} " +
                     f"is_controlling: {str(is_controlling):5s}")

            if show_repost_status:
                line += f"{sep} " + f"is_repost: {str(is_repost):5s}"
            if show_competing:
                line += f"{sep} " + f"competing: {competitors:2d}"
            if show_reposts:
                line += f"{sep} " + f"reposts: {comp_reposts:2d}"

            out += [line]
        else:
            paragraph = (f"Claim {it}/{num_claims}, {name}\n"
                         f"canonical_url: {uri}\n"
                         f"claim_id: {claim_id}\n"
                         f"staked: {staked:.3f}\n"
                         f"highest_bid: {max_lbc:.3f} (by others)\n"
                         f"is_controlling: {is_controlling}\n"
                         f"is_repost: {is_repost}\n"
                         f"competing: {competitors}\n")
            if is_repost:
                paragraph += f"reposts: {comp_reposts} + 1 (this one)\n"
            else:
                paragraph += f"reposts: {comp_reposts}\n"

            out += [paragraph]

    funcs.print_content(out, file=file, fdate=fdate)

    return claims_filtered


def w_claim_search(page=1,
                   what="trending",
                   trending="trending_mixed",
                   order="release_time",
                   text=None,
                   tags=None,
                   claim_id=False,
                   claim_type=None,
                   video_stream=False, audio_stream=False,
                   doc_stream=False, img_stream=False,
                   bin_stream=False, model_stream=False,
                   sanitize=False,
                   file=None, fdate=False, sep=";",
                   server="http://localhost:5279"):
    """Print trending claims or searched claims in the the network."""
    print(80 * "-")
    if what in "trending":
        print("Show trending claims")
    elif what in "text":
        print("Show searched text and tags")

    print(f"Page: {page}")

    msg = {"method": "claim_search",
           "params": {"page": page,
                      "page_size": 100,
                      "no_totals": True}}

    if what in "trending":
        msg["params"]["order_by"] = trending
    elif what in "text":
        msg["params"]["order_by"] = order

    if what in "text":
        if not tags:
            tags = []
        if isinstance(tags, str):
            tags = [tags]
        if not isinstance(tags, list):
            tags = []

        if text:
            msg["params"]["text"] = f'"{text}"'
        if tags:
            msg["params"]["any_tags"] = tags

    # Claim type can only be one of:
    # 'stream', 'channel', 'repost', 'collection'
    if claim_type:
        # Livestreams are just type 'stream' but have no 'source'
        if claim_type == "livestream":
            msg["params"]["has_no_source"] = True
            claim_type = "stream"

        # The 'playlist' argument is treated the same as 'collection'
        if claim_type == "playlist":
            claim_type = "collection"

        msg["params"]["claim_type"] = claim_type

    stypes = []
    if video_stream:
        stypes.append("video")
    if audio_stream:
        stypes.append("audio")
    if doc_stream:
        stypes.append("document")
    if img_stream:
        stypes.append("image")
    if bin_stream:
        stypes.append("binary")
    if model_stream:
        stypes.append("model")
    if stypes:
        msg["params"]["stream_types"] = stypes

    if what in "trending":
        print(f"order_by: {trending}")
    elif what in "text":
        print(f'text: "{text}"')
        print(f"tags: " + ", ".join(tags))
        print(f"order_by: {order}")

    print(f"claim_type: {claim_type}")
    print(f"stream_types: {stypes}")

    output = requests.post(server, json=msg).json()
    if "error" in output:
        return False

    claims = output["result"]["items"]

    content = prntc.print_tr_claims(claims,
                                    claim_id=claim_id,
                                    sanitize=sanitize,
                                    file=file, fdate=fdate, sep=sep)

    return content


def print_trending_claims(page=1,
                          trending="trending_mixed",
                          claim_id=False,
                          claim_type=None,
                          video_stream=False, audio_stream=False,
                          doc_stream=False, img_stream=False,
                          bin_stream=False, model_stream=False,
                          sanitize=False,
                          file=None, fdate=False, sep=";",
                          server="http://localhost:5279"):
    """Print trending claims in the network.

    Parameters
    ----------
    page: int, optional
        It defaults to 1.
        Page of output to show. Each page has 50 elements.
        At the moment the maximum is 20.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim ID (40-character string).
    claim_type: str, optional
        One of the five types: 'stream', 'channel', 'repost', 'collection',
        or 'livestream'.
    video_stream: bool, optional
        Show 'video' streams.
    audio_stream: bool, optional
        Show 'audio' streams.
    doc_stream: bool, optional
        Show 'document' streams.
    img_stream: bool, optional
        Show 'image' streams.
    bin_stream: bool, optional
        Show 'binary' streams.
    model_stream: bool, optional
        Show 'model' streams.
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the name of the claim and channel.
        If it is `True` it will remove these unicode characters
        and replace them with a simple black square.
        This option requires the `emoji` package to be installed.
    file: str, optional
        It defaults to `None`.
        It must be a writable path to which the summary will be written.
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
    str
        Returns the string to display, that was printed to the terminal
        or to the file.
    False
        If there is a problem it will return `False`.
    """
    content = w_claim_search(page=page,
                             what="trending",
                             trending=trending,
                             claim_id=claim_id,
                             claim_type=claim_type,
                             video_stream=video_stream,
                             audio_stream=audio_stream,
                             doc_stream=doc_stream,
                             img_stream=img_stream,
                             bin_stream=bin_stream,
                             model_stream=model_stream,
                             sanitize=sanitize,
                             file=file, fdate=fdate, sep=sep,
                             server=server)

    return content


def print_search_claims(page=1,
                        order="release_time",
                        text="lbry",
                        tags=None,
                        claim_id=False,
                        claim_type=None,
                        video_stream=False, audio_stream=False,
                        doc_stream=False, img_stream=False,
                        bin_stream=False, model_stream=False,
                        sanitize=False,
                        file=None, fdate=False, sep=";",
                        server="http://localhost:5279"):
    """Print the result of the claim search for an arbitrary text.

    Parameters
    ----------
    page: int, optional
        It defaults to 1.
        Page of output to show. Each page has 50 elements.
        At the moment the maximum is 20.
    text: str, optional
        It defaults to 'lbry'.
        Full string to search in the network; it will search in the claim name,
        channel name, title, description, author, and tags.
        The search isn't very good, however. Adding many words together
        will return few results or none.
    tags: list of str, optional
        Each string in the list will be considered a tag that is searched.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim ID (40-character string).
    claim_type: str, optional
        One of the five types: 'stream', 'channel', 'repost', 'collection',
        or 'livestream'.
    video_stream: bool, optional
        Show 'video' streams.
    audio_stream: bool, optional
        Show 'audio' streams.
    doc_stream: bool, optional
        Show 'document' streams.
    img_stream: bool, optional
        Show 'image' streams.
    bin_stream: bool, optional
        Show 'binary' streams.
    model_stream: bool, optional
        Show 'model' streams.
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the name of the claim and channel.
        If it is `True` it will remove these unicode characters
        and replace them with a simple black square.
        This option requires the `emoji` package to be installed.
    file: str, optional
        It defaults to `None`.
        It must be a writable path to which the summary will be written.
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
    str
        Returns the string to display, that was printed to the terminal
        or to the file.
    False
        If there is a problem it will return `False`.
    """
    content = w_claim_search(page=page,
                             what="text",
                             order=order,
                             text=text,
                             tags=tags,
                             claim_id=claim_id,
                             claim_type=claim_type,
                             video_stream=video_stream,
                             audio_stream=audio_stream,
                             doc_stream=doc_stream,
                             img_stream=img_stream,
                             bin_stream=bin_stream,
                             model_stream=model_stream,
                             sanitize=sanitize,
                             file=file, fdate=fdate, sep=sep,
                             server=server)

    return content


if __name__ == "__main__":
    claims_bids(show_non_controlling=True, skip_repost=False, channels_only=False)
    # claims_bids(show_non_controlling=True, skip_repost=True, channels_only=False)
