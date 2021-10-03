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
"""Auxiliary functions for handling supports."""
import os
import requests
import time

import lbrytools.funcs as funcs
import lbrytools.search as srch


def list_supports(claim_id=False,
                  combine=True, claims=True, channels=True,
                  file=None, fdate=False, sep=";",
                  server="http://localhost:5279"):
    """Print supported claims, the amount, and the trending score.

    Parameters
    ----------
    claim_id: bool, optional
        It defaults to `False`, in which case the name of the claim is shown.
        If it is `True` the `'claim_id'` will be shown instead.
    combine: bool, optional
        It defaults to `True`, in which case the `global`, `group`, `local`,
        and `mixed` trending scores are added into one combined score.
        If it is `False` it will show the four values separately.
    claims: bool, optional
        It defaults to `True`, in which case supported claims will be shown.
        If it is `False` simple claims won't be shown.
    channels: bool, optional
        It defaults to `True`, in which case supported channels will be shown.
        If it is `False` channel claims (which start with the `@` symbol)
        won't be shown.
    file: str, optional
        It defaults to `None`.
        It must be a user writable path to which the summary will be written.
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
    list
        The list of resolved claims, as returned by `lbrynet resolve`.
        Each item is a dictionary with information from the supported claim
        which may be a stream (video, music, document) or a channel.
    False
        If there is a problem or no list of supports, it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    msg = {"method": "support_list",
           "params": {"page_size": 99000}}
    output = requests.post(server, json=msg).json()

    if "error" in output:
        return False

    items = output["result"]["items"]
    n_items = len(items)

    if n_items < 1:
        print(f"Supports found: {n_items}")
        return False

    resolved = []
    for item in items:
        s = srch.search_item(cid=item["claim_id"])
        resolved.append(s)

    out_list = []
    for num, pair in enumerate(zip(items, resolved), start=1):
        item = pair[0]
        s = pair[1]

        name = item["name"]
        if claim_id:
            obj = f'"{item["claim_id"]}"'
        else:
            _name = f'"{name}"'
            obj = f'{_name:50s}'

        is_channel = True if name.startswith("@") else False

        if is_channel and not channels:
            continue
        if not is_channel and not claims:
            continue

        amount = f'{float(item["amount"]):8.2f}'
        m = s["meta"]
        combined = (m["trending_global"] + m["trending_group"]
                    + m["trending_local"] + m["trending_mixed"])

        tr_gl = f'{m["trending_global"]:6.2f}'
        tr_gr = f'{m["trending_group"]:6.2f}'
        tr_loc = f'{m["trending_local"]:6.2f}'
        tr_mix = f'{m["trending_mixed"]:6.2f}'
        tr_combined = f'{combined:6.2f}'
        is_spent = item["is_spent"]

        out = f"{num:3d}/{n_items:3d}" + f"{sep} "
        out += f"{obj}" + f"{sep} " + f"{amount}" + f"{sep} "
        if not is_spent:
            if combine:
                out += f"combined: {tr_combined}"
            else:
                out += f"mix: {tr_mix}" + f"{sep} "
                out += f"glob: {tr_gl}" + f"{sep} "
                out += f"grp: {tr_gr}" + f"{sep} "
                out += f"loc: {tr_loc}"
        else:
            continue
        out_list.append(out)

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
        for line in out_list:
            print(line, file=fd)

        fd.close()
        print(f"Summary written: {file}")
    else:
        print("\n".join(out_list))

    return resolved
