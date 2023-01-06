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
"""Functions to display playlist information."""
import requests
import time

import lbrytools.funcs as funcs


def search_playlists(shared=True,
                     server="http://localhost:5279"):
    """Search the playlists in the wallet."""
    if not funcs.server_exists(server=server):
        return False

    msg = {"method": "preference_get",
           "params": {}}

    output = requests.post(server, json=msg).json()
    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    result = output["result"]

    if "enable-sync" in result:
        sync = result["enable-sync"]
    else:
        sync = False

    r_local = result["local"]

    if "shared" in result:
        r_shared = result["shared"]

    print(f"Synchronization: {sync}")

    builtin = False
    if "builtinCollections" in r_local["value"]:
        pl_builtin_local = r_local["value"]["builtinCollections"]
        builtin = True

    unpublished = False
    if "unpublishedCollections" in r_local["value"]:
        pl_unpub_local = r_local["value"]["unpublishedCollections"]
        unpublished = True

    if "shared" in result and "builtinCollections" in r_shared["value"]:
        pl_builtin_shared = r_shared["value"]["builtinCollections"]
        builtin = True

    if "shared" in result and "unpublishedCollections" in r_shared["value"]:
        pl_unpub_shared = r_shared["value"]["unpublishedCollections"]
        unpublished = True

    if not builtin or not unpublished:
        if shared:
            print(f"Database: shared")
        else:
            print(f"Database: local")

        print(f"Builtin collection: {builtin}")
        print(f"Unpublished collection: {unpublished}")
        print("No playlists. Exit.")
        return False

    if shared and "shared" in result:
        print(f"Database: shared")
        pl_builtin = pl_builtin_shared
        pl_unpub = pl_unpub_shared
    else:
        if shared:
            print("No shared database, will use local")
        else:
            print(f"Database: local")
        pl_builtin = pl_builtin_local
        pl_unpub = pl_unpub_local

    pl_favorites = pl_builtin["favorites"]
    pl_watchlater = pl_builtin["watchlater"]

    return {"favorites": pl_favorites,
            "watchlater": pl_watchlater,
            "unpublished": pl_unpub}


def print_playlists(playlists,
                    claim_id=False,
                    sanitize=False,
                    file=None, fdate=False, sep=";"):
    """Print the playlists, favorites, watch later, and unpublished."""
    pl_favorites = playlists["favorites"]
    pl_watchlater = playlists["watchlater"]
    pl_unpub = playlists["unpublished"]

    name_fav = pl_favorites["name"]
    n_fav = len(pl_favorites["items"])
    time_fav = time.gmtime(int(pl_favorites["updatedAt"]))
    time_fav = time.strftime(funcs.TFMT, time_fav)

    out_fav = [f'"{name_fav}", updated: {time_fav}']

    for num, claim in enumerate(pl_favorites["items"], start=1):
        name, cid = claim.split("lbry://")[1].split("#")
        uri = name + "#" + cid[0:3]

        if sanitize:
            uri = funcs.sanitize_text(uri)

        line = f"{num:3d}/{n_fav:3d}" + f"{sep} "

        if claim_id:
            line += f"{cid}" + f"{sep} "

        line += f"{uri}"
        out_fav.append(line)

    out_fav.append("")

    name_later = pl_watchlater["name"]
    n_later = len(pl_watchlater["items"])
    time_later = time.gmtime(int(pl_watchlater["updatedAt"]))
    time_later = time.strftime(funcs.TFMT, time_later)

    out_later = [f'"{name_later}", updated: {time_later}']

    for num, claim in enumerate(pl_watchlater["items"], start=1):
        name, cid = claim.split("lbry://")[1].split("#")
        uri = name + "#" + cid[0:3]

        if sanitize:
            uri = funcs.sanitize_text(uri)

        line = f"{num:3d}/{n_later:3d}" + f"{sep} "

        if claim_id:
            line += f"{cid}" + f"{sep} "

        line += f"{uri}"
        out_later.append(line)

    out_later.append("")

    n_unpub = len(pl_unpub)

    out_unpub = [f"Unpublished playlists: {n_unpub}"]

    for num_pl, k in enumerate(pl_unpub, start=1):
        pl_updated = time.gmtime(int(pl_unpub[k]["updatedAt"]))
        pl_updated = time.strftime(funcs.TFMT, pl_updated)
        pl_name = pl_unpub[k]["name"]
        pl_title = f'"{pl_name}", updated: {pl_updated}'

        items = pl_unpub[k]["items"]
        n_items = len(items)

        pl_elems = []

        for num, claim in enumerate(items, start=1):
            name, cid = claim.split("lbry://")[1].split("#")
            uri = name + "#" + cid[0:3]

            if sanitize:
                uri = funcs.sanitize_text(uri)

            line = f"{num:3d}/{n_items:3d}" + f"{sep} "

            if claim_id:
                line += f"{cid}" + f"{sep} "

            line += f"{uri}"
            pl_elems.append(line)

        pl_paragraph = "\n".join(pl_elems)

        if num_pl != n_unpub:
            pl_paragraph += "\n"

        out_unpub.append(f"{pl_title}\n" + pl_paragraph)

    out = []
    out.extend(out_fav)
    out.extend(out_later)
    out.extend(out_unpub)

    funcs.print_content(out, file=file, fdate=fdate)


