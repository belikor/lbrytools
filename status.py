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
"""List the status of the lbrynet daemon."""
import requests

import lbrytools.funcs as funcs


def get_status(server="http://localhost:5279"):
    """Get the lbrynet status with some formatting applied."""
    if not funcs.server_exists(server=server):
        return None

    msg = {"method": "status"}
    output = requests.post(server, json=msg).json()
    result = output["result"]

    status = {}

    s = result["background_downloader"]
    dw1 = s.get("available_free_space_mb", 0) / 1024
    dw1 = "Availabe free space: " + f"{dw1:.4f} GB"
    dw2 = f"Ongoing download: " + str(s.get("ongoing_download", None))
    dw3 = "Running: " + str(s.get("running", None))
    status["background_downloader"] = dw3 + "\n" + dw2 + "\n" + dw1

    s = result["blob_manager"]
    c = s["connections"]
    bm0 = "Connections:"
    bm1 = "- Incoming bps: " + str(c.get("incoming_bps", None))
    bm2 = "- Max incoming mbs: " + str(c.get("max_incoming_mbs", 0))
    bm3 = "- Max outgoing mbs: " + str(c.get("max_outgoing_mbs", 0))
    bm4 = "- Outgoing bps: " + str(c.get("outgoing_bps", None))
    bm5 = "- Total incoming mbs: " + str(c.get("total_incoming_mbs", 0))
    bm6 = "- Total outgoing mbs: " + str(c.get("total_outgoing_mbs", 0))
    bm7 = "- Total received: " + str(c.get("total_received", 0))
    bm8 = "- Total sent: " + str(c.get("total_sent", 0))
    bm9 = "Finished blobs: " + str(s.get("finished_blobs", None))
    status["blob_manager"] = (bm0 + "\n"
                              + bm1 + "\n" + bm2 + "\n" + bm3 + "\n"
                              + bm4 + "\n" + bm5 + "\n" + bm6 + "\n"
                              + bm7 + "\n" + bm8 + "\n" + bm9)

    s = result["dht"]
    dht1 = "Node ID: " + s.get("node_id", "None")
    dht2 = str(s.get("peers_in_routing_table", None))
    dht2 = "Peers in routing table: " + dht2
    status["dht"] = dht1 + "\n" + dht2

    s = result["disk_space"]
    dsk1 = s.get("content_blobs_storage_used_mb", 0) / 1024
    dsk1 = "Content blobs used storage: " + f"{dsk1:.4f} GB"
    dsk2 = s.get("published_blobs_storage_used_mb", 0) / 1024
    dsk2 = "Published blobs used storage: " + f"{dsk2:.4f} GB"
    dsk3 = f"Running: " + str(s.get("running", None))
    dsk4 = s.get("seed_blobs_storage_used_mb", 0) / 1024
    dsk4 = "Seed blobs used storage: " + f"{dsk4:.4f} GB"
    dsk5 = s.get("total_used_mb", 0) / 1024
    dsk5 = "Total usage: " + f"{dsk5:.4f} GB"
    status["disk_space"] = (dsk3 + "\n"
                            + dsk2 + "\n" + dsk1 + "\n" + dsk4 + "\n"
                            + dsk5)

    s = result["ffmpeg_status"]
    ffm1 = str(s.get("analyze_audio_volume", None))
    ffm1 = "Analyze audio volume: " + ffm1
    ffm2 = "Available: " + str(s.get("available", None))
    ffm3 = "ffmpeg: " + s.get("which", "None")
    status["ffmpeg_status"] = ffm1 + "\n" + ffm2 + "\n" + ffm3

    s = result["file_manager"].get("managed_files", None)
    status["file_manager"] = f"Managed files: {s}"

    s = result["startup_status"]
    st1 = str(s.get("background_downloader", None))
    st1 = "background_downloader: " + st1
    st2 = "blob_manager: " + str(s.get("blob_manager", None))
    st3 = "database: " + str(s.get("database", None))
    st4 = "dht: " + str(s.get("dht", None))
    st5 = "disk_space: " + str(s.get("disk_space", None))
    st6 = str(s.get("exchange_rate_manager", None))
    st6 = "exchange_rate_manager: " + st6
    st7 = "file_manager: " + str(s.get("file_manager", None))
    st8 = "hash_announcer: " + str(s.get("hash_announcer", None))
    st9 = str(s.get("libtorrent_component", None))
    st9 = "libtorrent_component: " + st9
    st10 = str(s.get("peer_protocol_server", None))
    st10 = "peer_protocol_server: " + st10
    st11 = "upnp: " + str(s.get("upnp", None))
    st12 = "wallet: " + str(s.get("wallet", None))
    st13 = str(s.get("wallet_server_payments", None))
    st13 = "wallet_server_payments: " + st13
    status["startup_status"] = (st1 + "\n" + st2 + "\n" + st3 + "\n"
                                + st4 + "\n" + st5 + "\n" + st6 + "\n"
                                + st7 + "\n" + st8 + "\n" + st9 + "\n"
                                + st10 + "\n" + st11 + "\n" + st12 + "\n"
                                + st13)

    s = result["upnp"]
    upnp1 = "aioupnp version: " + str(s.get("aioupnp_version", None))
    upnp2 = "DHT redirect set: " + str(s.get("dht_redirect_set", None))
    upnp3 = "External IP: " + str(s.get("external_ip", None))
    upnp4 = "Gateway: " + str(s.get("gateway", None))
    upnp5 = "peer redirect set: " + str(s.get("peer_redirect_set", None))
    upnp6 = "redirects: " + str(s.get("redirects", None))
    status["upnp"] = (upnp1 + "\n" + upnp2 + "\n" + upnp3 + "\n"
                      + upnp4 + "\n" + upnp5 + "\n" + upnp6)

    s = result["wallet"]
    wall1 = "Blocks: " + str(s.get("blocks", None))
    wall2 = "Blocks behind: " + str(s.get("blocks_behind", None))
    wall3 = "Connected server: " + str(s.get("connected", None))
    wall3a = str(s["connected_features"].get("server_version", None))
    wall3a = "- Server version: " + wall3a
    wall3b = str(s["connected_features"].get("trending_algorithm", None))
    wall3b = "- Trending algorithm: " + wall3b
    status["wallet"] = (wall1 + "\n" + wall2 + "\n" + wall3 + "\n"
                        + wall3a + "\n" + wall3b)

    return status


