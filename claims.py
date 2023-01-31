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
import concurrent.futures as fts

import requests

import lbrytools.funcs as funcs
import lbrytools.search_utils as sutils
import lbrytools.print_claims as prntc


def params_claim_search(msg=None,
                        what="trending",
                        trending="trending_mixed",
                        order="release_time",
                        text=None,
                        tags=None,
                        claim_type=None,
                        video_stream=False, audio_stream=False,
                        doc_stream=False, img_stream=False,
                        bin_stream=False, model_stream=False):
    """Get the options needed for the claim search command."""
    if not msg:
        msg = {"method": "claim_search",
               "params": {}}

    if what in ("trending"):
        msg["params"]["order_by"] = trending
    elif what in ("text"):
        msg["params"]["order_by"] = order

    if what in ("text"):
        if not tags:
            tags = []
        if isinstance(tags, str):
            tags = [tags]
        if not isinstance(tags, list):
            tags = []

        if text:
            msg["params"]["text"] = f"{text}"
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

    return msg


def claim_search_pg(msg, page, server):
    """Call the search claim method with the appropriate page in a thread."""
    msg["params"].update({"page": page})
    output = requests.post(server, json=msg).json()
    items = output["result"]["items"]

    return items


def w_claim_search(what="trending",
                   threads=32,
                   page=None,
                   trending="trending_mixed",
                   order="release_time",
                   text=None,
                   tags=None,
                   claim_type=None,
                   video_stream=False, audio_stream=False,
                   doc_stream=False, img_stream=False,
                   bin_stream=False, model_stream=False,
                   server="http://localhost:5279"):
    """Wrapper to search claims in the network using threads."""
    msg = {"method": "claim_search",
           "params": {"page_size": 100,
                      "no_totals": True}}

    msg = params_claim_search(msg=msg,
                              what=what,
                              trending=trending,
                              order=order,
                              text=text,
                              tags=tags,
                              claim_type=claim_type,
                              video_stream=video_stream,
                              audio_stream=audio_stream,
                              doc_stream=doc_stream,
                              img_stream=img_stream,
                              bin_stream=bin_stream,
                              model_stream=model_stream)

    stypes = msg["params"].get("stream_types", [])
    tags = msg["params"].get("any_tags", [])

    searched = []

    if what in ("trending"):
        searched = ["Trending claims",
                    f"order_by: {trending}"]
    elif what in ("text"):
        searched = ["Searched text and tags",
                    f"text: '{text}'",
                    f"tags: " + ", ".join(tags),
                    f"order_by: {order}"]

    searched.extend([f"claim_type: {claim_type}",
                     f"stream_types: {stypes}"])

    # Page size is maximum 50 even if a higher value is set.
    # The maximum number of claims in 20 x 50 = 1000.
    if page:
        threads = 0

        if page < 0:
            page = abs(page)
        elif page > 20:
            page = 20

        pages = [page]
        searched.append(f"page: {page}")
    else:
        searched.append("page: all")
        pages = range(1, 21)
        msg_s = (msg for n in pages)
        servers = (server for n in pages)

    print()

    claims = []

    if threads:
        with fts.ThreadPoolExecutor(max_workers=threads) as executor:
            results = executor.map(claim_search_pg,
                                   msg_s, pages,
                                   servers)

            print("Waiting for claim search to finish; "
                  f"max threads: {threads}")

            for result in results:
                claims.extend(result)
    else:
        for page in pages:
            print("Waiting for claim search to finish")

            items = claim_search_pg(msg, page, server)
            claims.extend(items)

    claims_info = sutils.downloadable_size(claims, print_msg=False)
    claims_info["claims"] = claims
    claims_info["searched"] = "\n".join(searched)

    return claims_info