def print_summary_playlists(playlists):
    """Print a summary of the playlists."""
    pl_favorites = playlists["favorites"]
    pl_watchlater = playlists["watchlater"]
    pl_unpub = playlists["unpublished"]

    name_fav = pl_favorites["name"]
    n_fav = len(pl_favorites["items"])

    name_later = pl_watchlater["name"]
    n_later = len(pl_watchlater["items"])

    n_unpub = len(pl_unpub)

    pl_elems = []

    for k in pl_unpub:
        pl_name = pl_unpub[k]["name"]
        n_items = len(pl_unpub[k]["items"])
        pl_elems.append(f'"{pl_name}": {n_items}')

    unpub_paragraph = "\n".join(pl_elems)

    out = [f'"{name_fav}" items:   {n_fav:4d}',
           f'"{name_later}" items: {n_later:4d}',
           32 * "-",
           f"Unpublished playlists: {n_unpub}",
           32 * "-"]

    out.append(unpub_paragraph)

    funcs.print_content(out, file=None, fdate=False)


def list_playlists(shared=True,
                   claim_id=False,
                   sanitize=False,
                   file=None, fdate=False, sep=";",
                   server="http://localhost:5279"):
    """Display the claims in the existing playlists.

    Parameters
    ----------
    shared: bool, optional
        It defaults to `True`, in which case it uses the shared database
        synchronized with Odysee online.
        If it is `False` it will use only the local database
        to the LBRY Desktop application.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim ID (40-character string)
        of each claim.
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the name of the claim and channel.
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
        It has three keys:
        - 'favorites': a dictionary with five keys, 'id', 'items', 'name',
          'type', and 'updatedAt'. The 'items' key contains a list with
          the individual URIs of the claims in this playlist.
        - 'watchlater': a dictionary with the same five keys as 'favorites'.
        - 'unpublished': a dictionary containing a variable number
          of dictionaries, each of them representing an unpublished playlist.
          Each playlist has the same five keys of the 'favorites'
          and 'watchlater' dictionaries.
          Each subdictionary has a key that is an alphanumeric string,
          although this key doesn't really need to be used,
          as we can just loop using `unpublished.values()`.
    """
    if not funcs.server_exists(server=server):
        return False

    print("Playlists")
    print(80 * "-")

    playlists = search_playlists(shared=shared)

    print_playlists(playlists,
                    claim_id=claim_id,
                    sanitize=sanitize,
                    file=file, fdate=fdate, sep=sep)

    print(40 * "-")
    print_summary_playlists(playlists)

    return playlists
