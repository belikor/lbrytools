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
"""Functions to get published claims in the LBRY network."""
import concurrent.futures as fts
import time

import requests

import lbrytools.funcs as funcs
import lbrytools.search_utils as sutils
import lbrytools.accounts as accnts


def find_ch_account(ch_address, print_msg=False,
                    wallet_id="default_wallet",
                    server="http://localhost:5279"):
    """Find an address in one of the channel subaddresses."""
    wallet_info = accnts.get_wallet_info(wallet_id=wallet_id,
                                         server=server)
    accounts = wallet_info["accounts"]

    found = {"account": "",
             "account_name": "",
             "generator": ""}

    for num, account in enumerate(accounts, start=1):
        acc_id = account["id"]
        acc_name = account["name"]
        acc_gen = account["generator"]
        acc_addresses = account["addresses"]

        for add in acc_addresses:
            if ch_address in add["address"]:
                found = {"account": acc_id,
                         "account_name": acc_name,
                         "generator": acc_gen}

                if print_msg:
                    print(f"Channel address {ch_address} "
                          f"found in acc. {num}, "
                          f"{acc_id}, {acc_name}, {acc_gen}")

    return found


def get_channels(wallet_id="default_wallet",
                 is_spent=False, reverse=False,
                 threads=16,
                 server="http://localhost:5279"):
    """Get all channels and check to which account they belong.

    Parameters
    ----------
    wallet_id: str, optional
        It defaults to 'default_wallet', in which case it will search
        the accounts created in the default wallet created by `lbrynet`.
    is_spent: bool, optional
        It defaults to `False`, in which case it will show
        active channel claims with a transaction that hasn't been spent.
        If it is `True` it will get the channel claims with transactions
        that have already been spent. This means it will show
        some channels that are expired or no longer exist.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the output list.
        If it is `True` newer claims are at the beginning of the list.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        Each element in the list is a dictionary with the information
        corresponding to the output of `channel_list`.
        Each dictionary is augmented by three keys:
        - 'account': the 34-character ID of the account
          that created the channel.
        - 'account_name': the name assigned to this account.
        - 'generator': the type of account, either 'deterministic-chain'
          or 'single-address'. Odysee accounts are single-address type.
    False
        If there is a problem, such as non-existing `wallet_id`,
        it will return `False`.
    """
    msg = {"method": "channel_list",
           "params": {"page_size": 1000,
                      "resolve": True,
                      "wallet_id": wallet_id}}

    if is_spent:
        msg["params"]["is_spent"] = True

    output = requests.post(server, json=msg).json()
    if "error" in output:
        name = output["error"]["data"]["name"]
        mess = output["error"].get("message", "No error message")
        print(f">>> {name}: {mess}")
        return False

    channels = output["result"]["items"]
    n_channels = len(channels)

    if not n_channels:
        return False

    # Order channels by 'creation_timestamp'.
    # For spent transactions, 'creation_timestamp' doesn't exist
    # so we just use 'timestamp'.
    for ch in channels:
        if "error" in ch["meta"]:
            ch["meta"]["creation_timestamp"] = ch["timestamp"]

    channels = sorted(channels,
                      key=lambda ch: int(ch["meta"]["creation_timestamp"]),
                      reverse=reverse)

    # Iterables to be passed to the ThreadPoolExecutor
    ch_addresses = (ch["address"] for ch in channels)
    falses = (False for n in range(n_channels))
    wallet_ids = (wallet_id for n in range(n_channels))
    servers = (server for n in range(n_channels))

    if threads:
        with fts.ThreadPoolExecutor(max_workers=threads) as executor:
            # The input must be iterables
            results = executor.map(find_ch_account,
                                   ch_addresses, falses, wallet_ids,
                                   servers)

            found_chs = list(results)  # generator to list

        # Augment the original dictionary with the information
        # on the account which published this channel
        for pair in zip(channels, found_chs):
            ch = pair[0]
            found = pair[1]
            ch.update(found)
    else:
        for ch in channels:
            found = find_ch_account(ch["address"], wallet_id=wallet_id,
                                    server=server)
            ch.update(found)

    return channels


