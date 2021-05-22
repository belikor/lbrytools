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
"""Functions to help with downloading and managing LBRY content.

The daemon must be started before using the majority of these tools.
::
    lbrynet start

We use the `requests` module to send json messages to the running JSON-RPC
in `localhost`.
::
    import requests
    
    server = "http://localhost:5279"
    json = {"method": "get",
            "params": {"uri": "astream#bcd03a"}}
    
    requests.post(server, json=json).json()

In the past the `subprocess` module was used to run the `lbrynet` command.
::
    lbrynet get 'lbry://...'

That is
::
    import subprocess
    
    cmd = ["lbrynet", "get", "lbry://..."]
    output = subprocess.run(cmd, capture_output=True, check=True, text=True)
    data = json.loads(output.stdout)

Developed and tested with Python 3.8.
"""
from lbrytools.funcs import check_lbry
from lbrytools.blobs import get_blobs

from lbrytools.search import check_repost
from lbrytools.search import search_item
from lbrytools.search import ch_search_latest
from lbrytools.search import find_channel
from lbrytools.search import sort_items
from lbrytools.search import parse_claim_file

from lbrytools.print import print_summary
from lbrytools.print import print_multi_list

from lbrytools.download import download_single
from lbrytools.download import ch_download_latest
from lbrytools.download import ch_download_latest_multi
from lbrytools.download import redownload_latest
from lbrytools.download import redownload_claims

from lbrytools.clean import delete_single
from lbrytools.clean import measure_usage
from lbrytools.clean import cleanup_space
from lbrytools.clean import remove_media

# Use of the modules so that code checkers don't complain (flake8)
True if check_lbry else False
True if get_blobs else False

True if check_repost else False
True if search_item else False
True if ch_search_latest else False
True if find_channel else False
True if sort_items else False
True if parse_claim_file else False

True if print_summary else False

True if download_single else False
True if ch_download_latest else False
True if ch_download_latest_multi else False
True if redownload_latest else False
True if redownload_claims else False

True if delete_single else False
True if measure_usage else False
True if cleanup_space else False
True if remove_media else False
