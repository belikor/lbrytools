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
"""List the settings that are used by the lbrynet daemon."""
import requests

import lbrytools.funcs as funcs


def get_settings(server="http://localhost:5279"):
    """Get the lbrynet settings with some formatting applied."""
    if not funcs.server_exists(server=server):
        return None

    msg = {"method": "settings_get"}
    output = requests.post(server, json=msg).json()
    result = output["result"]

    config = {}

    keys = ["jurisdiction"]

    keys_int = ["blob_lru_cache_size", "blob_storage_limit",
                "concurrent_blob_announcers", "concurrent_hub_requests",
                "concurrent_reflector_uploads", "max_connections_per_download",
                "network_storage_limit",
                "prometheus_port",
                "split_buckets_under_index",
                "tcp_port", "transaction_cache_size", "udp_port",
                "video_bitrate_maximum", "volume_analysis_time"]

    keys_float = ["blob_download_timeout", "download_timeout",
                  "fixed_peer_delay", "hub_timeout",
                  "node_rpc_timeout", "peer_connect_timeout"]

    keys_bool = ["announce_head_and_sd_only", "reflect_streams",
                 "save_blobs", "save_files", "save_resolved_claims",
                 "share_usage_data", "streaming_get", "track_bandwidth",
                 "use_upnp"]

    keys_str = ["allowed_origin", "api", "audio_encoder",
                "blockchain_name", "coin_selection_strategy",
                "config", "data_dir", "download_dir",
                "ffmpeg_path", "max_wallet_server_fee", "network_interface",
                "streaming_server", "video_encoder", "video_scaler",
                "volume_filter", "wallet_dir"]

    keys_lst = ["components_to_skip", "fixed_peers", "known_dht_nodes",
                "lbryum_servers", "reflector_servers", "wallets"]

    for k in keys:
        value = result.get(k, None)
        config[k] = f"{k}: {value}"

    k_am = result["max_key_fee"]["amount"]
    k_cr = result["max_key_fee"]["currency"]
    v1 = f"- amount:   {k_am}"
    v2 = f"- currency: {k_cr}"
    config["max_key_fee"] = "max_key_fee:" + "\n" + v1 + "\n" + v2

    for k in keys_int:
        value = result.get(k, None)
        config[k] = f"{k}: {value}"

    for k in keys_float:
        value = result.get(k, None)
        config[k] = f"{k}: {value:.1f}"

    for k in keys_bool:
        value = str(result.get(k, None))
        config[k] = f"{k}: {value}"

    for k in keys_str:
        value = result.get(k, None)
        config[k] = f"{k}: '{value}'"

    for k in keys_lst:
        values = result.get(k, None)
        out = [f"{k}:"]

        for v in values:
            if isinstance(v, list):
                v1 = v[0]
                v2 = v[1]
                out.append(f"- {v1}:{v2}")
            else:
                out.append(f"- '{v}'")

        if len(values) < 1:
            out[0] = out[0] + " []"

        config[k] = "\n".join(out)

    return config


def list_lbrynet_settings(file=None, fdate=False,
                          server="http://localhost:5279"):
    """Get and print a summary of the settings of the lbrynet daemon.

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
        Various keys with a formatted string of information;
        each key can be printed.
        - `'config'`
        - `'data_dir'`
        - `'download_dir'`
        - `'wallet_dir'`
        - `'wallets'`
        - `'api'`
        - `'streaming_get'`
        - `'streaming_server'`
        - `'allowed_origin'`
        - `'share_usage_data'`
        - `'components_to_skip'`
        - `'network_interface'`
        - `'node_rpc_timeout'`
        - `'prometheus_port'`
        - `'blockchain_name'`
        - `'coin_selection_strategy'`
        - `'announce_head_and_sd_only'`
        - `'blob_download_timeout'`
        - `'blob_lru_cache_size'`
        - `'blob_storage_limit'`
        - `'concurrent_blob_announcers'`
        - `'concurrent_hub_requests'`
        - `'concurrent_reflector_uploads'`
        - `'network_storage_limit'`
        - `'max_connections_per_download'`
        - `'download_timeout'`
        - `'save_blobs'`
        - `'save_files'`
        - `'save_resolved_claims'`
        - `'peer_connect_timeout'`
        - `'fixed_peer_delay'`
        - `'fixed_peers'`
        - `'use_upnp'`
        - `'tcp_port'`
        - `'udp_port'`
        - `'known_dht_nodes'`
        - `'hub_timeout'`
        - `'jurisdiction'`
        - `'lbryum_servers'`
        - `'reflect_streams'`
        - `'reflector_servers'`
        - `'max_key_fee'`
        - `'max_wallet_server_fee'`
        - `'split_buckets_under_index'`
        - `'track_bandwidth'`
        - `'transaction_cache_size'`
        - `'ffmpeg_path'`
        - `'audio_encoder'`
        - `'video_bitrate_maximum'`
        - `'video_encoder'`
        - `'video_scaler'`
        - `'volume_analysis_time'`
        - `'volume_filter'`
    False
        If there is a problem, like a non-running server,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return None

    config = get_settings(server=server)

    if not config:
        return False

    out = [config["config"],
           config["data_dir"],
           config["download_dir"],
           config["wallet_dir"],
           config["wallets"], "",

           config["api"],
           config["streaming_get"],
           config["streaming_server"],
           config["allowed_origin"],
           config["share_usage_data"],
           config["components_to_skip"], "",

           config["network_interface"],
           config["node_rpc_timeout"],
           config["prometheus_port"], "",

           config["blockchain_name"],
           config["coin_selection_strategy"], "",

           config["announce_head_and_sd_only"],
           config["blob_download_timeout"],
           config["blob_lru_cache_size"],
           config["blob_storage_limit"],
           config["concurrent_blob_announcers"],
           config["concurrent_hub_requests"],
           config["concurrent_reflector_uploads"],
           config["network_storage_limit"],
           config["max_connections_per_download"], "",

           config["download_timeout"],
           config["save_blobs"],
           config["save_files"],
           config["save_resolved_claims"], "",

           config["peer_connect_timeout"],
           config["fixed_peer_delay"],
           config["fixed_peers"], "",

           config["use_upnp"],
           config["tcp_port"],
           config["udp_port"], "",

           config["known_dht_nodes"], "",

           config["hub_timeout"],
           config["jurisdiction"],
           config["lbryum_servers"], "",

           config["reflect_streams"],
           config["reflector_servers"], "",

           config["max_key_fee"],
           config["max_wallet_server_fee"], "",

           config["split_buckets_under_index"],
           config["track_bandwidth"],
           config["transaction_cache_size"], "",

           config["ffmpeg_path"],
           config["audio_encoder"],
           config["video_bitrate_maximum"],
           config["video_encoder"],
           config["video_scaler"],
           config["volume_analysis_time"],
           config["volume_filter"]]

    funcs.print_content(out, file=file, fdate=fdate)

    return config
