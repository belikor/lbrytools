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
"""Functions to print downloaded claims in the LBRY network."""
import time

import lbrytools.funcs as funcs
import lbrytools.sort as sort
import lbrytools.print as prnt


def print_summary(show="all",
                  blocks=False, cid=True, blobs=True, size=True,
                  typ=False, ch=False, ch_online=True,
                  name=True, title=False, path=False,
                  sanitize=False,
                  start=1, end=0, channel=None, invalid=False,
                  reverse=False,
                  threads=32,
                  file=None, fdate=False, sep=";",
                  server="http://localhost:5279"):
    """Print a summary of the items downloaded from the LBRY network.

    Parameters
    ----------
    show: str, optional
        It defaults to `'all'`, in which case it shows all items.
        If it is `'incomplete'` it will show claims that are missing blobs.
        If it is `'full'` it will show claims that have all blobs.
        If it is `'media'` it will show claims that have the media file
        (mp4, mp3, mkv, etc.).
        Normally only items that have all blobs also have a media file;
        however, if the claim is currently being downloaded
        a partial media file may be present.
        If it is `'missing'` it will show claims that don't have
        the media file, whether the full blobs are present or not.
    blocks: bool, optional
        It defaults to `False`, in which case it won't print
        the `height` block of the claims.
        If it is `True` it will print this value, which gives some idea
        of when the claim was registered in the blockchain.
    cid: bool, optional
        It defaults to `True`.
        Show the `'claim_id'` of the claim.
        It is a 40 character alphanumeric string.
    blobs: bool, optional
        It defaults to `True`.
        Show the number of blobs in the file, and how many are complete.
    size: bool, optional
        It defaults to `True`.
        Show the length of the stream in minutes and seconds, like `14:12`,
        when possible (audio and video), and also the size in mebibytes (MB).
    typ: bool, optional
        It defaults to `False`.
        Show the type of claim (video, audio, document, etc.)
    ch: bool, optional
        It defaults to `False`.
        Show the name of the channel that published the claim.

        This is slow if `ch_online=True`.
    ch_online: bool, optional
        It defaults to `True`, in which case it searches for the channel name
        by doing a reverse search of the item online. This makes the search
        slow.

        By setting it to `False` it will consider the channel name
        stored in the input dictionary itself, which will be faster
        but it won't be the full name of the channel. If no channel is found
        offline, then it will set a default value `'_None_'` just so
        it can be printed with no error.

        This parameter only has effect if `ch=True`, or if `channel`
        is used, as it internally sets `ch=True`.
    name: bool, optional
        It defaults to `True`.
        Show the name of the claim.
    title: bool, optional
        It defaults to `False`.
        Show the title of the claim.
    path: bool, optional
        It defaults to `False`.
        Show the full path of the saved media file.
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the name of the claim and channel.
        If it is `True` it will remove these unicode characters.
        This option requires the `emoji` package to be installed.
    start: int, optional
        It defaults to 1.
        Show claims starting from this index in the list of items.
    end: int, optional
        It defaults to 0.
        Show claims until and including this index in the list of items.
        If it is 0, it is the same as the last index in the list.
    channel: str, optional
        It defaults to `None`.
        It must be a channel's name, in which case it shows
        only the claims published by this channel.

        Using this parameter sets `ch=True`.
    invalid: bool, optional
        It defaults to `False`, in which case it prints every single claim
        previously downloaded.

        If it is `True` it will only print those claims that are 'invalid',
        that is, those that cannot be resolved anymore from the online
        database. This probably means that the author decided to remove
        the claims at some point after they were downloaded originally.
        This can be verified with the blockchain explorer, by following
        the claim ID for an 'unspent' transaction.

        Using this parameter sets `ch_online=False` as the channel name
        of invalid claims cannot be resolved online, only from the offline
        database.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the output list.
        If it is `True` newer claims are at the beginning of the list.
    threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to resolve claims,
        meaning claims that will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
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
        A dictionary with nine keys:
        - 'claims': a list of dictionaries where every dictionary represents
          a claim returned by `file_list`.
          The list is ordered in ascending order by default (old claims first),
          and in descending order (newer claims first) if `reverse=True`.
          Certain claims don't have `'release_time'` so for them we add
          this key, and use the value of `'timestamp'` for it.
          If there are no claims the list may be empty.
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

    s_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())

    claims_info = sort.sort_items_size(reverse=False, invalid=invalid,
                                       threads=threads,
                                       server=server)

    items = claims_info["claims"]

    if not items or len(items) < 1:
        if file:
            print("No file written.")
        return claims_info

    if invalid:
        ch_online = False

    print()
    prnt.print_items(items=items, show=show,
                     blocks=blocks, cid=cid, blobs=blobs,
                     size=size,
                     typ=typ, ch=ch, ch_online=ch_online,
                     name=name, title=title, path=path,
                     sanitize=sanitize,
                     start=start, end=end, channel=channel,
                     reverse=reverse,
                     file=file, fdate=fdate, sep=sep,
                     server=server)

    e_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())

    out = [40 * "-",
           claims_info["summary"],
           "",
           f"start: {s_time}",
           f"end:   {e_time}"]

    funcs.print_content(out, file=None, fdate=False)

    return claims_info
