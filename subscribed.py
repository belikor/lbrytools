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
"""Functions to display channel information like subscriptions."""
import concurrent.futures as fts
import time

import requests

import lbrytools.funcs as funcs
import lbrytools.search as srch
import lbrytools.search_ch as srch_ch


def validate_ch(channel, server="http://localhost:5279"):
    """Add 'valid' key to the channel dictionary."""
    channel["valid"] = srch.search_item(uri=channel["uri"],
                                        print_error=False,
                                        server=server)
    return channel


def filter_valid(resolved_channels, f_valid=True):
    """Filter list by value of 'valid' key."""
    ch_valid_filtered = []

    for channel in resolved_channels:
        valid = channel["valid"]

        if ((f_valid and not valid)
                or (not f_valid and valid)):
            continue

        ch_valid_filtered.append(channel)

    return ch_valid_filtered


def filter_notif(resolved_channels, f_notifications=False):
    """Filter list by value of 'notificationsDisabled' key."""
    ch_notif_filtered = []

    for channel in resolved_channels:
        if "notificationsDisabled" in channel:
            ch_nots = not channel["notificationsDisabled"]
        else:
            ch_nots = False

        if ((f_notifications and not ch_nots)
                or (not f_notifications and ch_nots)):
            continue

        ch_notif_filtered.append(channel)

    return ch_notif_filtered


