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
import requests

import lbrytools.funcs as funcs
import lbrytools.search as srch


def get_all_supports(server="http://localhost:5279"):
    """Get all supports in a dictionary; all, valid, and invalid.

    Returns
    -------
    dict
        A dictionary with information on the supports.
        The keys are the following:
        - 'all_supports': list with dictionaries of all supports.
        - 'all_resolved': list with dictionaries of all resolved claims
          corresponding to all supports.
          Invalid claims will simply be `False`.
        - 'valid_supports': list with dictionaries of supports
          for valid claims only.
        - 'valid_resolved': list with dictionaries of resolved claims
          corresponding to `'valid_supports'` only.
        - 'invalid_supports': list with dictionaries of supports
          for invalid claims. The claim IDs in these dictionaries
          cannot be resolved anymore.
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

    valid = []
    valid_resolved = []
    invalid = []

    all_supports = []
    all_resolved = []

    for item in items:
        s = srch.search_item(cid=item["claim_id"])

        if not s:
            invalid.append(item)
        else:
            valid.append(item)
            valid_resolved.append(s)

        all_supports.append(item)
        all_resolved.append(s)

    return {"all_supports": all_supports,
            "all_resolved": all_resolved,
            "valid_supports": valid,
            "valid_resolved": valid_resolved,
            "invalid_supports": invalid}


def list_supports(claim_id=False, invalid=False,
                  combine=True, claims=True, channels=True,
                  file=None, fdate=False, sep=";",
                  server="http://localhost:5279"):
    """Print supported claims, the amount, and the trending score.

    Parameters
    ----------
    claim_id: bool, optional
        It defaults to `False`, in which case only the name of the claim
        is shown.
        If it is `True` the `'claim_id'` will be shown as well.
    invalid: bool, optional
        It defaults to `False`, in which case it will show all supported
        claims, even those that are invalid.
        If it is `True` it will only show invalid claims. Invalid are those
        which were deleted by their authors, so the claim (channel
        or content) is no longer available in the blockchain.
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

    supports = get_all_supports(server=server)
    if not supports:
        return False

    items = supports["all_supports"]
    resolved = supports["all_resolved"]
    n_items = len(items)

    out_list = []
    for num, pair in enumerate(zip(items, resolved), start=1):
        item = pair[0]
        s = pair[1]

        name = item["name"]
        cid = item["claim_id"]
        is_channel = True if name.startswith("@") else False

        if is_channel and not channels:
            continue
        if not is_channel and not claims:
            continue

        obj = ""
        if claim_id:
            obj += f'"{cid}"' + f"{sep} "

        _name = f'"{name}"'

        if not s:
            _name = "[" + _name + "]"

        obj += f'{_name:58s}'

        _amount = float(item["amount"])
        amount = f"{_amount:14.8f}"

        if not s:
            m = {"support_amount": "0.0"}
            s = {"amount": item["amount"]}
        else:
            if invalid:
                continue
            m = s["meta"]

        existing_support = float(s["amount"]) + float(m["support_amount"])

        trend_gl = m.get("trending_global", 0)
        trend_gr = m.get("trending_group", 0)
        trend_loc = m.get("trending_local", 0)
        trend_mix = m.get("trending_mixed", 0)

        combined = (trend_gl
                    + trend_gr
                    + trend_loc
                    + trend_mix)

        tr_gl = f'{trend_gl:7.2f}'
        tr_gr = f'{trend_gr:7.2f}'
        tr_loc = f'{trend_loc:7.2f}'
        tr_mix = f'{trend_mix:7.2f}'
        tr_combined = f'{combined:7.2f}'
        is_spent = item["is_spent"]

        out = f"{num:3d}/{n_items:3d}" + f"{sep} "
        out += f"{obj}" + f"{sep} " + f"{amount}" + f"{sep} "
        out += f"{existing_support:15.8f}" + f"{sep} "

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

    funcs.print_content(out_list, file=file, fdate=fdate)

    return resolved


