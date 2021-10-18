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
import os
import requests
import time

import lbrytools.funcs as funcs


def claims_bids(skip_controlling=True, skip_repost=False, channels_only=False,
                show_claim_id=False,
                show_repost_status=True,
                show_competing=True, show_reposts=True,
                compact=False,
                file=None, fdate=False, sep=";",
                server="http://localhost:5279"):
    """Display the claims that are competing in name and LBC bidding.

    This is based on an original script by `@BrendonBrewer:3/vanity:8`

    Parameters
    ----------
    skip_controlling: bool, optional
        It defaults to `True`, in which case it will not process
        the 'controlling' claims, that is, those which have the highest bid.
        If it is `False` it will process all claims whether
        they have the highest bid (controlling) or not (non-controlling).
    skip_repost: bool, optional
        It defaults to `False`, in which case it will process all claims
        whether they are reposts or not.
        If it is `True` it will not process reposts.
    channels_only: bool, optional
        It defaults to `False`, in which case it will process all claims
        whether they are channels or not.
        If it is `True` it will only process the claims that are channels.
    show_claim_id: bool, optional
        It defaults to `False`.
        If it is `True`, the claim ID will be printed for all claims.
        This option only has an effect when `compact=True`.
    show_repost_status: bool, optional
        It defaults to `True`, in which case it will show whether the claims
        are reposts or not.
        This option only has an effect when `compact=True`.
    show_competing: bool, optional
        It defaults to `True`, in which case it will show the number
        of competing claims, that is, those that share the same name
        with the claim being inspected.
        This option only has an effect when `compact=True`.
    show_reposts: bool, optional
        It defaults to `True`, in which case it will show the number
        of reposts for the claim being inspected.
        This option only has an effect when `compact=True`.
    compact: bool, optional
        It defaults to `False`, in which case each claim's information
        will be printed in a paragraph.
        If it is `True` there will be one claim per row, so the summary
        will be more compact.
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
        It returns the list of dictionaries representing the processed claims.
    False
        If there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    msg = {"method": "claim_list",
           "params": {"page_size": 99000,
                      "resolve": True}}

    output = requests.post(server, json=msg).json()
    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    print("Analysis of the bidding amounts for claims, "
          "including channels, videos, reposts, playlists, etc.")

    num_claims = output["result"]["total_items"]
    print(f"Number of claims: {num_claims}")

    if skip_controlling:
        print("- Only non-controlling claims (low bids) will be considered")
    else:
        print("- Both controlling and non-controlling claims "
              "will be considered (high and low bids)")

    if skip_repost:
        print("- Reposts will be omitted")
    else:
        print("- Reposts will be considered")

    if channels_only:
        print("- Only channels will be considered")

    print(80 * "-")

    claims = output["result"]["items"]

    out = []
    claims_filtered = []

    for it, claim in enumerate(claims, start=1):
        is_repost = claim["value_type"] == "repost"
        is_channel = claim["value_type"] == "channel"
        is_controlling = claim["meta"]["is_controlling"]

        if ((skip_controlling and is_controlling)
                or (skip_repost and is_repost)
                or (channels_only and not is_channel)):
            continue

        claims_filtered.append(claim)

        uri = claim["canonical_url"]
        claim_id = claim["claim_id"]
        name = claim["name"]
        staked = float(claim["amount"])
        staked += float(claim["meta"]["support_amount"])

        # It's unlikely that more than 1000 items will share the same name
        msg2 = {"method": "claim_search",
                "params": {"name": name,
                           "page_size": 1000}}

        output2 = requests.post(server, json=msg2).json()
        if "error" in output2:
            print(">>> No 'result' in the JSON-RPC server output")
            return False

        max_lbc = 0
        competitors = 0
        comp_reposts = 0
        items = output2["result"]["items"]

        for item in items:
            item_lbc = float(item["amount"])
            item_lbc += float(item["meta"]["support_amount"])

            rep_claim_id = ("reposted_claim_id" in item
                            and item["reposted_claim_id"] == claim_id)

            if item["claim_id"] != claim_id or rep_claim_id:
                if max_lbc == 0 or item_lbc > max_lbc:
                    max_lbc = float(item_lbc)

                if item["value_type"] == "repost":
                    comp_reposts += 1
                else:
                    competitors += 1

        name = f'"{name}"'

        if compact:
            line = f"{it:3d}/{num_claims:3d}" + f"{sep} "
            if show_claim_id:
                line += f"{claim_id}" + f"{sep} "

            line += f"{name:56s}" + f"{sep} "
            line += f"controlling: {str(is_controlling):5s}" + f"{sep} "

            if show_repost_status:
                line += f"repost: {str(is_repost):5s}" + f"{sep} "
            if show_competing:
                line += f"competing: {competitors:2d}" + f"{sep} "
            if show_reposts:
                line += f"reposts: {comp_reposts:2d}" + f"{sep} "

            line += (f"staked: {staked:7.2f}" + f"{sep} " +
                     f"highest bid: {max_lbc:7.2f}")
            out += [line]
        else:
            paragraph = (f"Claim {it}/{num_claims}, {name}\n"
                         f"canonical_url: {uri}\n"
                         f"claim_id: {claim_id}\n"
                         f"controlling claim: {is_controlling}\n"
                         f"repost: {is_repost}\n"
                         f"competing: {competitors}\n")
            if is_repost:
                paragraph += f"reposts: {comp_reposts} + 1\n"
            else:
                paragraph += f"reposts: {comp_reposts}\n"

            paragraph += (f"staked: {staked:.3f}\n"
                          f"highest bid: {max_lbc:.3f} (by others)\n")
            out += [paragraph]

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
        fd.close()
        print(f"Summary written: {file}")
    else:
        print("\n".join(out))

    return claims_filtered


if __name__ == "__main__":
    claims_bids(skip_controlling=True, skip_repost=False, channels_only=False)
    # claims_bids(skip_controlling=True, skip_repost=True, channels_only=False)
