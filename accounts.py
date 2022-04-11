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
"""Functions to display account and wallet information."""
import requests

import lbrytools.funcs as funcs


def get_wallets(wallet_id=None,
                server="http://localhost:5279"):
    """Get all wallets or a specific wallet given a wallet_id."""
    msg = {"method": "wallet_list",
           "params": {"page_size": 1000}}

    if wallet_id:
        msg["params"]["wallet_id"] = wallet_id

    output = requests.post(server, json=msg).json()
    if "error" in output:
        name = output["error"]["data"]["name"]
        mess = output["error"].get("message", "No error message")
        print(f">>> {name}: {mess}")
        return False

    items = output["result"]["items"]

    wallets = []

    for w in items:
        wallets.append({"id": w["id"],
                        "name": w["name"]})

    return wallets


def get_bal_wallet(wallet_id="default_wallet",
                   server="http://localhost:5279"):
    """Get balance of a single wallet_id."""
    wallets = get_wallets(wallet_id=wallet_id, server=server)

    if not wallets:
        return False

    wallet = wallets[0]
    msg = {"method": "wallet_balance",
           "params": {"wallet_id": wallet["id"]}}

    output = requests.post(server, json=msg).json()
    if "error" in output:
        name = output["error"]["data"]["name"]
        mess = output["error"].get("message", "No error message")
        print(f">>> {name}: {mess}")
        return False

    result = output["result"]

    total = float(result["total"])
    available = float(result["available"])
    reserved = float(result["reserved"])

    claims = float(result["reserved_subtotals"]["claims"])
    supports = float(result["reserved_subtotals"]["supports"])
    tips = float(result["reserved_subtotals"]["tips"])

    balance = {"id": wallet["id"],
               "name": wallet["name"],
               "total": total,
               "available": available,
               "reserved": reserved,
               "claims": claims,
               "supports": supports,
               "tips": tips}

    return balance


def get_accounts(wallet_id="default_wallet",
                 server="http://localhost:5279"):
    """Get accounts of the default wallet or the given wallet_id."""
    msg = {"method": "account_list",
           "params": {"page_size": 1000}}

    if wallet_id:
        msg["params"]["wallet_id"] = wallet_id

    output = requests.post(server, json=msg).json()
    if "error" in output:
        name = output["error"]["data"]["name"]
        mess = output["error"].get("message", "No error message")
        print(f">>> {name}: {mess}")
        return False

    items = output["result"]["items"]

    accounts = []
    for item in items:
        ID = item["id"]
        name = item["name"]
        gen = item["address_generator"]["name"]

        account = {"id": ID,
                   "name": name,
                   "generator": gen}

        msg2 = {"method": "account_balance",
                "params": {"account_id": ID}}

        output = requests.post(server, json=msg2).json()
        if "error" in output:
            continue

        res2 = output["result"]

        total = float(res2["total"])
        available = float(res2["available"])
        reserved = float(res2["reserved"])

        claims = float(res2["reserved_subtotals"]["claims"])
        supports = float(res2["reserved_subtotals"]["supports"])
        tips = float(res2["reserved_subtotals"]["tips"])

        balance = {"total": total,
                   "available": available,
                   "reserved": reserved,
                   "claims": claims,
                   "supports": supports,
                   "tips": tips}

        msg3 = {"method": "address_list",
                "params": {"account_id": ID,
                           "page_size": 99000}}

        output = requests.post(server, json=msg3).json()
        if "error" in output:
            continue

        addr_items = output["result"]["items"]

        sub_addresses = []
        for n_ad, sub_address in enumerate(addr_items, start=1):
            address = sub_address["address"]
            used = sub_address["used_times"]

            if used < 1:
                continue

            sub_addresses.append({"n": n_ad,
                                  "address": address,
                                  "used_times": used})

        # Add the other keys into the main account dictionary
        account.update(balance)
        account["addresses"] = sub_addresses

        accounts.append(account)

    return accounts


def get_wallet_info(wallet_id="default_wallet",
                    server="http://localhost:5279"):
    """Get the wallet info together with the accounts in that wallet.

    Parameters
    ----------
    wallet_id: str, optional
        It defaults to `'default_wallet'`, in which case it will search
        the accounts created in the default wallet created by lbrynet.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict of dicts
        The output dictionary has two keys with information on the wallet,
        and the accounts.
        - 'wallet': a dictionary with 8 keys, 'id', 'name', which are strings,
          corresponding to the `wallet_id` and name of the current wallet;
          and then 'total', 'available', 'reserved', 'claims', 'supports',
          and 'tips', which are numerical values summarizing the LBC
          held by all wallet accounts.
        - 'accounts': a list of dictionaries, where each dictionary
          contains information on each wallet account.
          There are 10 keys: 'id' (a 34-character identifier), 'name',
          'generator' ('deterministic-chain' or 'single-address'),
          'total', 'available', 'reserved', 'claims', 'supports',
          'tips', which are numerical values summarizing the LBC
          held by this account.
          The last key is 'addresses' which contains a list of dictionaries,
          one for each address in the account.
          Each of these dictionaries has three keys, 'n', a numerical value
          indicating the position of the address in the account;
          'address', the actual 34-character address;
          and 'used_times', the number of times the address has been used
          to send or receive coins.
    False
        If there is a problem, such as non-existing `wallet_id`,
        it will return `False`.
    """
    wallet = get_bal_wallet(wallet_id=wallet_id, server=server)

    if not wallet:
        return False

    accounts = get_accounts(wallet_id=wallet_id, server=server)

    return {"wallet": wallet,
            "accounts": accounts}