def print_ch_summary(channels,
                     file=None, fdate=False):
    """Print a summary paragraph of the channels."""
    t_n_claims = 0
    t_b_amount = 0
    t_e_amount = 0

    for ch in channels:
        n_claims = ch["meta"].get("claims_in_channel", 0)
        amount = float(ch["amount"])
        e_amount = float(ch["meta"].get("effective_amount", 0))

        t_n_claims += n_claims
        t_b_amount += amount
        t_e_amount += e_amount

    out = [40 * "-",
           f"Total claims in channels: {t_n_claims}",
           f"Total base stake on all channels: {t_b_amount:14.8f}",
           f"Total stake on all channels:      {t_e_amount:14.8f}"]

    funcs.print_content(out, file=file, fdate=fdate)

    return {"n_claims": t_n_claims,
            "base_amount": t_b_amount,
            "total_amount": t_e_amount}


def print_channels(channels,
                   updates=False, claim_id=False, addresses=True,
                   accounts=False, amounts=True,
                   sanitize=False,
                   file=None, fdate=False, sep=";"):
    """Print the list of channels obtained from get_channels."""
    n_channels = len(channels)

    out = []

    for num, ch in enumerate(channels, start=1):
        meta = ch["meta"]
        value = ch["value"]

        cid = ch["claim_id"]
        address = ch["address"]

        # name = ch["name"]
        name = ch["canonical_url"].split("lbry://")[1]

        if sanitize:
            name = funcs.sanitize_text(name)
        name = '"' + name + '"'

        timestamp = ch["timestamp"]
        timestamp = time.strftime("%Y-%m-%d_%H:%M:%S%z",
                                  time.localtime(timestamp))

        title = value.get("title", 10 * "_")
        if sanitize:
            title = funcs.sanitize_text(title)
        title = '"' + title + '"'

        claim_op = ch["claim_op"]
        amount = float(ch["amount"])

        c_timestamp = meta.get("creation_timestamp", 0)
        c_timestamp = time.strftime("%Y-%m-%d_%H:%M:%S%z",
                                    time.localtime(c_timestamp))
        if "error" in meta:
            c_timestamp = 24 * "_"

        n_claims = meta.get("claims_in_channel", 0)
        e_amount = float(meta.get("effective_amount", 0))

        ch_acc = ch["account"]

        line = f"{num:2d}/{n_channels:2d}" + f"{sep} "
        line += f"{c_timestamp}" + f"{sep} "

        if updates:
            line += f"{claim_op}" + f"{sep} "
            line += f"{timestamp}" + f"{sep} "

        if claim_id:
            line += f"{cid}" + f"{sep} "

        if addresses:
            line += f"{address}" + f"{sep} "

        if accounts:
            line += f"in {ch_acc}" + f"{sep} "

        if amounts:
            line += f"{amount:14.8f}" + f"{sep} "
            line += f"{e_amount:14.8f}" + f"{sep} "

        line += f"c.{n_claims:4d}" + f"{sep} "
        line += f"{name:48s}" + f"{sep} "
        line += f"{title}"

        out.append(line)

    funcs.print_content(out, file=file, fdate=fdate)


