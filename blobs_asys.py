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
"""Functions to help use with blobs from LBRY content."""
import os
import time

import lbrytools.funcs as funcs
import lbrytools.printf as prntf
import lbrytools.clean as clean
import lbrytools.download as dld
import lbrytools.blobs as blobs


def analyze_blobs(blobfiles=None, channel=None,
                  start=1, end=0,
                  print_msg=False, print_each=False,
                  server="http://localhost:5279"):
    """Perform an analysis of all existing blobs in blobfiles directory.

    Parameters
    ----------
    blobfiles: str
        It defaults to `'$HOME/.local/share/lbry/lbrynet/blobfiles'`.
        The path to the directory where the blobs were downloaded.
        This is normally seen with `lbrynet settings get`, under `'data_dir'`.
        It can be any other directory if it is symbolically linked
        to it, such as `'/opt/lbryblobfiles'`
    channel: str, optional
        It defaults to `None`.
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    start: int, optional
        It defaults to 1.
        Count the blobs from claims starting from this index
        in the list of items.
    end: int, optional
        It defaults to 0.
        Count the blobs from claims until and including this index
        in the list of items.
        If it is 0, it is the same as the last index in the list.
    print_msg: bool, optional
        It defaults to `True`, in which case it will print information
        on the found claim.
        If `print_msg=False`, it also implies `print_each=False`.
    print_each: bool, optional
        It defaults to `False`.
        If it is `True` it will print all blobs
        that belong to the claim, and whether each of them is already
        in `blobfiles`.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict, list of dict, list of dict, list of dict, list of dict
        A tuple of five lists.
        - The first list contains blob information for claims
          that are complete.
        - The second list contains blob information for claims
          that have missing blobs. These claims need to be redownloaded
          in order to have all blobs.
        - The third list contains blob information for claims
          whose `'sd_hash'` is missing so it is impossible to determine
          how many blobs they are supposed to have. These claims need to be
          redownloaded at least to get their `'sd_hash'`.
        - The fourth list contains blob information for claims
          that were not found in the online database (blockchain).
          These are 'invalid' claims, that is, claims that were donwloaded
          in the past, but then they were removed by their authors.
        - The fifth list contains blob information for claims
          that had other errors like a connectivity problem with the server.

        If all claims have been properly downloaded all lists must be empty
        except for the first one.
        The claims of the second and third lists indicate incomplete downloads,
        or manually moved blobs, so the claims just need to be redownloaded.

        In each list, the blob information is a dictionary containing two keys
        - `'num'`: an integer from 1 up to the last item processed.
        - `'blob_info'`: the dictionary output from the `count_blobs` method.
          In rare cases this may be a single boolean value `False`
          if there was an unexpected error like a connectivity problem
          with the server.
    False
        If there is a problem, like non existing blobfiles directory,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if (not blobfiles or not isinstance(blobfiles, str)
            or not os.path.exists(blobfiles)):
        print("Count the blobs of the claim from the blobfiles directory")
        print(f"blobfiles={blobfiles}")
        print("This is typically '$HOME/.local/share/lbry/lbrynet/blobfiles'")

        home = os.path.expanduser("~")
        blobfiles = os.path.join(home,
                                 ".local", "share",
                                 "lbry", "lbrynet", "blobfiles")

        if not os.path.exists(blobfiles):
            print(f"Blobfiles directory does not exist: {blobfiles}")
            return False

    if channel and not isinstance(channel, str):
        print("Channel must be a string. Set to 'None'.")
        print(f"channel={channel}")
        channel = None

    if channel:
        if not channel.startswith("@"):
            channel = "@" + channel

    blob_all_info = blobs.count_blobs_all(blobfiles=blobfiles,
                                          channel=channel,
                                          start=start, end=end,
                                          print_msg=print_msg,
                                          print_each=print_each,
                                          server=server)
    if not blob_all_info:
        return False
    print()

    if channel:
        print(f"Analysis of existing blob files for: {channel}")
    else:
        print("Analysis of existing blob files")
    print(80 * "-")
    print(f"Blobfiles: {blobfiles}")

    all_existing_blobs = os.listdir(blobfiles)
    n_all_existing = len(all_existing_blobs)

    claims_blobs_complete = []
    claims_blobs_incomplete = []
    claims_no_sd_hash = []
    claims_not_found = []
    claims_other_error = []

    for info in blob_all_info:
        blob_info = info["blob_info"]

        if blob_info:
            if "all_present" in blob_info and blob_info["all_present"]:
                claims_blobs_complete.append(info)
            elif "all_present" in blob_info and not blob_info["all_present"]:
                claims_blobs_incomplete.append(info)

            if "error_no_sd_hash" in blob_info:
                claims_no_sd_hash.append(info)
            if "error_not_found" in blob_info:
                claims_not_found.append(info)
        else:
            claims_other_error.append(info)

    # Assemble existing blobs in a single list
    all_blobs = []
    counted_data_blobs = []
    counted_sd_hash_blobs = []

    for info in claims_blobs_complete:
        blob_info = info["blob_info"]
        all_blobs.append(blob_info["sd_hash"])
        counted_sd_hash_blobs.append(blob_info["sd_hash"])

        for blob in blob_info["blobs"]:
            all_blobs.append(blob[1])
            counted_data_blobs.append(blob[1])

    for info in claims_blobs_incomplete:
        blob_info = info["blob_info"]
        all_blobs.append(blob_info["sd_hash"])
        counted_sd_hash_blobs.append(blob_info["sd_hash"])

        existing = blob_info["blobs"][:]
        for blob in existing:
            all_blobs.append(blob[1])

        for missing_blob in blob_info["missing"]:
            existing.remove(missing_blob)

        for blob in existing:
            counted_data_blobs.append(blob[1])

    n_all_blobs = len(all_blobs)
    n_data = len(counted_data_blobs)

    minus_data_blobs = all_existing_blobs[:]
    for data_blob in counted_data_blobs:
        minus_data_blobs.remove(data_blob)

    n_minus_data = len(minus_data_blobs)

    n_sd_hash = len(counted_sd_hash_blobs)
    n_sum = n_data + n_sd_hash

    minus_data_sd_blobs = minus_data_blobs[:]
    for sd_blob in counted_sd_hash_blobs:
        minus_data_sd_blobs.remove(sd_blob)

    n_minus_data_sd = len(minus_data_sd_blobs)

    print("Total blobs that should exist: "
          f"[{n_all_blobs:7d}] (with complete claims)")
    print(40 * "-")
    print(f"Total files in directory: {n_all_existing:7d} | remaining")
    print()
    print(f" - Data blobs             {n_data:7d} | {n_minus_data:7d}")
    print(f" - 'sd_hash' blobs        {n_sd_hash:7d} | {n_minus_data_sd:7d}")
    if n_all_blobs == n_sum:
        print(f" - Sum                  >[{n_sum:7d}]")
    else:
        print(f" - Sum                  *[{n_sum:7d}]")

    if channel:
        print(f"Files that don't belong to {channel}: {n_minus_data_sd}")
    else:
        print("Files that don't belong to any downloaded claim: "
              f"{n_minus_data_sd} (orphaned blobs from invalid claims)")

    for rem_blob in minus_data_sd_blobs:
        if len(rem_blob) != 96:
            print(rem_blob)

    return (claims_blobs_complete, claims_blobs_incomplete,
            claims_no_sd_hash, claims_not_found, claims_other_error)


def analyze_channel(blobfiles=None, channel=None,
                    start=1, end=0,
                    print_msg=True,
                    server="http://localhost:5279"):
    """Obtain usage information from a channel by analyzing its blobs.

    If the channel is not specified, it will analyze all blobs from all valid
    claims in the system, and thus provide an overall summary of all downloads.

    Parameters
    ----------
    blobfiles: str
        It defaults to `'$HOME/.local/share/lbry/lbrynet/blobfiles'`.
        The path to the directory where the blobs were downloaded.
        This is normally seen with `lbrynet settings get`, under `'data_dir'`.
        It can be any other directory if it is symbolically linked
        to it, such as `'/opt/lbryblobfiles'`
    channel: str, optional
        It defaults to `None`.
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.

        If `channel=None` it will go through all valid claims
        so it will provide a general summary of all downloads.
    start: int, optional
        It defaults to 1.
        Count the blobs from claims starting from this index
        in the list of items.
    end: int, optional
        It defaults to 0.
        Count the blobs from claims until and including this index
        in the list of items.
        If it is 0, it is the same as the last index in the list.
    print_msg: bool, optional
        It defaults to `True`, in which case it will print the final
        summary of the channels.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with 7 keys.
        - `'channel'` the name, or `None` if all channels were inspected.
        - `'complete_claims'` number of completed claims.
        - `'complete_blobs'` number of blobs in completed claims.
        - `'complete_usage'` value in gigabytes (GB) of all blobs
          from completed claims.
        - `'incomplete_claims'` number of incomplete claims.
        - `'incomplete_blobs'` number of blobs in incomplete claims.
        - `'incomplete_usage'` value in gigabytes (GB) of all blobs
          from incomplete claims.
    """
    if not funcs.server_exists(server=server):
        return False

    s_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
    if (not blobfiles or not isinstance(blobfiles, str)
            or not os.path.exists(blobfiles)):
        print("Count the blobs of the claim from the blobfiles directory")
        print(f"blobfiles={blobfiles}")
        print("This is typically '$HOME/.local/share/lbry/lbrynet/blobfiles'")

        home = os.path.expanduser("~")
        blobfiles = os.path.join(home,
                                 ".local", "share",
                                 "lbry", "lbrynet", "blobfiles")

        if not os.path.exists(blobfiles):
            print(f"Blobfiles directory does not exist: {blobfiles}")
            return False

    if channel and not isinstance(channel, str):
        print("Channel must be a string. Set to 'None'.")
        print(f"channel={channel}")
        channel = None

    if channel:
        if not channel.startswith("@"):
            channel = "@" + channel

    output = analyze_blobs(blobfiles=blobfiles, channel=channel,
                           start=start, end=end,
                           print_msg=False,
                           print_each=False,
                           server=server)
    if not output:
        return False

    claims_complete = output[0]
    claims_incomplete = output[1]
    # claims_no_sd_hash = output[2]
    # claims_not_found = output[3]
    # claims_other_error = output[4]
    print()

    n_claims_complete = len(claims_complete)
    n_claims_incomplete = len(claims_incomplete)

    size_complete = 0
    n_blobs_complete = 0
    size_incomplete = 0
    n_blobs_incomplete = 0

    for info in claims_complete:
        blob_info = info["blob_info"]
        sd_hash = os.path.join(blobfiles, blob_info["sd_hash"])
        size_complete += os.path.getsize(sd_hash)
        n_blobs_complete += 1
        n_blobs_complete += len(blob_info["blobs"])

        for blob in blob_info["blobs"]:
            blob_file = os.path.join(blobfiles, blob[1])
            size_complete += os.path.getsize(blob_file)

    for info in claims_incomplete:
        blob_info = info["blob_info"]
        sd_hash = os.path.join(blobfiles, blob_info["sd_hash"])
        size_incomplete += os.path.getsize(sd_hash)
        n_blobs_incomplete += 1
        n_blobs_incomplete += len(blob_info["blobs"])
        n_blobs_incomplete -= len(blob_info["missing"])

        existing = blob_info["blobs"][:]
        for missing_blob in blob_info["missing"]:
            existing.remove(missing_blob)
        for blob in existing:
            blob_file = os.path.join(blobfiles, blob[1])
            size_incomplete += os.path.getsize(blob_file)

    size_complete = size_complete / (1024*1024*1024)
    size_incomplete = size_incomplete / (1024*1024*1024)

    if print_msg:
        if channel:
            print(f"Channel: {channel}")

        print(f"complete:   {n_claims_complete:4d},  "
              f"blobs: {n_blobs_complete:7d},  "
              f"usage: {size_complete:9.4f} GB")
        print(f"incomplete: {n_claims_incomplete:4d},  "
              f"blobs: {n_blobs_incomplete:7d},  "
              f"usage: {size_incomplete:9.4f} GB")
        print(40 * "-")

    n_claims = n_claims_complete + n_claims_incomplete
    n_blobs_all = n_blobs_complete + n_blobs_incomplete
    n_size_all = size_complete + size_incomplete

    if print_msg:
        print(f"all claims: {n_claims:4d},  "
              f"blobs: {n_blobs_all:7d},  "
              f"usage: {n_size_all:9.4f} GB")
        print()
        e_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
        print(f"start: {s_time}")
        print(f"end:   {e_time}")

    info = {"channel": channel,
            "complete_claims": n_claims_complete,
            "complete_blobs": n_blobs_complete,
            "complete_usage": size_complete,
            "incomplete_claims": n_claims_incomplete,
            "incomplete_blobs": n_blobs_incomplete,
            "incomplete_usage": size_incomplete}
    return info


def print_channel_analysis(blobfiles=None, split=True, bar=False,
                           start=1, end=0,
                           sort=False, reverse=False,
                           file=None, fdate=False,
                           server="http://localhost:5279"):
    """Print a summary of all blobs of all channels.

    Parameters
    ----------
    blobfiles: str
        It defaults to `'$HOME/.local/share/lbry/lbrynet/blobfiles'`.
        The path to the directory where the blobs were downloaded.
        This is normally seen with `lbrynet settings get`, under `'data_dir'`.
        It can be any other directory if it is symbolically linked
        to it, such as `'/opt/lbryblobfiles'`
    split: bool, optional
        It defaults to `True`, in which case the summary for each channel
        will be split into claims that are complete and incomplete.
        If it is `False` it will print the summary with the claims combined.
    bar: bool, optional
        It defaults to `False`, in which case no bar is printed.
        If it is `True` it will display a bar indicated the usage
        of a channel.
        The parameter `bar=True` overrides the `split` parameter.
    start: int, optional
        It defaults to 1.
        Count the channels starting from this index in the list of channels.
    end: int, optional
        It defaults to 0.
        Count the channels until and including this index
        in the list of channels.
        If it is 0, it is the same as the last index in the list.
    sort: bool, optional
        It defaults to `True`, in which case the channels will be ordered
        by the amount of space their claims take on the system.
        If it is `False` the channels will be in alphabetical order.
    reverse: bool, optional
        It defaults to `False`, in which case the channels will be ordered
        in ascending order of usage, that is, how much hard drive space
        their blobs take.
        If it is `True` it will be ordered in descending order.
        This parameter only works in combination with `sort=True`.
    file: str, optional
        It defaults to `None`.
        It must be a writable path to which the summary will be written.
        Otherwise the summary will be printed to the terminal.
    fdate: bool, optional
        It defaults to `False`.
        If it is `True` it will add the date to the name of the summary file.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    bool
        It returns `True` if it printed the summary successfully.
        If there is any error it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    s_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
    channels = prntf.print_channels(full=False, canonical=False,
                                    invalid=False, offline=False,
                                    print_msg=True,
                                    file=None, fdate=False,
                                    server=server)
    if not channels:
        return False

    print()
    n_channels = len(channels)

    out = []
    claims = []
    blobs = []
    sizes = []
    msg = []

    if split and not bar:
        out.append("{:43s}  completed (incomplete)".format(""))
    elif bar:
        out.append("{:83}  claims,   blobs,    use".format(""))

    for it, channel in enumerate(channels, start=1):
        if it < start:
            continue
        if end != 0 and it > end:
            break

        print(f"Channel {it}/{n_channels}")
        info = analyze_channel(blobfiles=blobfiles, channel=channel,
                               print_msg=False,
                               server=server)
        if not info:
            continue

        n_c_complete = info["complete_claims"]
        n_c_blobs = info["complete_blobs"]
        n_c_size = info["complete_usage"]

        n_i_complete = info["incomplete_claims"]
        n_i_blobs = info["incomplete_blobs"]
        n_i_size = info["incomplete_usage"]

        n_claims = n_c_complete + n_i_complete
        n_blobs_all = n_c_blobs + n_i_blobs
        n_size_all = n_c_size + n_i_size
        claims.append(n_claims)
        blobs.append(n_blobs_all)
        sizes.append(n_size_all)

        ch = channel + ","
        head = f"{it:3d}/{n_channels:3d}, {ch:34s}  "

        if split and not bar:
            text = (f"claims: {n_c_complete:4d} ({n_i_complete:4d}),  "
                    f"blobs: {n_c_blobs:7d} ({n_i_blobs:7d}),  "
                    f"use: {n_c_size:7.2f} GB ({n_i_size:7.2f} GB)")
        elif not split and not bar:
            text = (f"claims: {n_claims:4d},  "
                    f"blobs: {n_blobs_all:7d},  "
                    f"use: {n_size_all:7.2f} GB")
        else:
            text = ""
        msg.append(head + text)

    if bar:
        # Draw a bar indicating the amount of space used.
        spaces = 40
        top = max(sizes)
        sizes_p = [item/top for item in sizes]

        for it in range(len(sizes)):
            cl = claims[it]
            bl = blobs[it]
            sz = sizes[it]
            percent = sizes_p[it]
            m = int(percent * spaces)

            msg[it] += "|"
            if percent > 0.95:
                msg[it] += (spaces-1)*"="
            else:
                msg[it] += m*"="
                msg[it] += (spaces-1-m)*"."

            msg[it] += "|"
            msg[it] += f" {cl:4d}, {bl:7d}, {sz:7.2f} GB"

    if sort:
        # Pair the size and the message that we want to print in a dictionary
        pair = {}
        for it in range(len(sizes)):
            pair[sizes[it]] = msg[it]

        # Sort by the first element of the pair, the size
        sorted_list = sorted(pair.items(),
                             reverse=reverse,
                             key=lambda item: item[0])

        # Just take the second element, the message, into a new list
        msg = []
        for first, second in sorted_list:
            msg.append(second)

    out.extend(msg)

    fd = 0

    if file:
        dirn = os.path.dirname(file)
        base = os.path.basename(file)

        if fdate:
            fdate = time.strftime("%Y%m%d_%H%M", time.localtime()) + "_"
        else:
            fdate = ""

        file = os.path.join(dirn, fdate + base)

        try:
            fd = open(file, "w")
        except (FileNotFoundError, PermissionError) as err:
            print(f"Cannot open file for writing; {err}")

    if file and fd:
        print("\n".join(msg), file=fd)
        fd.close()
        print(f"Summary written: {file}")
    else:
        print("\n".join(out))

    print()
    e_time = time.strftime("%Y-%m-%d_%H:%M:%S%z %A", time.localtime())
    print(f"start: {s_time}")
    print(f"end:   {e_time}")

    return True