def get_base_support(uri=None, cid=None, name=None,
                     server="http://localhost:5279"):
    """Get the existing, base, and our support from a claim.

    Returns
    -------
    dict
        A dictionary with information on the support on a claim.
        The keys are the following:
        - 'canonical_url'
        - 'claim_id'
        - 'existing_support': total support that the claim has;
          this is `'base_support'` + `'old_support'`.
        - 'base_support': support that the claim has without our support.
        - 'old_support': support that we have added to this claim;
          it may be zero if this claim does not have any support from us.
    False
        If there is a problem or no list of supports, it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    item = srch.search_item(uri=uri, cid=cid, name=name, offline=False,
                            server=server)

    if not item:
        return False

    uri = item["canonical_url"]
    cid = item["claim_id"]

    existing = float(item["amount"]) + float(item["meta"]["support_amount"])

    msg = {"method": "support_list",
           "params": {"claim_id": item["claim_id"]}}

    output = requests.post(server, json=msg).json()

    if "error" in output:
        return False

    supported_items = output["result"]["items"]
    old_support = 0

    if not supported_items:
        # Old support remains 0
        pass
    else:
        for su_item in supported_items:
            old_support += float(su_item["amount"])

    base_support = existing - old_support

    return {"canonical_url": uri,
            "claim_id": cid,
            "existing_support": existing,
            "base_support": base_support,
            "old_support": old_support}


def create_support(uri=None, cid=None, name=None,
                   amount=0.0,
                   server="http://localhost:5279"):
    """Create a new support on the claim.

    Parameters
    ----------
    uri: str
        A unified resource identifier (URI) to a claim on the LBRY network.
        It can be full or partial.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            uri = '@MyChannel#3/some-video-name#2'
            uri = 'some-video-name'

        The URI is also called the `'canonical_url'` of the claim.
    cid: str, optional
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            name = 'some-video-name'
    amount: float, optional
        It defaults to `0.0`.
        It is the amount of LBC support that will be deposited,
        whether there is a previous support or not.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with information on the result of the support.
        The keys are the following:
        - 'canonical_url': canonical URI of the claim.
        - 'claim_id': unique 40 character alphanumeric string.
        - 'existing_support': existing support before we add or remove ours;
          this is the sum of `base_support` and `old_support`.
        - 'base_support': existing minimum support that we do not control;
          all published claims must have a positive `base_support`.
        - 'old_support': support that we have added to this claim in the past;
          it may be zero.
        - 'new_support': new support that was successfully deposited
          in the claim, equal to `keep`.
        - 'txid': transaction ID in the blockchain that records the operation.
    False
        If there is a problem or non existing claim, or lack of funds,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    supports = get_base_support(uri=uri, cid=cid, name=name)
    if not supports:
        return False

    uri = supports["canonical_url"]
    claim_id = supports["claim_id"]
    existing = supports["existing_support"]
    base_support = supports["base_support"]
    old_support = supports["old_support"]

    new_support = 0.0
    t_input = 0.0
    t_output = 0.0
    t_fee = 0.0
    txid = None

    amount = abs(amount)
    msg = {"method": "support_create",
           "params": {"claim_id": claim_id,
                      "amount": f"{amount:.8f}"}}

    output = requests.post(server, json=msg).json()

    if "error" in output:
        error = output["error"]
        if "data" in error:
            print(">>> Error: {}, {}".format(error["data"]["name"],
                                             error["message"]))
        else:
            print(f">>> Error: {error}")
        print(f">>> Requested amount: {amount:.8f}")
        return False

    new_support = amount
    t_input = float(output["result"]["total_input"])
    t_output = float(output["result"]["total_output"])
    t_fee = float(output["result"]["total_fee"])
    txid = output["result"]["txid"]

    out = [f"canonical_url: {uri}",
           f"claim_id: {claim_id}",
           f"Existing support: {existing:14.8f}",
           f"Base support:     {base_support:14.8f}",
           f"Old support:      {old_support:14.8f}",
           f"New support:      {new_support:14.8f}",
           "",
           f"Applied:          {new_support:14.8f}",
           f"total_input:      {t_input:14.8f}",
           f"total_output:     {t_output:14.8f}",
           f"total_fee:        {t_fee:14.8f}",
           f"txid: {txid}"]
    print("\n".join(out))

    return {"canonical_url": uri,
            "claim_id": claim_id,
            "existing_support": existing,
            "base_support": base_support,
            "old_support": old_support,
            "new_support": new_support,
            "txid": txid}


