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
"""Functions to get the list of published channels in the LBRY network."""
import concurrent.futures as fts
import time

import requests

import lbrytools.funcs as funcs
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

        create_time = meta.get("creation_timestamp", 0)
        create_time = time.strftime(funcs.TFMTp, time.gmtime(create_time))

        if "error" in meta:
            create_time = 24 * "_"

        claim_op = ch["claim_op"]
        timestamp = ch["timestamp"]
        timestamp = time.strftime(funcs.TFMTp, time.gmtime(timestamp))

        ch_claim_id = ch["claim_id"]
        address = ch["address"]
        ch_acc = ch["account"]
        ch_gen = ch["generator"]
        ch_gen = f"{ch_gen:<19}"
        ch_acc_name = ch["account_name"]
        ch_acc_name = f"{ch_acc_name:<12}"

        amount = float(ch["amount"])
        e_amount = float(meta.get("effective_amount", 0))
        n_claims = meta.get("claims_in_channel", 0)

        name = ch["canonical_url"].split("lbry://")[1]
        name = '"' + name + '"'

        title = value.get("title", "(no title)")
        title = '"' + title + '"'

        if sanitize:
            name = funcs.sanitize_text(name)
            title = funcs.sanitize_text(title)

        line = f"{num:2d}/{n_channels:2d}" + f"{sep} "
        line += f"{create_time}" + f"{sep} "

        if updates:
            line += f"{claim_op}" + f"{sep} "
            line += f"{timestamp}" + f"{sep} "

        if claim_id:
            line += f"{ch_claim_id}" + f"{sep} "

        if addresses:
            line += f"add. {address}" + f"{sep} "

        if accounts:
            line += f"acc. {ch_acc}" + f"{sep} "
            line += f"{ch_gen}" + f"{sep} "
            line += f"{ch_acc_name}" + f"{sep} "

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