def list_channels(wallet_id="default_wallet", is_spent=False,
                  updates=False, claim_id=False, addresses=True,
                  accounts=False, amounts=True,
                  reverse=False, sanitize=False,
                  file=None, fdate=False, sep=";",
                  server="http://localhost:5279"):
    """List channels defined in the wallet.

    Parameters
    ----------
    wallet_id: str, optional
        It defaults to 'default_wallet', in which case it will search
        the accounts created in the default wallet created by `lbrynet`.
    is_spent: bool, optional
        It defaults to `False`, in which case it will show
        active channels with a transaction that hasn't been spent.
        If it is `True` it will get the channel claims with transactions
        that have already been spent. This means it will show
        some channels that are expired or no longer exist.
    updates: bool, optional
        It defaults to `False`.
        If it is `True` it will print the last time the channels claims were
        created or updated.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim ID of the channels.
    addresses: bool, optional
        It defaults to `True`, in which case it prints the 34-character
        address that created the channel.
    accounts: bool, optional
        It defaults to `False`.
        If it is `True` it will print the 34-character ID of the account
        that created the channel.
    amounts: bool, optional
        It defaults to `True`, in which case it prints two quantities,
        the amount of LBC that is originally staked on the channel claim,
        and the total amount, which may include tips and supports
        by other people.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the output list.
        If it is `True` newer claims are at the beginning of the list.
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the name and title of the claim and channel.
        If it is `True` it will remove these unicode characters.
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
        There are two keys
        - 'summary': a dictionary with three keys 'n_claims',
          'base_amount', and 'total_amount', indicating the number of claims
          in all channels, the total base staked amount in all channels,
          and the total stake in all channels.
          The claims published anonymously, that is, without a channel
          are not taken into account.
        - 'channels': a list of dict.
          Each element in the list is a dictionary with the information
          corresponding to the output of `channel_list`.
          Each dictionary is augmented by three keys:
          - 'account': the 34-character ID of the account
            that created the channel.
          - 'account_name': the name assigned to this account.
          - 'generator': the type of account, either 'deterministic-chain'
            or 'single-address'. Odysee accounts are single-address type.
    False
        If there is a problem, such as non-existing `wallet_id`,
        it will return `False`.
    """
    print("Channels in the wallet")
    print(80 * "-")

    if not funcs.server_exists(server=server):
        return False

    channels = get_channels(wallet_id=wallet_id,
                            is_spent=is_spent, reverse=reverse,
                            server=server)

    if not channels:
        return False

    print_channels(channels,
                   updates=updates, claim_id=claim_id, addresses=addresses,
                   accounts=accounts, amounts=amounts,
                   sanitize=sanitize,
                   file=file, fdate=fdate, sep=sep)

    summary = print_ch_summary(channels, file=None, fdate=False)

    return {"channels": channels,
            "summary": summary}


def get_channel_claims(wallet_id="default_wallet",
                       is_spent=False, reverse=False,
                       server="http://localhost:5279"):
    """Get all published claims by channel in the wallet."""
    ch_claims = []

    channels = get_channels(wallet_id=wallet_id,
                            is_spent=False, reverse=False,
                            server=server)

    if not channels:
        return ch_claims

    for channel in channels:
        msg = {"method": "claim_list",
               "params": {"wallet_id": wallet_id,
                          "page_size": 99000,
                          "resolve": True,
                          "channel_id": channel["claim_id"]}}

        if is_spent:
            msg["params"]["is_spent"] = True

        output = requests.post(server, json=msg).json()
        if "error" in output:
            name = output["error"]["data"]["name"]
            mess = output["error"].get("message", "No error message")
            print(f">>> {name}: {mess}")
            continue

        claims = output["result"]["items"]

        # Order the claims by 'release_time' which exists for streams
        # (video, audio, documents).
        # For other claims (reposts, collections) it will use
        # 'creation_timestamp'. For spent transactions, 'creation_timestamp'
        # doesn't exist so we just use 'timestamp'.
        for claim in claims:
            if "relase_time" not in claim["value"]:
                if "creation_timestamp" in claim["meta"]:
                    claim["value"]["release_time"] = \
                        claim["meta"]["creation_timestamp"]
                else:
                    claim["value"]["release_time"] = claim["timestamp"]

        claims = sorted(claims,
                        key=lambda c: int(c["value"]["release_time"]),
                        reverse=reverse)

        ds = sutils.downloadable_size(claims, local=False, print_msg=False)

        ch_name = channel["canonical_url"].split("lbry://")[1]

        ch_claims.append({"name": ch_name,
                          "id": channel["claim_id"],
                          "address": channel["address"],
                          "claims": claims,
                          "size": ds["size"],
                          "duration": ds["duration"]})

    return ch_claims