def calculate_abandon(claim_id=None, keep=0.0,
                      server="http://localhost:5279"):
    """Actually abandon the support and get the data."""
    new_support = 0.0
    t_input = 0.0
    t_output = 0.0
    t_fee = 0.0
    txid = None

    msg = {"method": "support_abandon",
           "params": {"claim_id": claim_id}}

    if keep:
        msg["params"]["keep"] = f"{keep:.8f}"

    output = requests.post(server, json=msg).json()

    if "error" in output:
        error = output["error"]
        if "data" in error:
            print(">>> Error: {}, {}".format(error["data"]["name"],
                                             error["message"]))
        else:
            print(f">>> Error: {error}")
        print(f">>> Requested amount: {keep:.8f}")
        return False, False

    new_support = keep
    t_input = float(output["result"]["total_input"])
    t_output = float(output["result"]["total_output"])
    t_fee = float(output["result"]["total_fee"])
    txid = output["result"]["txid"]

    calc = {"new_support": new_support,
            "t_input": t_input,
            "t_output": t_output,
            "t_fee": t_fee,
            "txid": txid}

    text = [f"Applied:          {new_support:14.8f}",
            f"total_input:      {t_input:14.8f}",
            f"total_output:     {t_output:14.8f}",
            f"total_fee:        {t_fee:14.8f}",
            f"txid: {txid}"]

    return calc, text