def search_ch_subs(shared=True,
                   show_all=True, filtering="valid",
                   valid=True, notifications=False,
                   threads=32,
                   server="http://localhost:5279"):
    """Search the wallet for the channel subscriptions.

    Parameters
    ----------
    shared: bool, optional
        It defaults to `True`, in which case it uses the shared database
        synchronized with Odysee online.
        If it is `False` it will use only the local database
        to `lbrynet`, for example, used by the LBRY Desktop application.
    show_all: bool, optional
        It defaults to `True`, in which case all followed channels
        will be printed, regardless of `filtering`, `valid`,
        or `notifications`.
        If it is `False` then we can control what channels to show
        with `filtering`, `valid`, or `notifications`.
    filtering: str, optional
        It defaults to `'valid'`. It is the type of filtering that
        will be done as long as `show_all=False`.
        It can be `'valid'` (depending on the value of `valid` parameter),
        `'notifications'` (depending on the value of `notifications`),
        or `'both'` (depending on the values of `valid` and `notifications`).
        If `'both'`, the list of channels will be filtered by `valid` first,
        and then by `notifications`.
    valid: bool, optional
        It defaults to `True` in which case only the channels that resolve
        online will be returned.
        If it is `False` it will return only those channels that no longer
        resolve online.
        This parameter only works when `show_all=False`
        and `filtering='valid'` or `'both'`.
    notifications: bool, optional
        It defaults to `False` in which case only the channels
        that have notifications disabled will be returned.
        If it is `True` it will return only those channels
        that have notifications enabled.
        This parameter only works when `show_all=False`
        and `filtering='notifications'` or `'both'`.
    threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to resolve channels
        online, meaning that many channels will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        It returns the list of dictionaries representing
        the filtered channels depending on the values of `shared`, `show_all`,
        `filtering`, `valid`, and `notifications`.

        Each dictionary has three keys:
        - 'uri': the `'permanent_url'` of the channel.
        - 'notificationsDisabled': a boolean value, indicating whether
          the notification is enabled for that channel or not.
        - 'valid': it's the dictionary of the resolved channel,
          or `False` if the channel is invalid and doesn't exist.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    msg = {"method": "preference_get",
           "params": {}}

    output = requests.post(server, json=msg).json()
    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    result = output["result"]

    sync = result.get("enable-sync", False)

    r_local = result["local"]

    if "shared" in result:
        r_shared = result["shared"]

    print("Channel subscriptions")
    print(80 * "-")
    print(f"Synchronization: {sync}")
    print("Show all:", bool(show_all))
    if not show_all:
        print(f"Filtering: '{filtering}'")
        print("- Valid:", bool(valid))
        print("- Notifications:", bool(notifications))

    following_local = r_local["value"]["following"]

    if "shared" in result:
        following_shared = r_shared["value"]["following"]

    if shared and "shared" in result:
        print("Database: shared")
        channels = following_shared
        n_channels = len(following_shared)
    else:
        if shared:
            print("No shared database, will use local")
        else:
            print("Database: local")
        channels = following_local
        n_channels = len(following_local)

    res_channels = []

    # Iterables to be passed to the ThreadPoolExecutor
    servers = (server for n in range(n_channels))

    if threads:
        with fts.ThreadPoolExecutor(max_workers=threads) as executor:
            # The input must be iterables
            res_channels = executor.map(validate_ch, channels, servers)
            print(f"Resolving channels; max threads: {threads}")
            res_channels = list(res_channels)  # generator to list
    else:
        for channel in channels:
            result = validate_ch(channel, server=server)
            res_channels.append(result)

    if show_all:
        return res_channels

    ch_valid_filtered = filter_valid(res_channels,
                                     f_valid=valid)

    ch_notif_filtered = filter_notif(res_channels,
                                     f_notifications=notifications)

    ch_both = filter_notif(ch_valid_filtered,
                           f_notifications=notifications)

    if filtering in "valid":
        ch_filtered = ch_valid_filtered
    elif filtering in "notifications":
        ch_filtered = ch_notif_filtered
    elif filtering in "both":
        ch_filtered = ch_both

    return ch_filtered


def print_ch_subs(channels=None,
                  claim_id=False,
                  file=None, fdate=False, sep=";"):
    """Print channels found from the subscriptions."""
    out = []
    n_channels = len(channels)

    for num, channel in enumerate(channels, start=1):
        name, cid = channel["uri"].lstrip("lbry://").split("#")
        f_name = name + "#" + cid[0:3]
        f_name = f'"{f_name}"'

        if "notificationsDisabled" in channel:
            ch_nots = not channel["notificationsDisabled"]
        else:
            ch_nots = False
        ch_nots = f"{ch_nots}"

        if "valid" in channel:
            valid = bool(channel["valid"])
        else:
            valid = "_____"
        valid = f"{valid}"

        line = f"{num:4d}/{n_channels:4d}" + f"{sep} "
        if claim_id:
            line += f"{cid}" + f"{sep} "
        line += f"{f_name:48s}" + f"{sep} "
        line += f"valid: {valid:5s}" + f"{sep} "
        line += f"notifications: {ch_nots:5s}"

        out.append(line)

    funcs.print_content(out, file=file, fdate=fdate)


def list_ch_subs(shared=True,
                 show_all=True, filtering="valid",
                 valid=True, notifications=False,
                 threads=32,
                 claim_id=False,
                 file=None, fdate=False, sep=";",
                 server="http://localhost:5279"):
    """Search and print the channels from our subscriptions.

    Parameters
    ----------
    shared: bool, optional
        It defaults to `True`, in which case it uses the shared database
        synchronized with Odysee online.
        If it is `False` it will use only the local database
        to `lbrynet`, for example, used by the LBRY Desktop application.
    show_all: bool, optional
        It defaults to `True`, in which case all followed channels
        will be printed, regardless of `filtering`, `valid`,
        or `notifications`.
        If it is `False` then we can control what channels to show
        with `filtering`, `valid`, or `notifications`.
    filtering: str, optional
        It defaults to `'valid'`. It is the type of filtering that
        will be done as long as `show_all=False`.
        It can be `'valid'` (depending on the value of `valid` parameter),
        `'notifications'` (depending on the value of `notifications`),
        or `'both'` (depending on the values of `valid` and `notifications`).
        If `'both'`, the list of channels will be filtered by `valid` first,
        and then by `notifications`.
    valid: bool, optional
        It defaults to `True` in which case only the channels that resolve
        online will be returned.
        If it is `False` it will return only those channels that no longer
        resolve online.
        This parameter only works when `show_all=False`
        and `filtering='valid'` or `'both'`.
    notifications: bool, optional
        It defaults to `False` in which case only the channels
        that have notifications disabled will be returned.
        If it is `True` it will return only those channels
        that have notifications enabled.
        This parameter only works when `show_all=False`
        and `filtering='notifications'` or `'both'`.
    threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to resolve channels
        online, meaning that many channels will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the `claim_id` of the channel.
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
        It returns the list of dictionaries representing
        the filtered channels depending on the values of `shared`, `show_all`,
        `filtering`, `valid`, and `notifications`.

        Each dictionary has three keys:
        - 'uri': the `'permanent_url'` of the channel.
        - 'notificationsDisabled': a boolean value, indicating whether
          the notification is enabled for that channel or not.
        - 'valid': it's the dictionary of the resolved channel,
          or `False` if the channel is invalid and doesn't exist.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    ch_filtered = search_ch_subs(shared=shared,
                                 show_all=show_all, filtering=filtering,
                                 valid=valid,
                                 notifications=notifications,
                                 threads=threads,
                                 server=server)

    print_ch_subs(ch_filtered, claim_id=claim_id,
                  file=file, fdate=fdate, sep=sep)

    return ch_filtered