def print_accounts(wallet_info, addresses=False,
                   file=None, fdate=False, sep=";"):
    """Print the account information including sub-addresses optionally."""
    accounts = wallet_info["accounts"]

    n_accounts = len(accounts)

    if n_accounts < 1:
        return False

    acc_addresses = []
    acc_values = []
    acc_subaddresses = []

    for num, account in enumerate(accounts, start=1):
        ID = account["id"]
        name = account["name"]
        gen = account["generator"]

        line = (f"{num:2d}/{n_accounts:2d}" + f"{sep} "
                f"{ID}" + f"{sep} "
                f"{gen:19s}" + f"{sep} "
                f'"{name}"')
        acc_addresses.append(line)

        total = account["total"]
        available = account["available"]
        reserved = account["reserved"]

        claims = account["claims"]
        supports = account["supports"]
        tips = account["tips"]

        line2 = (f"{num:2d}/{n_accounts:2d}" + f"{sep} "
                 f"total: {total:14.8f}" + f"{sep} "
                 f"available: {available:14.8f}" + f"{sep} "
                 f"reserved: {reserved:14.8f}" + f"{sep} "
                 f"claims: {claims:14.8f}" + f"{sep} "
                 f"supports: {supports:14.8f}" + f"{sep} "
                 f"tips: {tips:14.8f}")

        acc_values.append(line2)

        sub_addresses = []
        for sub_address in account["addresses"]:
            n_add = sub_address["n"]
            address = sub_address["address"]
            used = sub_address["used_times"]

            sub_addresses.append(f"{n_add:4d}: "
                                 f"{address}" + f"{sep} "
                                 f"uses: {used}")

        g_addresses = "\n".join(sub_addresses)
        group = (f"{num}/{n_accounts}" + f"{sep} "
                 f"{ID}" + f"{sep} "
                 f'"{name}"' + "\n"
                 + g_addresses)

        if num < n_accounts:
            group += "\n"

        acc_subaddresses.append(group)

    wallet = wallet_info["wallet"]
    w_total = wallet["total"]
    w_available = wallet["available"]
    w_reserved = wallet["reserved"]

    w_claims = wallet["claims"]
    w_supports = wallet["supports"]
    w_tips = wallet["tips"]

    space0 = 29 * "-"
    space1 = " " + 26 * "-"
    space2 = " " + 25 * "-"
    space3 = " " + 23 * "-"
    space4 = " " + 25 * "-"
    space5 = " " + 20 * "-"

    w_summary = [space0 + space1 + space2 + space3 + space4 + space5,
                 7 * " " +
                 f"total: {w_total:14.8f}" + f"{sep} "
                 f"available: {w_available:14.8f}" + f"{sep} "
                 f"reserved: {w_reserved:14.8f}" + f"{sep} "
                 f"claims: {w_claims:14.8f}" + f"{sep} "
                 f"supports: {w_supports:14.8f}" + f"{sep} "
                 f"tips: {w_tips:14.8f}"]

    wid = wallet["id"]
    wname = wallet["name"]
    w_info = [f'id: "{wid}"' + f"{sep} " + f'"{wname}"']

    out = w_info
    out += acc_addresses + [""]
    out += acc_values + w_summary

    if addresses:
        out += [""] + acc_subaddresses

    funcs.print_content(out, file=file, fdate=fdate)


def list_accounts(wallet_id="default_wallet", addresses=False,
                  file=None, fdate=False, sep=";",
                  server="http://localhost:5279"):
    """Display information of the accounts on the default wallet.

    Parameters
    ----------
    wallet_id: str, optional
        It defaults to `'default_wallet'`, in which case it will search
        the accounts created in the default wallet created by lbrynet.
    addresses: bool, optional
        It defaults to `False`, in which case it will just display
        the condensed account information.
        If it is `True` it will display the addresses used by each account.
        Some accounts may include thousands of addresses.
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
    dict of dicts
        The output dictionary has two keys with information on the wallet,
        and the accounts.
        - 'wallet': a dictionary with 8 keys, 'id', 'name', which are strings,
          corresponding to the `wallet_id` and name of the current wallet;
          and then 'total', 'available', 'reserved', 'claims', 'supports',
          and 'tips', which are numerical values summarizing the LBC
          held by all wallet accounts.
        - 'accounts': a list of dictionaries, where each dictionary
          contains information on each wallet account.
          There are 10 keys: 'id' (a 34-character identifier), 'name',
          'generator' ('deterministic-chain' or 'single-address'),
          'total', 'available', 'reserved', 'claims', 'supports',
          'tips', which are numerical values summarizing the LBC
          held by this account.
          The last key is 'addresses' which contains a list of dictionaries,
          one for each address in the account.
          Each of these dictionaries has three keys, 'n', a numerical value
          indicating the position of the address in the account;
          'address', the actual 34-character address;
          and 'used_times', the number of times the address has been used
          to send or receive coins.
    False
        If there is a problem, such as non-existing `wallet_id`,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    print("Accounts in the wallet")
    print(80 * "-")

    wallet_info = get_wallet_info(wallet_id=wallet_id,
                                  server=server)

    if not wallet_info:
        return False

    print_accounts(wallet_info, addresses=addresses,
                   file=file, fdate=fdate, sep=sep)

    return wallet_info