def list_lbrynet_status(file=None, fdate=False,
                        server="http://localhost:5279"):
    """Get and print a summary of the lbrynet status.

    Parameters
    ----------
    file: str, optional
        It defaults to `None`.
        It must be a writable path to which the summary will be written.
        Otherwise the summary will be printed to the terminal.
    fdate: bool, optional
        It defaults to `False`.
        If it is `True` it will add the date to the name of the summary file.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the local `lbrynet` daemon used to sign
        the data.

    Returns
    -------
    dict
        Various keys with formatted paragraphs of information;
        each key can be printed.
        - `'dht'`
        - `'disk_space'`
        - `'background_downloader'`
        - `'blob_manager'`
        - `'ffmpeg_status'`
        - `'file_manager'`
        - `'startup_status'`
        - `'upnp'`
        - `'wallet'`
    False
        If there is a problem, like a non-running server,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return None

    status = get_status(server=server)

    if not status:
        return False

    out = ["DHT", 40 * "-", status["dht"], "",
           "Disk space", 40 * "-", status["disk_space"], "",
           "Background downloader",
           40 * "-", status["background_downloader"], "",
           "Blob manager", 40 * "-", status["blob_manager"], "",
           "ffmpeg status", 40 * "-", status["ffmpeg_status"], "",
           "File manager", 40 * "-", status["file_manager"], "",
           "Startup status", 40 * "-", status["startup_status"], "",
           "Upnp", 40 * "-", status["upnp"], "",
           "Wallet", 40 * "-", status["wallet"]]

    funcs.print_content(out, file=file, fdate=fdate)

    return status
