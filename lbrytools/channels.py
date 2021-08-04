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
import os
import requests
import time


def channel_subs(shared=True, notifications=True,
                 file=None, fdate=False,
                 server="http://localhost:5279"):
    """Display the channel subscriptions.

    Parameters
    ----------
    shared: bool, optional
        It defaults to `True`, in which case it uses the shared database
        synchronized with Odysee online.
        If it is `False` it will use only the local database
        to the LBRY Desktop application.
    notifications: bool, optional
        It defaults to `True`, in which case it will show only
        the channels for which notifications have been enabled.
        If it is `False` it will show only the channels
        with disabled notifications.
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
    list of dict
        It returns the list of dictionaries representing
        the filtered channels depending on the values of `shared`
        and `notifications`.

        Each dictionary has two elements, `'uri'` which is
        the `'permanent_url'` of the channel, and `'notificationsDisabled'`
        which is a boolean value, indicating whether the notification
        is enabled for that channel.
    False
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

    print("Channel subscriptions")
    print(80 * "-")
    print(f"Synchronization: {sync}")
    print(f"Notifications: {bool(notifications)}")

    following_local = r_local["value"]["following"]

    if "shared" in result:
        following_shared = r_shared["value"]["following"]

    if shared and "shared" in result:
        print(f"Database: shared")
        channels = following_shared
        n_items = len(following_shared)
    else:
        if shared:
            print("No shared database, will use local")
        else:
            print(f"Database: local")
        channels = following_local
        n_items = len(following_local)

    out = []
    ch_filtered = []

    for it, channel in enumerate(channels, start=1):
        line = f"{it:3d}/{n_items:3d}, "
        uri, cid = channel["uri"].lstrip("lbry://").split("#")
        uri = uri + "#" + cid[0:3] + ","

        if "notificationsDisabled" in channel:
            ch_notifications = not channel["notificationsDisabled"]
        else:
            ch_notifications = False

        line += f"{uri:34s} notifications: {ch_notifications}"

        if ((notifications and not ch_notifications)
                or (not notifications and ch_notifications)):
            continue

        ch_filtered.append(channel)
        out += [line]

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

    return ch_filtered