def download_missing_blobs(blobfiles=None, ddir=None, channel=None,
                           start=1, end=0,
                           print_msg=False, print_each=False,
                           server="http://localhost:5279"):
    """Download the missing blobfiles from the downloaded claims.

    It will finish downloading incomplete claims, and claims without
    the `'sd_hash'` blob.

    Parameters
    ----------
    blobfiles: str
        It defaults to `'$HOME/.local/share/lbry/lbrynet/blobfiles'`.
        The path to the directory where the blobs were downloaded.
        This is normally seen with `lbrynet settings get`, under `'data_dir'`.
        It can be any other directory if it is symbolically linked
        to it, such as `'/opt/lbryblobfiles'`
    ddir: str, optional
        It defaults to `$HOME`.
        The path to the download directory.
    channel: str, optional
        It defaults to `None`.
        A channel's name, full or partial:
        `'@MyChannel#5'`, `'MyChannel#5'`, `'MyChannel'`

        If a simplified name is used, and there are various channels
        with the same name, the one with the highest LBC bid will be selected.
        Enter the full name to choose the right one.
    start: int, optional
        It defaults to 1.
        Count the blobs from claims starting from this index
        in the list of items.
    end: int, optional
        It defaults to 0.
        Count the blobs from claims until and including this index
        in the list of items.
        If it is 0, it is the same as the last index in the list.
    print_msg: bool, optional
        It defaults to `True`, in which case it will print information
        on the found claim.
        If `print_msg=False`, it also implies `print_each=False`.
    print_each: bool, optional
        It defaults to `False`.
        If it is `True` it will print all blobs
        that belong to the claim, and whether each of them is already
        in `blobfiles`.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list, list
        A tuple of two lists.
        The first list has the return information of the downloaded claims
        that were missing blobs.
        The second list has the return information of the downloaded claims
        that were missing the `'sd_hash'` blob.
    """
    if not funcs.server_exists(server=server):
        return False

    if (not blobfiles or not isinstance(blobfiles, str)
            or not os.path.exists(blobfiles)):
        print("Count the blobs of the claim from the blobfiles directory")
        print(f"blobfiles={blobfiles}")
        print("This is typically '$HOME/.local/share/lbry/lbrynet/blobfiles'")

        home = os.path.expanduser("~")
        blobfiles = os.path.join(home,
                                 ".local", "share",
                                 "lbry", "lbrynet", "blobfiles")

        if not os.path.exists(blobfiles):
            print(f"Blobfiles directory does not exist: {blobfiles}")
            return False

    if channel and not isinstance(channel, str):
        print("Channel must be a string. Set to 'None'.")
        print(f"channel={channel}")
        channel = None

    if channel:
        if not channel.startswith("@"):
            channel = "@" + channel

    output = analyze_blobs(blobfiles=blobfiles, channel=channel,
                           start=start, end=end,
                           print_msg=print_msg,
                           print_each=print_each,
                           server=server)
    if not output:
        return False

    # claims_complete = output[0]
    claims_incomplete = output[1]
    claims_no_sd_hash = output[2]
    # claims_not_found = output[3]
    # claims_other_error = output[4]
    print()

    if not (claims_incomplete or claims_no_sd_hash):
        if channel:
            print(f"All claims from {channel} have complete blobs "
                  "(data and 'sd_hash'). "
                  "Nothing will be downloaded.")
        else:
            print("All claims have complete blobs (data and 'sd_hash'). "
                  "Nothing will be downloaded.")
        return False

    n_claims_incomplete = len(claims_incomplete)
    n_claims_no_sd_hash = len(claims_no_sd_hash)

    info_get_incomplete = []
    info_get_no_sd = []

    if n_claims_incomplete:
        print("Claims with incomplete blobs: "
              f"{n_claims_incomplete} (will be redownloaded)")
    else:
        print("Claims with incomplete blobs: "
              f"{n_claims_incomplete} (nothing to redownload)")

    for it, info in enumerate(claims_incomplete, start=1):
        blob_info = info["blob_info"]
        uri = blob_info["canonical_url"]
        cid = blob_info["claim_id"]
        name = blob_info["name"]

        print(f"Claim {it}/{n_claims_incomplete}")
        # The missing blobs will only be downloaded if the media file
        # is not present so we must make sure it is deleted.
        print("Ensure the media file is deleted.")
        clean.delete_single(uri=uri, cid=cid, name=name, what="media",
                            server=server)
        print()
        info = dld.download_single(uri=uri, cid=cid, name=name, ddir=ddir,
                                   server=server)
        info_get_incomplete.append(info)
        print()

    if n_claims_no_sd_hash:
        print("Claims with no 'sd_hash' blobs: "
              f"{n_claims_no_sd_hash} (will be redownloaded)")
    else:
        print("Claims with no 'sd_hash' blobs: "
              f"{n_claims_no_sd_hash} (nothing to redownload)")

    for it, info in enumerate(claims_no_sd_hash, start=1):
        blob_info = info["blob_info"]
        uri = blob_info["canonical_url"]
        cid = blob_info["claim_id"]
        name = blob_info["name"]

        print(f"Claim {it}/{n_claims_no_sd_hash}")
        # The missing blobs will only be downloaded if the media file
        # is not present so we must make sure it is deleted.
        print("Ensure the media file is deleted.")
        clean.delete_single(uri=uri, cid=cid, name=name, what="media",
                            server=server)
        print()
        info = dld.download_single(uri=uri, cid=cid, name=name, ddir=ddir,
                                   server=server)
        info_get_no_sd.append(info)
        print()

    return info_get_incomplete, info_get_no_sd