def get_anon_claims(wallet_id="default_wallet",
                    is_spent=False, reverse=False,
                    server="http://localhost:5279"):
    """Get all published claims that are not published by a channel."""
    msg = {"method": "claim_list",
           "params": {"wallet_id": wallet_id,
                      "page_size": 99000,
                      "resolve": True}}
    if is_spent:
        msg["params"]["is_spent"] = True

    output = requests.post(server, json=msg).json()
    if "error" in output:
        name = output["error"]["data"]["name"]
        mess = output["error"].get("message", "No error message")
        print(f">>> {name}: {mess}")
        return False

    claims = output["result"]["items"]

    # Only pick claims without a channel
    anon_claims = []

    for claim in claims:
        if ("signing_channel" not in claim
                and claim["value_type"] not in "channel"):
            # Order the claims by 'release_time' which exists for streams
            # (video, audio, documents).
            # For other claims (reposts, collections) it will use
            # 'creation_timestamp'. For spent transactions,
            # 'creation_timestamp' doesn't exist so we just use 'timestamp'.
            if "relase_time" not in claim["value"]:
                if "creation_timestamp" in claim["meta"]:
                    claim["value"]["release_time"] = \
                        claim["meta"]["creation_timestamp"]
                else:
                    claim["value"]["release_time"] = claim["timestamp"]
            anon_claims.append(claim)

    if not anon_claims:
        return False

    anon_claims = sorted(anon_claims,
                         key=lambda c: int(c["value"]["release_time"]),
                         reverse=reverse)

    anon_ds = sutils.downloadable_size(anon_claims, local=False,
                                       print_msg=False)

    unknown = {"name": "_Unknown_",
               "id": None,
               "address": None,
               "claims": anon_claims,
               "size": anon_ds["size"],
               "duration": anon_ds["duration"]}

    return unknown


def get_claims(wallet_id="default_wallet",
               is_spent=False, reverse=False,
               server="http://localhost:5279"):
    """Get all claims published by channels or published anonymously.

    Parameters
    ----------
    wallet_id: str, optional
        It defaults to 'default_wallet', in which case it will search
        the accounts created in the default wallet created by `lbrynet`.
    is_spent: bool, optional
        It defaults to `False`, in which case it will show
        active claims with a transaction that hasn't been spent.
        If it is `True` it will get the claims with transactions
        that have already been spent. This means it will show
        some claims that are expired or no longer exist.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the output list.
        If it is `True` newer claims are at the beginning of the list.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    list of dict
        Each element in the list is a dictionary with the information
        corresponding to a channel and its claims.
        Each dictionary contains 6 keys:
        - 'name': name of the channel starting with '@'.
        - 'id': claim ID of the channel (40-character string).
        - 'address': 34-character address that created the channel claim.
        - 'claims': list of dictionaries corresponding to the output
          of `claim_list`, indicating the claims published by this channel.
        - 'size': total size of all claims in the channel, in bytes.
        - 'duration': total duration of all claims in the channel, in seconds.

        There may be one special dictionary with 'name' being '_Unknown_',
        that is, not starting with '@'. This dictionary has the claims
        that were published anonymously, that is, not under any channel.
        For this dictionary 'id' and 'address' will be `None`.
    False
        If there is a problem, such as non-existing `wallet_id`,
        it will return `False`.
    """
    ch_claims = get_channel_claims(wallet_id=wallet_id,
                                   is_spent=is_spent, reverse=reverse,
                                   server=server)

    unknown = get_anon_claims(wallet_id=wallet_id,
                              is_spent=is_spent, reverse=reverse,
                              server=server)

    if unknown:
        ch_claims.append(unknown)

    return ch_claims