def ch_search_latest_d(channel=None, number=4,
                       server="http://localhost:5279"):
    """Search the claims from a channel taken from the wallet file."""
    name, cid = channel["uri"].lstrip("lbry://").split("#")
    f_name = name + "#" + cid[0:3]

    claims = srch_ch.ch_search_latest(channel=f_name, number=number,
                                      server=server)

    return {"channel": f_name,
            "claim_id": cid,
            "claims": claims}


def search_ch_subs_latest(number=4, override=False,
                          shared=True,
                          show_all=True, filtering="valid",
                          valid=True, notifications=True,
                          threads=32,
                          server="http://localhost:5279"):
    """Search the latest claims from our subscribed channels in the wallet.

    Parameters
    ----------
    number: int, optional
        It defaults to 4.
        Number of newest claims to get from each channel in our subscriptions.
        If it's 0, it will be set to 1, otherwise it would search
        all claims which would take a very long time.
        Override the minimum value of 1 by using `override=True`.
    override: bool, optional
        It defaults to `False`.
        If it is `True` then `number` can be set to 0.
    shared: bool, optional
        It defaults to `True`. See `search_ch_subs`.
    show_all: bool, optional
        It defaults to `True`. See `search_ch_subs`.
    filtering: str, optional
        It defaults to `'valid'`. See `search_ch_subs`.
    valid: bool, optional
        It defaults to `True`. See `search_ch_subs`.
    notifications: bool, optional
        It defaults to `True`. See `search_ch_subs`.
    threads: int, optional
        It defaults to 32. See `search_ch_subs`.
    server: str, optional
        It defaults to `'http://localhost:5279'`. See `search_ch_subs`.

    Returns
    -------
    list of dict
        It returns a list of dictionaries where each dictionary corresponds
        to the information of a subscribed channel in the wallet.
        The channels in the wallet are filtered depending
        on the values of `shared`, `show_all`, `filtering`, `valid`,
        and `notifications`.

        Each dictionary has three keys:
        - 'channel': the `'name'` of the channel with three characters
          from the claim ID, like `@channel#123`.
        - 'claim_id': the full 40-digit alphanumeric unique ID
          of the channel.
        - 'claims': list of dict; each dictionary corresponds
          to one of the newest claims of the channel.
          The list has a maximum length of `number`.
          If the channel is invalid, `'claims'` will be `False`,
          meaning that the channel was probably deleted and is no longer
          found online.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    s_time = time.strftime(funcs.TFMT, time.gmtime())

    if number < 0:
        number = 1

    if number == 0 and not override:
        number = 1
        print("Number of claims set to: 1")

    ch_filtered = search_ch_subs(shared=shared,
                                 show_all=show_all, filtering=filtering,
                                 valid=valid, notifications=notifications,
                                 threads=threads,
                                 server=server)

    if not ch_filtered or len(ch_filtered) < 1:
        return False

    ch_latest_claims = []

    # Iterables to be passed to the ThreadPoolExecutor
    n_channels = len(ch_filtered)
    numbers = (number for n in range(n_channels))
    servers = (server for n in range(n_channels))

    if threads:
        with fts.ThreadPoolExecutor(max_workers=threads) as executor:
            # The input must be iterables
            results = executor.map(ch_search_latest_d,
                                   ch_filtered, numbers,
                                   servers)
            print(f"Channel claims search; max threads: {threads}")
            ch_latest_claims = list(results)  # generator to list
    else:
        for channel in ch_filtered:
            claims = ch_search_latest_d(channel=channel, number=number,
                                        server=server)
            ch_latest_claims.append(claims)

    e_time = time.strftime(funcs.TFMT, time.gmtime())

    print()
    print(f"start: {s_time}")
    print(f"end:   {e_time}")

    return ch_latest_claims


def print_ch_subs_latest(ch_latest_claims,
                         claim_id=False, typ=True, title=False,
                         sanitize=False,
                         start=1, end=0,
                         file=None, fdate=False, sep=";"):
    """Print a summary of the channels with their latest published claims."""
    if not ch_latest_claims or len(ch_latest_claims) < 0:
        return False

    n_channels = len(ch_latest_claims)

    out = []

    for num, result in enumerate(ch_latest_claims, start=1):
        if num < start:
            continue
        if end != 0 and num > end:
            break

        channel = result["channel"]
        cid = result["claim_id"]
        claims = result["claims"]

        out.append(f"Channel {num}/{n_channels}, {channel}, {cid}")

        if not claims:
            out.append("  - Invalid channel (removed?)")

            if num < n_channels:
                out.append("")
            continue

        n_claims = len(claims)

        for k, claim in enumerate(claims, start=1):
            value = claim["value"]

            if "release_time" in value:
                rels_time = int(value.get("release_time", 0))
            else:
                rels_time = claim["meta"].get("creation_timestamp", 0)

            rels_time = time.strftime(funcs.TFMTp, time.gmtime(rels_time))

            vtype = claim["value_type"]

            if "stream_type" in value:
                stream_type = value.get("stream_type")
            else:
                stream_type = 8 * "_"

            seconds = 0
            if "video" in value:
                seconds = value["video"].get("duration", 0)
            elif "audio" in value:
                seconds = value["audio"].get("duration", 0)

            mi = seconds // 60
            sec = seconds % 60
            duration = f"{mi:3d}:{sec:02d}"

            size = 0
            if "source" in value:
                size = int(value["source"].get("size", 0))

            size_mb = size / (1024**2)

            name = claim["name"]

            if title:
                name = value.get("title") or name

            if sanitize:
                name = funcs.sanitize_text(name)

            line = f" {k:2d}/{n_claims:2d}" + f"{sep} "
            line += f"{rels_time}" + f"{sep} "

            if claim_id:
                line += claim["claim_id"] + f"{sep} "

            if typ:
                line += f"{vtype:10s}" + f"{sep} "
                line += f"{stream_type:9s}" + f"{sep} "

            line += f"{duration}" + f"{sep} "
            line += f"{size_mb:9.4f} MB" + f"{sep} "
            line += '"' + name + '"'

            out.append(line)

        if num < n_channels:
            out.append("")

    funcs.print_content(out, file=file, fdate=fdate)


def list_ch_subs_latest(number=4, override=False,
                        claim_id=False, typ=True, title=False,
                        sanitize=False,
                        shared=True,
                        show_all=True, filtering="valid",
                        valid=True, notifications=False,
                        threads=32,
                        start=1, end=0,
                        file=None, fdate=False, sep=";",
                        server="http://localhost:5279"):
    """List the latest claims from our subscribed channels.

    Parameters
    ----------
    number: int, optional
        It defaults to 4.
        Number of newest claims to get from each channel in our subscriptions.
        If it's 0, it will be set to 1, otherwise it would search
        all claims which would take a very long time.
        Override the minimum value of 1 by using `override=True`.
    override: bool, optional
        It defaults to `False`.
        If it is `True` then `number` can be set to 0.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the `'claim_id'` of the claims
        of the channel.
    typ: bool, optional
        It defaults to `True` in which case it will print the claim type,
        and stream type (if any) of the claims of the channel.
    title: bool, optional
        It defaults to `False` in which case the claim `'name'`
        will be printed.
        If it is `True`, the claim `'title'` will be printed instead.
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the name or title of the claim.
        If it is `True` it will remove these unicode characters.
        This option requires the `emoji` package to be installed.
    shared: bool, optional
        It defaults to `True`, in which case it uses the shared database
        synchronized with Odysee online.
        If it is `False` it will use only the local database
        to `lbrynet`, for example, used by the LBRY Desktop application.
    show_all: bool, optional
        It defaults to `True`, in which case all followed channels
        will be printed, regardless of `filtering`, `valid`,
        or `notifications`.
        If it is `False` then we can control what channels to show
        with `filtering`, `valid`, or `notifications`.
    filtering: str, optional
        It defaults to `'valid'`. It is the type of filtering that
        will be done as long as `show_all=False`.
        It can be `'valid'` (depending on the value of `valid` parameter),
        `'notifications'` (depending on the value of `notifications`),
        or `'both'` (depending on the values of `valid` and `notifications`).
        If `'both'`, the list of channels will be filtered by `valid` first,
        and then by `notifications`.
    valid: bool, optional
        It defaults to `True` in which case only the channels that resolve
        online will be returned.
        If it is `False` it will return only those channels that no longer
        resolve online.
        This parameter only works when `show_all=False`
        and `filtering='valid'` or `'both'`.
    notifications: bool, optional
        It defaults to `False` in which case only the channels
        that have notifications disabled will be returned.
        If it is `True` it will return only those channels
        that have notifications enabled.
        This parameter only works when `show_all=False`
        and `filtering='notifications'` or `'both'`.
    threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to resolve channels
        online, meaning that many channels will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
    start: int, optional
        It defaults to 1.
        Show claims starting from this index in the list of items.
    end: int, optional
        It defaults to 0.
        Show claims until and including this index in the list of items.
        If it is 0, it is the same as the last index in the list.
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
        It returns a list of dictionaries where each dictionary corresponds
        to the information of a subscribed channel in the wallet.
        The channels in the wallet are filtered depending
        on the values of `shared`, `show_all`, `filtering`, `valid`,
        and `notifications`.

        Each dictionary has three keys:
        - 'channel': the `'name'` of the channel with three characters
          from the claim ID, like `@channel#123`.
        - 'claim_id': the full 40-digit alphanumeric unique ID
          of the channel.
        - 'claims': list of dict; each dictionary corresponds
          to one of the newest claims of the channel.
          The list has a maximum length of `number`.
          If the channel is invalid, `'claims'` will be `False`,
          meaning that the channel was probably deleted and is no longer
          found online.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    ch_latest_claims = search_ch_subs_latest(number=number,
                                             override=override,
                                             shared=shared,
                                             show_all=show_all,
                                             filtering=filtering,
                                             valid=valid,
                                             notifications=notifications,
                                             threads=threads,
                                             server=server)

    print()
    print_ch_subs_latest(ch_latest_claims,
                         claim_id=claim_id, typ=typ, title=title,
                         sanitize=sanitize,
                         start=start, end=end,
                         file=file, fdate=fdate, sep=sep)

    return ch_latest_claims


if __name__ == "__main__":
    list_ch_subs()
    print()
    list_ch_subs_latest(number=1)
