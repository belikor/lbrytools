#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2021 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
# ----------------------------------------------------------------------------
"""Zeedit script to download LBRY content and seed blobs.

This script should be run at regular intervals, for example, every 6 hours
so that new claims are downloaded periodically, and at the same time
older files are deleted to free space in the drive.

A configuration module `zeedit_config.py` should be placed in the same
directory as this file to quickly define all relevant variables passed
to the `lbrytools` functions.

If `lbrytools` is correctly installed in the Python path, this script
can be executed directly, or through the Python interpreter.
::
    python zeedit.py
"""
import zeedit_config as cfg
import lbrytools as lbryt

# Download the latest claims from select channels.
print(80 * "=")
print("1. Download step")
lbryt.ch_download_latest_multi(channels=cfg.channels,
                               ddir=cfg.ddir,
                               own_dir=cfg.own_dir,
                               number=cfg.number)

# For a seeding only system, the media files (mp4, mp3, mkv, etc.)
# will be removed and only the binary blobs will remain.
# This will also affect the cleanup section.
print(80 * "=")
print("2. Seeding step")
if cfg.seeding_only:
    lbryt.remove_media(never_delete=None)
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
                    what=cfg.what_to_delete)

# Print a summary of the existing downloaded content.
print(80 * "=")
print("4. Summary")
if cfg.sm_summary:
    lbryt.print_summary(show=cfg.sm_show,
                        title=cfg.sm_title,
                        typ=cfg.sm_type,
                        path=cfg.sm_path,
                        cid=cfg.sm_cid,
                        blobs=cfg.sm_blobs,
                        ch=cfg.sm_ch,
                        name=cfg.sm_name,
                        file=cfg.sm_file,
                        date=cfg.sm_date)