def print_s_claims(claims, output=None,
                   updates=False, claim_id=False, addresses=False,
                   typ=False, amounts=True, ch_name=False,
                   title=False, sanitize=False,
                   start=1, end=0,
                   reverse=False,
                   sep=";"):
    """Prepare output list in order to print the claims."""
    if not output:
        output = []

    if reverse:
        claims.reverse()

    n_claims = len(claims)
    if n_claims < 1:
        output.append("   No claims")

    for num, claim in enumerate(claims, start=1):
        if num < start:
            continue
        if end != 0 and num > end:
            break

        meta = claim["meta"]
        value = claim["value"]

        cid = claim["claim_id"]
        ad = claim["address"]

        name = claim["name"]

        if title and "title" in value:
            name = value["title"]

        if sanitize:
            name = funcs.sanitize_text(name)
        name = '"' + name + '"'

        claim_op = claim["claim_op"]
        tstamp = claim["timestamp"]
        timestamp = time.strftime("%Y-%m-%d_%H:%M:%S%z",
                                  time.localtime(tstamp))

        vtype = claim["value_type"]
        if "stream_type" in value:
            stream_type = value.get("stream_type", 8 * "_")
        else:
            stream_type = 8 * "_"

        if "source" in value:
            mtype = value["source"].get("media_type", 14 * "_")
        else:
            mtype = 14 * "_"

        if "signing_channel" in claim:
            if "canonical_url" in claim["signing_channel"]:
                channel = claim["signing_channel"]["canonical_url"]
                channel = channel.lstrip("lbry://")
            else:
                channel = claim["signing_channel"]["permanent_url"]
                _ch, _id = channel.split("#")
                _ch = _ch.lstrip("lbry://")
                channel = _ch + "#" + _id[0:3]

            if sanitize:
                channel = funcs.sanitize_text(channel)
        else:
            channel = 14 * "_"

        if sanitize:
            channel = funcs.sanitize_text(channel)

        length_s = 0
        rem_s = 0
        rem_min = 0

        if "video" in value and "duration" in value["video"]:
            length_s = value["video"]["duration"]
        if "audio" in value and "duration" in value["audio"]:
            length_s = value["audio"]["duration"]

        rem_s = length_s % 60
        rem_min = length_s // 60

        size = 0
        if "source" in value and "size" in value["source"]:
            size = float(value["source"]["size"])
            size = size/(1024**2)  # to MB

        amount = float(claim["amount"])
        t_amount = float(meta.get("effective_amount", 0))
        rep = meta.get("reposted", 0)
        # creation = meta.get("creation_height", 0)
        # height = claim["height"]

        rels_time = int(value.get("release_time", 0))
        rels_time = time.strftime("%Y-%m-%d_%H:%M:%S%z",
                                  time.localtime(rels_time))

        line = f"{num:4d}/{n_claims:4d}" + f"{sep} "
        line += rels_time + f"{sep} "

        if updates:
            line += f"{claim_op}" + f"{sep} "
            line += f"{timestamp}" + f"{sep} "

        if claim_id:
            line += f"{cid}" + f"{sep} "

        if addresses:
            line += f"{ad}" + f"{sep} "

        if typ:
            line += f"{vtype:10s}" + f"{sep} "
            line += f"{stream_type:9s}" + f"{sep} "
            line += f"{mtype:17s}" + f"{sep} "

        if amounts:
            line += f"{amount:14.8f}" + f"{sep} "
            line += f"{t_amount:14.8f}" + f"{sep} "

        if ch_name:
            line += f"{channel}" + f"{sep} "

        line += f"r.{rep:3d}" + f"{sep} "
        line += f"{rem_min:3d}:{rem_s:02d}" + f"{sep} "
        line += f"{size:9.4f} MB" + f"{sep} "

        line += f"{name}"
        output.append(line)

    return output


def print_claims(ch_claims,
                 updates=False, claim_id=False, addresses=False,
                 typ=False, amounts=True, ch_name=False,
                 title=False, sanitize=False,
                 file=None, fdate=False, sep=";"):
    """Print the list of channels and claims."""
    n_chs = len(ch_claims)

    out = []
    t_n_claims = 0
    t_size = 0
    t_duration = 0

    t_n_an_claims = 0
    t_an_size = 0
    t_an_duration = 0
    anon_exists = False
    is_anon = False

    for ch_claim in ch_claims:
        if ch_claim["name"] in "_Unknown_":
            anon_exists = True
            n_chs = n_chs - 1

    for n_ch, ch_claim in enumerate(ch_claims, start=1):
        chan_name = ch_claim["name"]

        if chan_name in "_Unknown_":
            is_anon = True

        if sanitize:
            chan_name = funcs.sanitize_text(chan_name)

        chan_name = '"' + chan_name + '"'

        chan_id = ch_claim["id"]
        chan_add = ch_claim["address"]
        chan_size = ch_claim["size"]
        chan_duration = ch_claim["duration"]

        claims = ch_claim["claims"]

        if is_anon:
            t_n_an_claims += len(claims)
            t_an_size += chan_size
            t_an_duration += chan_duration
        else:
            t_n_claims += len(claims)
            t_size += chan_size
            t_duration += chan_duration

        GB = chan_size / (1024**3)  # to GiB
        hrs = chan_duration / 3600
        days = hrs / 24

        hr = chan_duration // 3600
        mi = (chan_duration % 3600) // 60
        sec = (chan_duration % 3600) % 60

        if is_anon:
            line = ""
        else:
            line = f"{n_ch:2d}/{n_chs:2d}" + f"{sep} "

        line += f"{chan_name}" + f"{sep} "
        line += f"{chan_id}" + f"{sep} "
        line += f"{chan_add}" + f"{sep} "
        line += f"{GB:.4f} GiB" + f"{sep} "
        line += f"{hr} h {mi} min {sec} s, or {days:.4f} days"
        out.append(line)

        out = print_s_claims(claims, output=out,
                             updates=updates,
                             claim_id=claim_id, addresses=addresses,
                             typ=typ, amounts=amounts, ch_name=ch_name,
                             title=title, sanitize=sanitize,
                             sep=sep)

        if not is_anon:
            if n_ch < n_chs or anon_exists:
                out.append("")

    funcs.print_content(out, file=file, fdate=fdate)


