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
"""Zeedit script to download LBRY content and seed blobs.

This script should be run at regular intervals, for example, every 6 hours
so that new claims are downloaded periodically, and at the same time
older files are deleted to free space in the drive.

If `lbrytools` is correctly installed in the Python path, this script
can be executed directly, or through the Python interpreter.
::
    python zeedit.py [config.py]

A configuration module can be passed as first argument to quickly define
all relevant variables used by the `lbrytools` functions.
If no argument is given, or the provided configuration file does not exist,
it will try to load a configuration under the name `zeedit_config.py`.
"""
import importlib
import os
import sys

try:
    import lbrytools as lbryt
    # lbryt = importlib.import_module("lbrytools")
except ModuleNotFoundError as err:
    print(f"{err}")
    print("This package must be in the same directory as this script, "
          "or installed to a Python 'site-packages' directory")
    exit(1)


def usage():
    """Print the usage to the terminal."""
    msg = ["Usage:",
           "  zeedit [config.py]",
           "",
           "A configuration file is optional as first argument.",
           "Otherwise it looks for the default 'zeedit_config.py'."]

    print("\n".join(msg))


if __name__ == "__main__":
    cfg_loaded = False

    # The first argument is the configuration file.
    # Otherwise it tries using a default module.
    if len(sys.argv) > 1:
        config = sys.argv[1]

        if not os.path.exists(config):
            print(f"Configuration file does not exist, '{config}'")
        else:
            spec = importlib.util.spec_from_file_location("cfg",
                                                          location=config)
            cfg = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cfg)
            cfg_loaded = True
            print(f"Configuration will use '{config}'")

    if not cfg_loaded:
        config = "zeedit_config"
        print(f"Configuration will use '{config}.py'")

        try:
            cfg = importlib.import_module(config)
        except ModuleNotFoundError as err:
            print(f"{err}")
            print("Exiting.")
            print()
            usage()
            exit(1)

    # Load the default variables if they are not in the configuration.
    cfg = lbryt.z_defaults(cfg)
    if not cfg:
        print("Exiting.")
        exit(1)

    if not lbryt.server_exists(server=cfg.server):
        exit(1)

    # Download the latest claims from select channels.
    print(80 * "=")
    print("1. Download step")
    info = lbryt.ch_download_latest_multi(channels=cfg.channels,
                                          ddir=cfg.ddir,
                                          own_dir=cfg.own_dir,
                                          save_file=cfg.save_file,
                                          number=cfg.number,
                                          shuffle=cfg.shuffle,
                                          server=cfg.server)
    lbryt.print_multi_list(info, sep=cfg.sm_sep)

    # For a seeding only system, the media files (mp4, mp3, mkv, etc.)
    # will be removed and only the binary blobs will remain.
    # This will also affect the cleanup section.
    print(80 * "=")
    print("2. Seeding step")
    if cfg.seeding_only:
        lbryt.remove_media(never_delete=None,
                           server=cfg.server)
        cfg.what_to_delete = "both"

    # Normal cleanup step.
    # Free space in the disk by removing older media files and blobs according
    # to the configuration.
    print(80 * "=")
    print("3. Cleanup step")
    lbryt.cleanup_space(main_dir=cfg.main_dir,
                        size=cfg.size,
                        percent=cfg.percent,
                        never_delete=cfg.never_delete,
                        what=cfg.what_to_delete,
                        server=cfg.server)

    # Print a summary of the existing downloaded content.
    print(80 * "=")
    print("4. Summary")
    if cfg.sm_summary:
        lbryt.print_summary(show=cfg.sm_show,
                            blocks=cfg.sm_blocks,
                            cid=cfg.sm_cid,
                            blobs=cfg.sm_blobs,
                            size=cfg.sm_size,
                            typ=cfg.sm_type,
                            ch=cfg.sm_ch,
                            ch_online=cfg.sm_ch_online,
                            name=cfg.sm_name,
                            title=cfg.sm_title,
                            path=cfg.sm_path,
                            sanitize=cfg.sm_sanitize,
                            reverse=cfg.sm_reverse,
                            file=cfg.sm_file,
                            fdate=cfg.sm_fdate,
                            sep=cfg.sm_sep,
                            server=cfg.server)