def abandon_support(uri=None, cid=None, name=None,
                    keep=0.0,
                    server="http://localhost:5279"):
    """Abandon a support, or change it to a different amount.

    Parameters
    ----------
    uri: str
        A unified resource identifier (URI) to a claim on the LBRY network.
        It can be full or partial.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            uri = '@MyChannel#3/some-video-name#2'
            uri = 'some-video-name'

        The URI is also called the `'canonical_url'` of the claim.
    cid: str, optional
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            name = 'some-video-name'
    keep: float, optional
        It defaults to `0.0`.
        It is the amount of LBC support that should remain in the claim
        after we remove our previous support. That is, we can use
        this parameter to assign a new support value.
        If it is `0.0` all support is removed.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with information on the result of the support.
        The keys are the following:
        - 'canonical_url': canonical URI of the claim.
        - 'claim_id': unique 40 character alphanumeric string.
        - 'existing_support': existing support before we add or remove ours;
          this is the sum of `base_support` and `old_support`.
        - 'base_support': existing minimum support that we do not control;
          all published claims must have a positive `base_support`.
        - 'old_support': support that we have added to this claim in the past;
          it may be zero.
        - 'new_support': new support that was successfully deposited
          in the claim, equal to `keep`.
        - 'txid': transaction ID in the blockchain that records the operation.
    False
        If there is a problem or non existing claim, or lack of funds,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    supports = get_base_support(uri=uri, cid=cid, name=name)
    if not supports:
        return False

    uri = supports["canonical_url"]
    claim_id = supports["claim_id"]
    existing = supports["existing_support"]
    base_support = supports["base_support"]
    old_support = supports["old_support"]

    calc, text = calculate_abandon(claim_id=claim_id, keep=keep,
                                   server=server)
    if not calc:
        return False

    new_support = calc["new_support"]
    txid = calc["txid"]

    out = [f"canonical_url: {uri}",
           f"claim_id: {claim_id}",
           f"Existing support: {existing:14.8f}",
           f"Base support:     {base_support:14.8f}",
           f"Old support:      {old_support:14.8f}",
           f"New support:      {keep:14.8f}",
           ""]
    out += text

    print("\n".join(out))

    return {"canonical_url": uri,
            "claim_id": claim_id,
            "existing_support": existing,
            "base_support": base_support,
            "old_support": old_support,
            "new_support": new_support,
            "txid": txid}


def abandon_support_inv(invalids=None, cid=None, name=None,
                        keep=0.0,
                        server="http://localhost:5279"):
    """Abandon or change a support for invalid claims.

    Parameters
    ----------
    invalids: list of dict, optional
        A list where each element is a dictionary indicating the support
        for an 'invalid' claim.
        Invalid claims no longer resolve online (the output has been spent)
        but they may still have an existing support.
        If this list is `None`, the list will be obtained
        from `get_all_supports()['invalid_supports']`.
    cid: str, optional
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            name = 'some-video-name'
    keep: float, optional
        It defaults to `0.0`.
        It is the amount of LBC support that should remain in the claim
        after we remove our previous support. That is, we can use
        this parameter to assign a new support value.
        If it is `0.0` all support is removed.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with information on the result of the support.
        The keys are the following:
        - 'claim_name': name of the claim; the canonical URI is not available
          because the claim can't be resolved online any more.
        - 'claim_id': unique 40 character alphanumeric string.
        - 'existing_support': existing support before we add or remove ours;
          this should be the same as `old_support`.
        - 'base_support': since this claim does not resolve any more,
          it should be zero.
        - 'old_support': support that we have added to this claim in the past;
          it cannot be zero because we use this method only with claims
          that have been previously supported (and are now invalid).
        - 'new_support': new support that was successfully deposited
          in the claim, equal to `keep`.
        - 'txid': transaction ID in the blockchain that records the operation.
    False
        If there is a problem or non existing claim, or lack of funds,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if not cid and not name:
        print(80 * "-")
        print(f'cid={cid}\n'
              f'name="{name}"')
        return False

    existing = 0
    base_support = 0
    old_support = 0
    found = False

    if not invalids:
        all_supports = get_all_supports(server=server)

        if not all_supports:
            return False

        invalids = all_supports["invalid_supports"]

    for supp in invalids:
        if ((cid and cid in supp["claim_id"])
                or (name and name in supp["name"])):
            existing = float(supp["amount"])
            old_support = float(supp["amount"])
            claim_id = supp["claim_id"]
            c_name = supp["name"]
            found = True

    if not found:
        print(80 * "-")
        print("Claim not found among the invalid claims")
        print(f'cid={cid}\n'
              f'name="{name}"')
        return False

    calc, text = calculate_abandon(claim_id=claim_id, keep=keep,
                                   server=server)
    if not calc:
        return False

    new_support = calc["new_support"]
    txid = calc["txid"]

    out = [f"claim_name: {c_name}",
           f"claim_id: {claim_id}",
           f"Existing support: {existing:14.8f}",
           f"Base support:     {base_support:14.8f}",
           f"Old support:      {old_support:14.8f}",
           f"New support:      {keep:14.8f}",
           ""]
    out += text

    print("\n".join(out))

    return {"claim_name": c_name,
            "claim_id": claim_id,
            "existing_support": existing,
            "base_support": base_support,
            "old_support": old_support,
            "new_support": new_support,
            "txid": txid}


