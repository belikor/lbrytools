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
import os
import requests
import time


def list_playlists(shared=True,
                   file=None, fdate=False,
                   server="http://localhost:5279"):
    """Display the playlists.

    Parameters
    ----------
    shared: bool, optional
        It defaults to `True`, in which case it uses the shared database
        synchronized with Odysee online.
        If it is `False` it will use only the local database
        to the LBRY Desktop application.
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

    print("Playlists")
    print(80 * "-")
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
    n_favs = len(pl_favorites["items"])
    time_favs = time.localtime(int(pl_favorites["updatedAt"]))
    time_favs = time.strftime("%Y-%m-%d_%H%M", time_favs)

    pl_watchlater = pl_builtin["watchlater"]
    n_later = len(pl_watchlater["items"])
    time_later = time.localtime(int(pl_watchlater["updatedAt"]))
    time_later = time.strftime("%Y-%m-%d_%H%M", time_later)

    out = [f"Favorites, updated: {time_favs}"]
    out2 = [f"Watch later, updated: {time_later}"]

    for it, item in enumerate(pl_favorites["items"], start=1):
        line = f"{it:3d}/{n_favs:3d}, "
        uri, cid = item.lstrip("lbry://").split("#")
        uri = uri + "#" + cid[0:3]
        out += [line + f"{uri}"]

    for it, item in enumerate(pl_watchlater["items"], start=1):
        line = f"{it:3d}/{n_later:3d}, "
        uri, cid = item.lstrip("lbry://").split("#")
        uri = uri + "#" + cid[0:3]
        out2 += [line + f"{uri}"]

    out3 = []

    for it, k in enumerate(pl_unpub, start=1):
        updated = time.localtime(int(pl_unpub[k]["updatedAt"]))
        updated = time.strftime("%Y-%m-%d_%H%M", updated)
        name = pl_unpub[k]["name"]
        title = f"{name}, updated: {updated}"

        items = pl_unpub[k]["items"]
        n_items = len(items)

        elems = []
        for itt, item in enumerate(items, start=1):
            line = f"{itt:3d}/{n_items:3d}, "
            uri, cid = item.lstrip("lbry://").split("#")
            uri = uri + "#" + cid[0:3]
            line = line + f"{uri}"
            elems.append(line)

        lines = "\n".join(elems)
        out3 += [f"{title}\n"
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
        print("", file=fd)
        print("\n".join(out3), file=fd)
        fd.close()
        print(f"Summary written: {file}")
    else:
        print("\n".join(out))
        print("")
        print("\n".join(out2))
        print("")
        print("\n".join(out3))

    return True
