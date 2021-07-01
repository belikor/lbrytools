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
"""Functions to clean multiple downloaded claims from the LBRY network."""
import os

import lbrytools.search as srch
import lbrytools.search_ch as srch_ch
import lbrytools.sort as sort
import lbrytools.clean as clean


def ch_cleanup(channel=None, number=2, what="media",
               server="http://localhost:5279"):
    """Delete all claims from a channel, except for the latest ones.

    Parameters
    ----------
    channel: str
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    number: int, optional
        It defaults to 2.
        The number of items to keep from `channel`.
        These will be the newest ones according to their `'release_time'`
        or `'timestamp'`, if the former is missing.
    what: str, optional
        It defaults to `'media'`, in which case only the full media file
        (mp4, mp3, mkv, etc.) is deleted.
        If it is `'blobs'`, it will delete only the blobs.
        If it is `'both'`, it will delete both the media file
        and the blobs.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of bool
        It returns a list of booleans, where each boolean represents
        a deleted item; `True` if the claim was deleted successfully,
        and `False` if it was not.
    False
        If there is a problem or non existing channel,
        it will return `False`.
    """
    if not channel or not isinstance(channel, str):
        print("Clean up items from a single channel.")
        print(f"channel={channel}")
        return False

    if (number is None or number is False
            or not isinstance(number, int) or number < 0):
        number = 2
        print("Number must be a positive integer, "
              f"set to default value, number={number}")

    if (not isinstance(what, str)
            or what not in ("media", "blobs", "both")):
        print(">>> Error: what can only be 'media', 'blobs', 'both'")
        print(f"what={what}")
        return False

    list_info_del = []
    sorted_items = sort.sort_items(channel=channel,
                                   server=server)
    if not sorted_items:
        print()
        return False

    n_items = len(sorted_items)

    remaining = n_items - 0

    for it, item in enumerate(sorted_items, start=1):
        if remaining <= number:
            print(8*"-")
            print(f"Finished deleting; remaining {remaining}")
            print()
            break

        print(f"Claim {it}/{n_items}")

        del_info = clean.delete_single(cid=item["claim_id"], what=what,
                                       server=server)
        list_info_del.append(del_info)
        remaining = n_items - it

        if remaining > number:
            print()

        if remaining == 0:
            print(8*"-")
            print(f"Finished deleting; remaining {remaining}")
            print()

    return list_info_del


def ch_cleanup_multi(channels=None, what="media", number=None,
                     server="http://localhost:5279"):
    """Delete all claims from a list of channels, except for the latest ones.

    Parameters
    ----------
    channels: list of lists
        Each element in the list is a list of two elements.
        The first element is a channel's name, full or partial;
        the second element is an integer that indicates the number
        of items from that channel that will be kept.
        ::
            channels = [
                         ['@MyChannel#5', 3],
                         ['GoodChannel#f', 4],
                         ['Fast_channel', 2]
                       ]
    what: str, optional
        It defaults to `'media'`, in which case only the full media file
        (mp4, mp3, mkv, etc.) is deleted.
        If it is `'blobs'`, it will delete only the blobs.
        If it is `'both'`, it will delete both the media file
        and the blobs.
    number: int, optional
        It defaults to `None`.
        If this is present, it will override the individual
        numbers in `channels`.
        That is, the number of claims that will be kept
        will be the same for every channel.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Alternative input
    -----------------
    channels: list of str
        The list of channels can also be specified as a list of strings.
        ::
            channels = [
                         '@MyChannel#5',
                         'GoodChannel#f',
                         'Fast_channel'
                       ]
            number = 4

        In this case `number` must be specified explicitly to control
        the number of claims that will be kept for every channel.

    Returns
    -------
    list of lists of bool
        A list of lists, where each internal list represents one channel,
        and this internal list has a boolean value for each deleted item;
        `True` if the claim was deleted successfully, and `False` if it
        was not.
    False
        If there is a problem, or an empty channel list,
        it will return `False`.
    """
    if not channels or not isinstance(channels, (list, tuple)):
        m = ["Delete items from a list of channels and numbers.",
             "  [",
             "    ['@MyChannel', 2],",
             "    ['@AwesomeCh:8', 1],",
             "    ['@A-B-C#a', 3]",
             "  ]"]
        print("\n".join(m))
        print(f"channels={channels}")
        return False

    if (not isinstance(what, str)
            or what not in ("media", "blobs", "both")):
        print(">>> Error: what can only be 'media', 'blobs', 'both'")
        print(f"what={what}")
        return False

    DEFAULT_NUM = 2

    if number:
        if not isinstance(number, int) or number < 0:
            number = DEFAULT_NUM
            print("Number must be a positive integer, "
                  f"set to default value, number={number}")

        print("Global value overrides per channel number, "
              f"number={number}")

    n_channels = len(channels)

    if n_channels <= 0:
        print(">>> No channels in the list")
        return False

    list_ch_del_info = []

    # Each element of the `channels` list may be a string,
    # a list with a single element, or a list with multiple elements (two).
    #     ch1 = "Channel"
    #     ch2 = ["@Ch1"]
    #     ch3 = ["Mychan", 2]
    #     channels = [ch1, ch2, ch3]

    for it, channel in enumerate(channels, start=1):
        ch_del_info = []
        if isinstance(channel, str):
            _number = DEFAULT_NUM
        elif isinstance(channel, (list, tuple)):
            if len(channel) < 2:
                _number = DEFAULT_NUM
            else:
                _number = channel[1]
                if not isinstance(_number, (int, float)) or _number < 0:
                    print(f">>> Number set to {DEFAULT_NUM}")
                    _number = DEFAULT_NUM
                _number = int(_number)

            channel = channel[0]

        if not isinstance(channel, str):
            print(f"Channel {it}/{n_channels}, {channel}")
            print(">>> Error: channel must be a string. Skip channel.")
            print()
            list_ch_del_info.append(ch_del_info)
            continue

        if not channel.startswith("@"):
            channel = "@" + channel

        # Number overrides the individual number for all channels
        if number:
            _number = number

        print(f"Channel {it}/{n_channels}, {channel}")
        ch_del_info = ch_cleanup(channel=channel, number=_number, what=what,
                                 server=server)

        list_ch_del_info.append(ch_del_info)

    return list_ch_del_info