def list_trending_claims(threads=32,
                         page=None,
                         trending="trending_mixed",
                         claim_type=None,
                         video_stream=False, audio_stream=False,
                         doc_stream=False, img_stream=False,
                         bin_stream=False, model_stream=False,
                         create=False, height=False, release=True,
                         claim_id=False, typ=True, ch_name=True,
                         sizes=True, fees=True,
                         title=False, sanitize=False,
                         file=None, fdate=False, sep=";",
                         server="http://localhost:5279"):
    """Print trending claims in the network.

    Parameters
    ----------
    threads: int, optional
        It defaults to 32.
        It is the maximum number of threads that will be used to search
        for pages of claims.
        A maximum of twenty pages of claims will be searched,
        so at least 20 threads is suggested.
        This number shouldn't be large if the CPU doesn't have many cores.
    page: int, optional
        It defaults to `None`, in which case all 20 pages will be searched.
        If it is an integer between 1 and 20, only that page will be searched.
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
    create: bool, optional
        It defaults to `False`.
        If it is `True` it will print the creation height and creation time
        of each claim.
    height: bool, optional
        It defaults to `False`.
        If it is `True` it will print the block height and timestamp
        of each claim.
    release: bool, optional
        It defaults to `True`, in which case it will print the release time
        of the claim, if it exists (for stream claims),
        or just the creation time.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim ID (40-character string).
    typ: bool, optional
        It defaults to `True`, in which case it will print the value type
        of the claim, and if applicable (for stream claims)
        the stream type and the media type.
    ch_name: bool, optional
        It defaults to `True`, in which case it will print the channel name
        that published the claim.
    sizes: bool, optional
        It defaults to `True`, in which case it will print the duration
        in minutes and seconds, and size in MB of each claim, if applicable
        (streams of type `'audio'` and `'video'`).
    fees: bool, optional
        It defaults to `True`, in which case it will print the fee (quantity
        and currency) associated with accessing each claim, if applicable.
    title: bool, optional
        It defaults to `False`, in which case the claim `'name'`
        will be printed.
        If it is `True` it will print the claim `'title'` instead.
        To download a stream, the claim name or the claim ID must be used.
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
    dict
        A dictionary with ten keys:
        - 'claims': a list of dictionaries where every dictionary represents
           a claim returned by `claim_search`.
        - 'searched': a paragraph of text that with the information
          that was searched, such as claim type, stream types, and page.
        - 'size': total size of the claims in bytes.
          It can be divided by 1024 to obtain kibibytes, by another 1024
          to obtain mebibytes, and by another 1024 to obtain gibibytes.
        - 'duration': total duration of the claims in seconds.
          It will count only stream types which have a duration
          such as audio and video.
        - 'size_GB': total size in GiB (floating point value)
        - 'd_h': integer hours HH when the duration is shown as HH:MM:SS
        - 'd_min': integer minutes MM when the duration is shown as HH:MM:SS
        - 'd_s`: integer seconds SS when the duration is shown as HH:MM:SS
        - 'days': total seconds converted into days (floating point value)
        - 'summary': paragraph of text describing the number of claims,
           the total size in GiB, and the total duration expressed as HH:MM:SS,
           and days
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    print("Show trending claims")
    claims_info = w_claim_search(threads=threads,
                                 page=page,
                                 what="trending",
                                 trending=trending,
                                 claim_type=claim_type,
                                 video_stream=video_stream,
                                 audio_stream=audio_stream,
                                 doc_stream=doc_stream,
                                 img_stream=img_stream,
                                 bin_stream=bin_stream,
                                 model_stream=model_stream,
                                 server=server)

    if claims_info["claims"]:
        prntc.print_sch_claims(claims_info["claims"],
                               create=create, height=height, release=release,
                               claim_id=claim_id, typ=typ, ch_name=ch_name,
                               long_chan=True,
                               sizes=sizes, fees=fees,
                               title=title, sanitize=sanitize,
                               start=1, end=0,
                               reverse=False,
                               file=file, fdate=fdate, sep=sep)

    print(80 * "-")
    print(claims_info["searched"])
    print(40 * "-")
    print(claims_info["summary"])

    return claims_info


def list_search_claims(threads=32,
                       page=None,
                       order="release_time",
                       text="lbry",
                       tags=None,
                       claim_type=None,
                       video_stream=False, audio_stream=False,
                       doc_stream=False, img_stream=False,
                       bin_stream=False, model_stream=False,
                       create=False, height=False, release=True,
                       claim_id=False, typ=True, ch_name=True,
                       sizes=True, fees=True,
                       title=False, sanitize=False,
                       file=None, fdate=False, sep=";",
                       server="http://localhost:5279"):
    """Print the result of the claim search for an arbitrary text.

    Parameters
    ----------
    threads: int, optional
        It defaults to 32.
        It is the maximum number of threads that will be used to search
        for pages of claims.
        A maximum of twenty pages of claims will be searched,
        so at least 20 threads is suggested.
        This number shouldn't be large if the CPU doesn't have many cores.
    page: int, optional
        It defaults to `None`, in which case all 20 pages will be searched.
        If it is an integer between 1 and 20, only that page will be searched.
    text: str, optional
        It defaults to 'lbry'.
        Full string to search in the network; it will search in the claim name,
        channel name, title, description, author, and tags.
        The search isn't very good, however. Adding many words together
        will return few results or none.
    tags: list of str, optional
        Each string in the list will be considered a tag that is searched.
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
    create: bool, optional
        It defaults to `False`.
        If it is `True` it will print the creation height and creation time
        of each claim.
    height: bool, optional
        It defaults to `False`.
        If it is `True` it will print the block height and timestamp
        of each claim.
    release: bool, optional
        It defaults to `True`, in which case it will print the release time
        of the claim, if it exists (for stream claims),
        or just the creation time.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim ID (40-character string).
    typ: bool, optional
        It defaults to `True`, in which case it will print the value type
        of the claim, and if applicable (for stream claims)
        the stream type and the media type.
    ch_name: bool, optional
        It defaults to `True`, in which case it will print the channel name
        that published the claim.
    sizes: bool, optional
        It defaults to `True`, in which case it will print the duration
        in minutes and seconds, and size in MB of each claim, if applicable
        (streams of type `'audio'` and `'video'`).
    fees: bool, optional
        It defaults to `True`, in which case it will print the fee (quantity
        and currency) associated with accessing each claim, if applicable.
    title: bool, optional
        It defaults to `False`, in which case the claim `'name'`
        will be printed.
        If it is `True` it will print the claim `'title'` instead.
        To download a stream, the claim name or the claim ID must be used.
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
    dict
        A dictionary with ten keys:
        - 'claims': a list of dictionaries where every dictionary represents
           a claim returned by `claim_search`.
        - 'searched': a paragraph of text that with the information
          that was searched, such as claim type, stream types, and page.
        - 'size': total size of the claims in bytes.
          It can be divided by 1024 to obtain kibibytes, by another 1024
          to obtain mebibytes, and by another 1024 to obtain gibibytes.
        - 'duration': total duration of the claims in seconds.
          It will count only stream types which have a duration
          such as audio and video.
        - 'size_GB': total size in GiB (floating point value)
        - 'd_h': integer hours HH when the duration is shown as HH:MM:SS
        - 'd_min': integer minutes MM when the duration is shown as HH:MM:SS
        - 'd_s`: integer seconds SS when the duration is shown as HH:MM:SS
        - 'days': total seconds converted into days (floating point value)
        - 'summary': paragraph of text describing the number of claims,
           the total size in GiB, and the total duration expressed as HH:MM:SS,
           and days
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    print("Show searched text and tags")
    claims_info = w_claim_search(threads=threads,
                                 page=page,
                                 what="text",
                                 order=order,
                                 text=text,
                                 tags=tags,
                                 claim_type=claim_type,
                                 video_stream=video_stream,
                                 audio_stream=audio_stream,
                                 doc_stream=doc_stream,
                                 img_stream=img_stream,
                                 bin_stream=bin_stream,
                                 model_stream=model_stream,
                                 server=server)

    if claims_info["claims"]:
        prntc.print_sch_claims(claims_info["claims"],
                               create=create, height=height, release=release,
                               claim_id=claim_id, typ=typ, ch_name=ch_name,
                               long_chan=True,
                               sizes=sizes, fees=fees,
                               title=title, sanitize=sanitize,
                               start=1, end=0,
                               reverse=False,
                               file=file, fdate=fdate, sep=sep)

    print(80 * "-")
    print(claims_info["searched"])
    print(40 * "-")
    print(claims_info["summary"])

    return claims_info


if __name__ == "__main__":
    list_trending_claims()
    print()
    list_search_claims(text='trees')