def print_claims_summary(ch_claims,
                         file=None, fdate=False):
    """Print a summary paragraph of the channel claims."""
    n_chs = len(ch_claims)

    t_n_claims = 0
    t_size = 0
    t_duration = 0

    t_n_anon_claims = 0
    t_anon_size = 0
    t_anon_duration = 0
    is_anon = False

    for ch_claim in ch_claims:
        if ch_claim["name"] in "_Unknown_":
            n_chs = n_chs - 1

    for ch_claim in ch_claims:
        if ch_claim["name"] in "_Unknown_":
            is_anon = True

        chan_size = ch_claim["size"]
        chan_duration = ch_claim["duration"]
        claims = ch_claim["claims"]

        if is_anon:
            t_n_anon_claims += len(claims)
            t_anon_size += chan_size
            t_anon_duration += chan_duration
        else:
            t_n_claims += len(claims)
            t_size += chan_size
            t_duration += chan_duration

    t_GB = t_size / (1024**3)  # to GiB
    t_hrs = t_duration / 3600
    t_days = t_hrs / 24

    t_hr = t_duration // 3600
    t_mi = (t_duration % 3600) // 60
    t_sec = (t_duration % 3600) % 60

    t_anon_GB = t_anon_size / (1024**3)  # to GiB
    t_anon_hrs = t_anon_duration / 3600
    t_anon_days = t_anon_hrs / 24

    t_anon_hr = t_anon_duration // 3600
    t_anon_mi = (t_anon_duration % 3600) // 60
    t_anon_sec = (t_anon_duration % 3600) % 60

    out1 = [40 * "-",
            f"Total unique channels: {n_chs}",
            f"Total claims in channels: {t_n_claims}",
            f"Total download size: {t_GB:.4f} GiB",
            f"Total duration: {t_hr} h {t_mi} min {t_sec} s, "
            f"or {t_days:.4f} days"]

    out2 = [40 * "-",
            f"Anonymous unique claims: {t_n_anon_claims}",
            f"Total download size of anonymous claims: {t_anon_GB:.4f} GiB",
            "Total duration of anonymous claims: "
            f"{t_anon_hr} h {t_anon_mi} min {t_anon_sec} s, "
            f"or {t_anon_days:.4f} days"]

    out = []

    if t_n_claims > 0:
        out += out1

    if t_n_anon_claims > 0:
        out += out2

    funcs.print_content(out, file=file, fdate=fdate)

    return {"n_channels": n_chs,
            "n_ch_claims": t_n_claims,
            "chs_size": t_GB,
            "chs_hr": t_hr,
            "chs_min": t_mi,
            "chs_sec": t_sec,
            "chs_days": t_days,
            "n_anon_claims": t_n_anon_claims,
            "anon_size": t_anon_GB,
            "anon_hr": t_anon_hr,
            "anon_min": t_anon_mi,
            "anon_sec": t_anon_sec,
            "anon_days": t_anon_days}


