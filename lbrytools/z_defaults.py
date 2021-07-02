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
"""Set default variables for the configuration file used in `zeedit.py`

This function needs to be used after the configuration has been loaded,
and before the actual functions from `lbrytools` are called.
"""
import os


def z_defaults(cfg):
    """Define the default variables for the zeedit script."""
    config = dir(cfg)

    print(80 * "-")
    # 0. Server
    if "server" not in config:
        cfg.server = "http://localhost:5279"
        print(f"server: '{cfg.server}' (use default)")
    else:
        print(f"server: '{cfg.server}'")

    # 1. Download
    if "channels" not in config:
        print("Error: 'channels' list is mandatory in the configuration")
        return False
    else:
        print(f"channels: [{cfg.channels[0]}, ...]")

    if "ddir" not in config:
        cfg.ddir = os.path.expanduser("~")
        print(f"ddir: '{cfg.ddir}' (use default)")
    else:
        print(f"ddir: '{cfg.ddir}'")

    if "own_dir" not in config:
        cfg.own_dir = True
        print(f"own_dir: {cfg.own_dir} (use default)")
    else:
        print(f"own_dir: {cfg.own_dir}")

    if "number" not in config:
        cfg.number = 2
        print(f"number: {cfg.number} (use default)")
    else:
        print(f"number: {cfg.number}")

    if "shuffle" not in config:
        cfg.shuffle = True
        print(f"shuffle: {cfg.shuffle} (use default)")
    else:
        print(f"shuffle: {cfg.shuffle}")

    # 2. Seeding
    if "seeding_only" not in config:
        cfg.seeding_only = False
        print(f"seeding_only: {cfg.seeding_only} (use default)")
    else:
        print(f"seeding_only: {cfg.seeding_only}")

    # 3. Cleanup
    if "main_dir" not in config:
        cfg.main_dir = os.path.expanduser("~")
        print(f"main_dir: '{cfg.main_dir}' (use default)")
    else:
        print(f"main_dir: '{cfg.main_dir}'")

    if "size" not in config:
        cfg.size = 1000
        print(f"size: {cfg.size} (use default)")
    else:
        print(f"size: {cfg.size}")

    if "percent" not in config:
        cfg.percent = 90
        print(f"percent: {cfg.percent} (use default)")
    else:
        print(f"percent: {cfg.percent}")

    if "never_delete" not in config:
        cfg.never_delete = None
        print(f"never_delete: {cfg.never_delete} (use default)")
    else:
        print(f"never_delete: [{cfg.never_delete[0]}, ...]")

    if "what_to_delete" not in config:
        cfg.what_to_delete = "media"
        print(f"what_to_delete: '{cfg.what_to_delete}' (use default)")
    else:
        print(f"what_to_delete: '{cfg.what_to_delete}'")

    # 4. Summary
    if "sm_summary" not in config:
        cfg.sm_summary = True
        print(f"sm_summary: {cfg.sm_summary} (use default)")
    else:
        print(f"sm_summary: {cfg.sm_summary}")

    if "sm_file" not in config:
        cfg.sm_file = os.path.join(cfg.ddir, "lbry_summary.txt")
        print(f"sm_file: '{cfg.sm_file}' (use default)")
    else:
        print(f"sm_file: '{cfg.sm_file}'")

    if "sm_fdate" not in config:
        cfg.sm_fdate = True
        print(f"sm_fdate: {cfg.sm_fdate} (use default)")
    else:
        print(f"sm_fdate: {cfg.sm_fdate}")

    if "sm_show" not in config:
        cfg.sm_show = "all"
        print(f"sm_show: '{cfg.sm_show}' (use default)")
    else:
        print(f"sm_show: '{cfg.sm_show}'")

    if "sm_title" not in config:
        cfg.sm_title = False
        print(f"sm_title: {cfg.sm_title} (use default)")
    else:
        print(f"sm_title: {cfg.sm_title}")

    if "sm_type" not in config:
        cfg.sm_type = False
        print(f"sm_type: {cfg.sm_type} (use default)")
    else:
        print(f"sm_type: {cfg.sm_type}")

    if "sm_path" not in config:
        cfg.sm_path = False
        print(f"sm_path: {cfg.sm_path} (use default)")
    else:
        print(f"sm_path: {cfg.sm_path}")

    if "sm_cid" not in config:
        cfg.sm_cid = True
        print(f"sm_cid: {cfg.sm_cid} (use default)")
    else:
        print(f"sm_cid: {cfg.sm_cid}")

    if "sm_blobs" not in config:
        cfg.sm_blobs = True
        print(f"sm_blobs: {cfg.sm_blobs} (use default)")
    else:
        print(f"sm_blobs: {cfg.sm_blobs}")

    if "sm_ch" not in config:
        cfg.sm_ch = False
        print(f"sm_ch: {cfg.sm_ch} (use default)")
    else:
        print(f"sm_ch: {cfg.sm_ch}")

    if "sm_ch_online" not in config:
        cfg.sm_ch_online = True
        print(f"sm_ch_online: {cfg.sm_ch_online} (use default)")
    else:
        print(f"sm_ch_online: {cfg.sm_ch_online}")

    if "sm_name" not in config:
        cfg.sm_name = True
        print(f"sm_name: {cfg.sm_name} (use default)")
    else:
        print(f"sm_name: {cfg.sm_name}")

    return cfg