def target_support(uri=None, cid=None, name=None,
                   target=0.0,
                   server="http://localhost:5279"):
    """Add an appropriate amount of LBC to reach a target support.

    Parameters
    ----------
    uri: str
        A unified resource identifier (URI) to a claim on the LBRY network.
        It can be full or partial.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            uri = '@MyChannel#3/some-video-name#2'
            uri = 'some-video-name'

        The URI is also called the `'canonical_url'` of the claim.
    cid: str, optional
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            name = 'some-video-name'
    target: float, optional
        It defaults to `0.0`.
        It is the amount of LBC support that we want the claim to have
        at the end of our support.
        For example, if the current support is `100`, and we specify a target
        of `500`, we will be supporting the claim with `400`
        in order to reach the target.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with information on the result of the support.
        The keys are the following:
        - 'canonical_url': canonical URI of the claim.
        - 'claim_id': unique 40 character alphanumeric string.
        - 'existing_support': existing support before we add or remove ours;
          this is the sum of `base_support` and `old_support`.
        - 'base_support': existing minimum support that we do not control;
          all published claims must have a positive `base_support`.
        - 'old_support': support that we have added to this claim in the past;
          it may be zero.
        - 'target': target support that we want after running this method.
          It must be a positive number.
        - 'must_add': amount of support that we must add or remove (negative)
          to reach the `target`; it may be zero if `target`
          is already below the `base_support`.
        - 'new_support': new support that was successfully deposited
          in the claim; it may be zero if `target` is already below
          the `base_support`, or if `old_support` already satisfies
          our `target`.
        - 'txid': transaction ID in the blockchain that records the operation;
          it may be `None` if the transaction was not made because the `target`
          was already achieved before applying additional support.
    False
        If there is a problem or non existing claim, or lack of funds,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    supports = get_base_support(uri=uri, cid=cid, name=name)
    if not supports:
        return False

    uri = supports["canonical_url"]
    claim_id = supports["claim_id"]
    existing = supports["existing_support"]
    base_support = supports["base_support"]
    old_support = supports["old_support"]

    target = abs(target)
    out = [f"canonical_url: {uri}",
           f"claim_id: {claim_id}",
           f"Existing support: {existing:14.8f}",
           f"Base support:     {base_support:14.8f}",
           f"Old support:      {old_support:14.8f}",
           "",
           f"Target:           {target:14.8f}"]

    new_support = 0.0
    must_add = 0.0

    if target > base_support:
        # Target above base, calculate addition
        must_add = target - existing
        new_support = old_support + must_add
    elif target < base_support:
        if not old_support:
            # Target below base support, and no old support, nothing to add,
            # reset support to 0
            pass
        else:
            # Target below base support, and old support, remove it
            must_add = -old_support
    else:
        # Same target as base support, nothing to add, reset support to 0
        pass

    out.append(f"Must add:         {must_add:14.8f}")
    out.append(f"New support:      {new_support:14.8f}")

    applied = 0.0
    t_input = 0.0
    t_output = 0.0
    t_fee = 0.0
    txid = None

    # The SDK accepts the amount as a string, not directly as a number.
    # The minimum amount is 0.00000001, so we convert all quantities
    # to have 8 decimal significant numbers.
    #
    # Only perform the transaction if the new support is different
    # from the old support
    if new_support != old_support:
        if not old_support and new_support > 0:
            # No existing support, so we create it
            msg = {"method": "support_create",
                   "params": {"claim_id": claim_id,
                              "amount": f"{new_support:.8f}"}}
            output = requests.post(server, json=msg).json()
        else:
            # Existing support, so we update it with the new value
            msg = {"method": "support_abandon",
                   "params": {"claim_id": claim_id,
                              "keep": f"{new_support:.8f}"}}
            output = requests.post(server, json=msg).json()

        if "error" in output:
            error = output["error"]
            if "data" in error:
                print(">>> Error: {}, {}".format(error["data"]["name"],
                                                 error["message"]))
            else:
                print(f">>> Error: {error}")
            print(f">>> Requested amount: {new_support:.8f}")
            return False

        applied = new_support
        t_input = float(output["result"]["total_input"])
        t_output = float(output["result"]["total_output"])
        t_fee = float(output["result"]["total_fee"])
        txid = output["result"]["txid"]

    out += ["",
            f"Applied:          {applied:14.8f}",
            f"total_input:      {t_input:14.8f}",
            f"total_output:     {t_output:14.8f}",
            f"total_fee:        {t_fee:14.8f}",
            f"txid: {txid}"]

    print("\n".join(out))

    return {"canonical_url": uri,
            "claim_id": cid,
            "existing_support": existing,
            "base_support": base_support,
            "old_support": old_support,
            "target": target,
            "must_add": must_add,
            "new_support": new_support,
            "txid": txid}