def list_claims(wallet_id="default_wallet", is_spent=False,
                channel=None, channel_id=None, anon=False,
                updates=False, claim_id=False, addresses=False,
                typ=False, amounts=True, ch_name=False,
                title=False,
                reverse=False, sanitize=False,
                file=None, fdate=False, sep=";",
                server="http://localhost:5279"):
    """List all claims published by channels or published anonymously.

    Parameters
    ----------
    wallet_id: str, optional
        It defaults to 'default_wallet', in which case it will search
        the accounts created in the default wallet created by `lbrynet`.
    is_spent: bool, optional
        It defaults to `False`, in which case it will show
        active claims with a transaction that hasn't been spent.
        If it is `True` it will get the claims with transactions
        that have already been spent. This mean it will show
        claims that are expired or no longer exist.
    channel: str, optional
        It defaults to `None` in which case it will print
        the claims of all channels, as long as `channel_id` is also `None`.
        If it is the name of one of our channels, it will display the claims
        only for this channel.
    channel_id: str, optional
        It defaults to `None` in which case it will print
        the claims of all channels, as long as `channel` is also `None`.
        If it is a 40-character claim ID, it will display the claims
        only for the channel with this claim ID.
    anon: bool, optional
        It defaults to `False`.
        If it is `True` it will only print our claims published without
        a channel, that is, that were published anonymously.
    updates: bool, optional
        It defaults to `False`.
        If it is `True` it will print the last time the claims were
        created or updated.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim ID of the claims.
    addresses: bool, optional
        It defaults to `False`.
        If it is `True` it will print the 34-character address
        that created the claim.
    typ: bool, optional
        It defaults to `False`.
        If it is `True` it will print the type of claim, the type of stream,
        and the media type, if any.
    amounts: bool, optional
        It defaults to `True`, in which case it prints two quantities,
        the amount of LBC that is originally staked on the claim,
        and the total amount, which may include tips and supports
        by other people.
    ch_name: bool, optional
        It defaults to `False`.
        If it is `True` it will print the channel that published the claims.
    title: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim title instead of
        the claim name.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the output list.
        If it is `True` newer claims are at the beginning of the list.
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the name and title of the claim and channel.
        If it is `True` it will remove these unicode characters.
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
        There are two keys
        - 'summary': a dictionary with 13 keys 'n_channels' (number
          of channels), 'n_ch_claims' (number of claims in channels),
          'chs_size' (GB), 'chs_hr' (hours), 'chs_min' (minutes),
          'chs_sec' (seconds), 'chs_days' (days),
          'n_anon_claims' (number of anonymous claims), and similarly
          'anon_size', 'anon_hr', 'anon_min', 'anon_sec', and 'anon_days'.
        - 'ch_claims': a list of dict.
          Each element in the list is a dictionary with the information
          corresponding to a channel and its claims.
          Each dictionary contains 6 keys:
            - 'name': name of the channel starting with '@'.
            - 'id': claim ID of the channel (40-character string).
            - 'address': 34-character address that created the channel claim.
            - 'claims': list of dictionaries corresponding to the output
              of `claim_list`, indicating the claims published by this channel.
              If there are no claims, the list will be empty.
            - 'size': total size of all claims in the channel, in bytes.
            - 'duration': total duration of all claims in the channel,
              in seconds.

          If `channel` or `channel_id` were used to find a channel,
          or `anon=True`, the list will only contain at most one dictionary.

          If `anon=True` the single dictionary in the list will contain
          the information of the claims that were published anonymously,
          that is, not under any channel.
          For this dictionary 'name' will be '_Unknown_' (it will not start
          with '@'), and 'id' and 'address' will be `None`.
    False
        If there is a problem, such as non-existing `wallet_id`,
        it will return `False`.
    """
    print("Claims in the wallet")
    print(80 * "-")

    if not funcs.server_exists(server=server):
        return False

    ch_claims = get_claims(wallet_id=wallet_id,
                           is_spent=is_spent, reverse=reverse,
                           server=server)

    if not ch_claims:
        return False

    found = False

    # Filter the list of channels by the entered name or claim ID
    if anon:
        channel = "_Unknown_"

    if channel or channel_id:
        if channel:
            if channel in "_Unknown_":
                # Special name not starting with @ for anonymous claims
                anon = True
            elif not channel.startswith("@"):
                channel = "@" + channel

        for ch in ch_claims:
            chan_name = ch["name"]
            chan_id = ch["id"]
            if (channel and channel in chan_name
                    or channel_id and channel_id in chan_id):
                print(f"Found match")
                ch_claims = [ch]
                found = True
                break

        if not found:
            if anon:
                print(f"No anonymous claims")
            else:
                print(f'Not found: "{channel}", "{channel_id}"')
            return False

    print_claims(ch_claims,
                 updates=updates, claim_id=claim_id, addresses=addresses,
                 typ=typ, amounts=amounts, ch_name=ch_name,
                 title=title, sanitize=sanitize,
                 file=file, fdate=fdate, sep=sep)

    summary = print_claims_summary(ch_claims, file=None, fdate=False)

    return {"ch_claims": ch_claims,
            "summary": summary}