def remove_media(never_delete=None,
                 server="http://localhost:5279"):
    """Remove all media files but leave the binary blobs.

    This function is intended for systems that will only seed content.
    It should be run after downloading various claims, for example,
    with `download_single` or `ch_download_latest_multi`.
    It will delete only the media files (mp4, mp3, mkv, etc.)
    but leave the blobs intact to continue seeding them to the network.

    Parameters
    ----------
    never_delete: list of str, optional
        It defaults to `None`.
        If it exists it is a list with channel names.
        The content produced by these channels will not be deleted
        so the media files and blobs will remain in `main_dir`.

        Using this parameter is slow as it needs to perform
        an additional search for the channel.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        It returns `True` if the older files were successfully deleted.
        It returns `False` if there is a problem, or if there
        was nothing to clean up.
    """
    if never_delete and not isinstance(never_delete, (list, tuple)):
        print("Must be a list of channels that should never be deleted.")
        print(f"never_delete={never_delete}")
        return False

    print(80 * "-")
    print("Delete all media files")

    items = sort.sort_items(server=server)
    n_items = len(items)

    for it, item in enumerate(items, start=1):
        out = "{:4d}/{:4d}, {}, ".format(it, n_items, item["claim_name"])
        if never_delete:
            channel = srch_ch.find_channel(cid=item["claim_id"],
                                           full=False,
                                           server=server)
            if not channel:
                continue

            channel = channel.lstrip("@")
            skip = False

            for safe_channel in never_delete:
                if channel in safe_channel:
                    skip = True
                    break

            if skip:
                print(out + f"item from {channel} will not be deleted. "
                      "Skipping.")
                continue

        path = item["download_path"]
        if path:
            os.remove(path)
            print(out + f"delete {path}")
        else:
            print(out + "no media found locally, probably already deleted.")

    print("Media files deleted")
    return True


def remove_claims(start=1, end=0, file=None, invalid=False,
                  what="media",
                  server="http://localhost:5279"):
    """Delete claims from a file, or delete the ones already present.

    Parameters
    ----------
    start: int, optional
        It defaults to 1.
        Operate on the item starting from this index in the internal list
        of claims or in the claims provided by `file`.
    end: int, optional
        It defaults to 0.
        Operate until and including this index in the internal list of claims
        or in the claims provided by `file`.
        If it is 0, it is the same as the last index.
    file: str, optional
        It defaults to `None`.
        The file to read claims from. It is a comma-separated value (CSV)
        list of claims, in which each row represents a claim,
        and one element is the `'claim_id'` which can be used
        with `delete_single` to delete that claim.

        If `file=None` it will delete the claims obtained
        from `sort_items` which should already be present
        in the system fully or partially.
    invalid: bool, optional
        It defaults to `False`, in which case it will assume
        the processed claims are still valid in the online database.
        It will use `lbrynet claim search` to resolve the `claim_id`.

        If it is `True` it will assume the claims are no longer valid,
        that is, that the claims have been removed from the online database
        and only exist locally.
        In this case, it will use `lbrynet file list` to resolve
        the `claim_id`.

        Therefore this parameter is required if `file` is a document
        containing 'invalid' claims, otherwise the claims won't be found
        and won't be deleted.
    what: str, optional
        It defaults to `'media'`, in which case only the full media file
        (mp4, mp3, mkv, etc.) is deleted.
        If it is `'blobs'`, it will delete only the blobs.
        If it is `'both'`, it will delete both the media file
        and the blobs.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of bool
        It returns a list of booleans, where each boolean represents
        a deleted item; `True` if the claim was deleted successfully,
        and `False` if it was not.
    False
        If there is a problem, non-existing claims, or non-existing file,
        it will return `False`.
    """
    print(80 * "-")

    if not file:
        print("Remove claims from existing list")
        sorted_items = sort.sort_items(server=server)

        if not sorted_items:
            print(">>> Error: no claims previously downloaded.")
            return False
    else:
        if file and not isinstance(file, str) or not os.path.exists(file):
            print("The file path must exist.")
            print(f"file={file}")
            return False

        print("Remove claims from existing file")
        sorted_items = srch.parse_claim_file(file=file)
        print()

        if not sorted_items:
            print(">>> Error: the file must have a 'claim_id' "
                  "(40-character alphanumeric string); "
                  "could not parse the file.")
            print(f"file={file}")
            return False

    n_items = len(sorted_items)

    list_del_info = []

    for it, item in enumerate(sorted_items, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        print(f"Claim {it}/{n_items}")
        del_info = clean.delete_single(cid=item["claim_id"],
                                       invalid=invalid,
                                       what=what,
                                       server=server)
        list_del_info.append(del_info)
        print()

    return list_del_info
