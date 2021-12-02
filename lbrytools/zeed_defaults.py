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

    lines = []
    # 0. Server
    if "server" not in config:
        cfg.server = "http://localhost:5279"
        lines += [f"server: '{cfg.server}' (default value)"]
    else:
        lines += [f"server: '{cfg.server}'"]

    # 1. Download
    if "channels" not in config:
        print("Error: 'channels' list is mandatory in the configuration")
        return False
    else:
        if not cfg.channels:
            print("Error: 'channels' list is must have at least one element")
            return False

        n = len(cfg.channels)
        limit = 3
        if n < limit:
            limit = int(n)

        sub = "["
        for i in range(0, limit):
            sub += str(cfg.channels[i]) + ", "
        sub += "...]"

        lines += [f"channels: {sub}"]

    if "ddir" not in config:
        cfg.ddir = os.path.expanduser("~")
        lines += [f"ddir: '{cfg.ddir}' (default value)"]
    else:
        lines += [f"ddir: '{cfg.ddir}'"]

    if "own_dir" not in config:
        cfg.own_dir = True
        lines += [f"own_dir: {cfg.own_dir} (default value)"]
    else:
        lines += [f"own_dir: {cfg.own_dir}"]

    if "save_file" not in config:
        cfg.save_file = True
        lines += [f"save_file: {cfg.save_file} (default value)"]
    else:
        lines += [f"save_file: {cfg.save_file}"]

    if "number" not in config:
        cfg.number = 2
        lines += [f"number: {cfg.number} (default value)"]
    else:
        lines += [f"number: {cfg.number}"]

    if "shuffle" not in config:
        cfg.shuffle = True
        lines += [f"shuffle: {cfg.shuffle} (default value)"]
    else:
        lines += [f"shuffle: {cfg.shuffle}"]

    # 2. Seeding
    if "seeding_only" not in config:
        cfg.seeding_only = False
        lines += [f"seeding_only: {cfg.seeding_only} (default value)"]
    else:
        lines += [f"seeding_only: {cfg.seeding_only}"]

    # 3. Cleanup
    if "main_dir" not in config:
        cfg.main_dir = os.path.expanduser("~")
        lines += [f"main_dir: '{cfg.main_dir}' (default value)"]
    else:
        lines += [f"main_dir: '{cfg.main_dir}'"]

    if "size" not in config:
        cfg.size = 1000
        lines += [f"size: {cfg.size} (default value)"]
    else:
        lines += [f"size: {cfg.size}"]

    if "percent" not in config:
        cfg.percent = 90
        lines += [f"percent: {cfg.percent} (default value)"]
    else:
        lines += [f"percent: {cfg.percent}"]

    if "never_delete" not in config:
        cfg.never_delete = None
        lines += [f"never_delete: {cfg.never_delete} (default value)"]
    else:
        if not cfg.never_delete:
            cfg.never_delete = None
            lines += [f"never_delete: {cfg.never_delete} (default value)"]
        else:
            n = len(cfg.never_delete)
            limit = 3
            if n < limit:
                limit = int(n)

            sub = "["
            for i in range(0, limit):
                sub += str(cfg.never_delete[i]) + ", "
            sub += "...]"

            lines += [f"never_delete: {sub}"]

    if "what_to_delete" not in config:
        cfg.what_to_delete = "media"
        lines += [f"what_to_delete: '{cfg.what_to_delete}' (default value)"]
    else:
        lines += [f"what_to_delete: '{cfg.what_to_delete}'"]

    # 4. Summary
    if "sm_summary" not in config:
        cfg.sm_summary = True
        lines += [f"sm_summary: {cfg.sm_summary} (default value)"]
    else:
        lines += [f"sm_summary: {cfg.sm_summary}"]

    if "sm_file" not in config:
        cfg.sm_file = os.path.join(cfg.ddir, "lbry_summary.txt")
        lines += [f"sm_file: '{cfg.sm_file}' (default value)"]
    else:
        lines += [f"sm_file: '{cfg.sm_file}'"]

    if "sm_fdate" not in config:
        cfg.sm_fdate = True
        lines += [f"sm_fdate: {cfg.sm_fdate} (default value)"]
    else:
        lines += [f"sm_fdate: {cfg.sm_fdate}"]

    if "sm_sep" not in config:
        cfg.sm_sep = ";"
        lines += [f"sm_sep: '{cfg.sm_sep}' (default value)"]
    else:
        lines += [f"sm_sep: '{cfg.sm_sep}'"]

    if "sm_show" not in config:
        cfg.sm_show = "all"
        lines += [f"sm_show: '{cfg.sm_show}' (default value)"]
    else:
        lines += [f"sm_show: '{cfg.sm_show}'"]

    if "sm_blocks" not in config:
        cfg.sm_blocks = False
        lines += [f"sm_blocks: '{cfg.sm_blocks}' (default value)"]
    else:
        lines += [f"sm_blocks: '{cfg.sm_blocks}'"]

    if "sm_cid" not in config:
        cfg.sm_cid = True
        lines += [f"sm_cid: {cfg.sm_cid} (default value)"]
    else:
        lines += [f"sm_cid: {cfg.sm_cid}"]

    if "sm_blobs" not in config:
        cfg.sm_blobs = True
        lines += [f"sm_blobs: {cfg.sm_blobs} (default value)"]
    else:
        lines += [f"sm_blobs: {cfg.sm_blobs}"]

    if "sm_size" not in config:
        cfg.sm_size = True
        lines += [f"sm_size: {cfg.sm_size} (default value)"]
    else:
        lines += [f"sm_size: {cfg.sm_size}"]

    if "sm_type" not in config:
        cfg.sm_type = False
        lines += [f"sm_type: {cfg.sm_type} (default value)"]
    else:
        lines += [f"sm_type: {cfg.sm_type}"]

    if "sm_ch" not in config:
        cfg.sm_ch = False
        lines += [f"sm_ch: {cfg.sm_ch} (default value)"]
    else:
        lines += [f"sm_ch: {cfg.sm_ch}"]

    if "sm_ch_online" not in config:
        cfg.sm_ch_online = True
        lines += [f"sm_ch_online: {cfg.sm_ch_online} (default value)"]
    else:
        lines += [f"sm_ch_online: {cfg.sm_ch_online}"]

    if "sm_name" not in config:
        cfg.sm_name = True
        lines += [f"sm_name: {cfg.sm_name} (default value)"]
    else:
        lines += [f"sm_name: {cfg.sm_name}"]

    if "sm_title" not in config:
        cfg.sm_title = False
        lines += [f"sm_title: {cfg.sm_title} (default value)"]
    else:
        lines += [f"sm_title: {cfg.sm_title}"]

    if "sm_path" not in config:
        cfg.sm_path = False
        lines += [f"sm_path: {cfg.sm_path} (default value)"]
    else:
        lines += [f"sm_path: {cfg.sm_path}"]

    if "sm_sanitize" not in config:
        cfg.sm_sanitize = False
        lines += [f"sm_sanitize: {cfg.sm_sanitize} (default value)"]
    else:
        lines += [f"sm_sanitize: {cfg.sm_sanitize}"]

    print(80 * "-")
    print("\n".join(lines))

    return cfg
