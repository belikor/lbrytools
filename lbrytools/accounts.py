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
import os
import requests
import time

import lbrytools.funcs as funcs


def list_accounts(addresses=False,
                  file=None, fdate=False,
                  server="http://localhost:5279"):
    """Display information of the accounts on the default wallet.

    Parameters
    ----------
    addresses: bool, optional
        It defaults to `False`, in which case it will just display
        the condensed account information.
        If it is `True` it will display the addresses used by each account.
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
        It returns `True` if it prints the information successfully.
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    print("Accounts in the wallet")
    print(80 * "-")

    msg = {"method": "account_list",
           "params": {}}

    output = requests.post(server, json=msg).json()
    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    result = output["result"]

    items = result["items"]
    n_acc = len(items)

    out = []
    out2 = []
    out3 = []

    for it, item in enumerate(items, start=1):
        ID = item["id"]
        name = item["name"]
        coins = item["coins"]
        gen = item["address_generator"]["name"]

        out += [f"{it}/{n_acc}, "
                f"{ID}, {name}, {gen}, {coins}"]

        msg2 = {"method": "account_balance",
                "params": {"account_id": ID}}

        output = requests.post(server, json=msg2).json()
        if "error" in output:
            continue

        res2 = output["result"]
        total = res2["total"]
        available = res2["available"]
        claims = res2["reserved_subtotals"]["claims"]
        supports = res2["reserved_subtotals"]["supports"]
        tips = res2["reserved_subtotals"]["tips"]

        out2 += [f"{it}/{n_acc}, "
                 f"total: {total}, "
                 f"available: {available}, "
                 f"claims: {claims}, "
                 f"supports: {supports}, "
                 f"tips: {tips}"]

        if not addresses:
            continue

        msg3 = {"method": "address_list",
                "params": {"account_id": ID,
                           "page_size": 1000}}

        output = requests.post(server, json=msg3).json()
        if "error" in output:
            continue

        res3 = output["result"]
        ad_items = res3["items"]

        ad = []
        for iit, address in enumerate(ad_items, start=1):
            num = address["used_times"]
            if num < 1:
                continue
            ad.append(f"{iit:3d}: " + address["address"]
                      + f", uses: {num}")

        lines = "\n".join(ad)
        out3 += [f"{it}/{n_acc}, {ID}, {name}\n"
                 + lines + "\n"]

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
        print("\n".join(out), file=fd)
        print("", file=fd)
        print("\n".join(out2), file=fd)

        if addresses:
            print("", file=fd)
            print("\n".join(out3), file=fd)

        fd.close()
        print(f"Summary written: {file}")
    else:
        print("\n".join(out))
        print()
        print("\n".join(out2))

        if addresses:
            print()
            print("\n".join(out3))

    return True
