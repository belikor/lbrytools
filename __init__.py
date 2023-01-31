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
from lbrytools.zeed_defaults import z_defaults

from lbrytools.funcs import check_lbry
from lbrytools.funcs import server_exists
from lbrytools.funcs import sanitize_text

from lbrytools.status import list_lbrynet_status
from lbrytools.config import list_lbrynet_settings
from lbrytools.s_wallet import sync_wallet

from lbrytools.search import check_repost
from lbrytools.search import search_item
from lbrytools.parse import parse_claim_file

from lbrytools.resolve_ch import resolve_channel
from lbrytools.resolve_ch import find_channel

from lbrytools.search_ch import ch_search_latest

from lbrytools.sort import sort_items
from lbrytools.sort import sort_invalid
from lbrytools.sort import sort_items_size

from lbrytools.print import print_multi_list
from lbrytools.printf import print_f_claims
from lbrytools.printf import print_summary

from lbrytools.print_claims import print_sch_claims
from lbrytools.print_ch import print_channels
from lbrytools.claims_ch import list_ch_claims

from lbrytools.download import download_single

from lbrytools.download_multi import ch_download_latest
from lbrytools.download_multi import ch_download_latest_multi
from lbrytools.download_multi import redownload_latest
from lbrytools.download_multi import download_claims

from lbrytools.clean import delete_single

from lbrytools.clean_multi import ch_cleanup
from lbrytools.clean_multi import ch_cleanup_multi
from lbrytools.clean_multi import remove_media
from lbrytools.clean_multi import remove_claims

from lbrytools.space import measure_usage
from lbrytools.space import cleanup_space

from lbrytools.blobs import count_blobs
from lbrytools.blobs import count_blobs_all

from lbrytools.blobs_asys import analyze_blobs
from lbrytools.blobs_asys import analyze_channel
from lbrytools.blobs_asys import print_channel_analysis
from lbrytools.blobs_asys import download_missing_blobs

from lbrytools.blobs_act import blob_get
from lbrytools.blobs_act import blobs_action
from lbrytools.blobs_act import redownload_blobs

from lbrytools.blobs_mv import blobs_move
from lbrytools.blobs_mv import blobs_move_all

from lbrytools.blobs_auto import print_network_sd_blobs
from lbrytools.blobs_auto import sd_blobs_compared

from lbrytools.claims_bid import claims_bids
from lbrytools.claims_search import list_trending_claims
from lbrytools.claims_search import list_search_claims

from lbrytools.channels import list_ch_subs
from lbrytools.channels import list_ch_subs_latest

from lbrytools.accounts import list_accounts
from lbrytools.publishes_ch import list_channels
from lbrytools.publishes_claims import list_claims

from lbrytools.playlists import list_playlists

from lbrytools.support import get_all_supports
from lbrytools.support import list_supports
from lbrytools.support import get_base_support
from lbrytools.support import create_support
from lbrytools.support import abandon_support
from lbrytools.support import abandon_support_inv
from lbrytools.support import target_support

from lbrytools.blobs_ratio import print_blobs_ratio

from lbrytools.comments_list import list_comments
from lbrytools.comments_act import create_comment
from lbrytools.comments_act import update_comment
from lbrytools.comments_act import abandon_comment

from lbrytools.peers_claims import list_peers
from lbrytools.peers_claims import list_m_peers
from lbrytools.peers_ch import list_ch_peers
from lbrytools.peers_multi import list_chs_peers
from lbrytools.peers_multi import list_ch_subs_peers

# Use of the modules so that code checkers don't complain (flake8)
True if z_defaults else False

True if check_lbry else False
True if server_exists else False
True if sanitize_text else False

True if list_lbrynet_status else False
True if list_lbrynet_settings else False
True if sync_wallet else False

True if check_repost else False
True if search_item else False
True if parse_claim_file else False

True if resolve_channel else False
True if find_channel else False

True if ch_search_latest else False

True if sort_items else False
True if sort_invalid else False
True if sort_items_size else False

True if print_multi_list else False
True if print_f_claims else False
True if print_summary else False

True if print_sch_claims else False
True if print_channels else False
True if list_ch_claims else False

True if download_single else False

True if ch_download_latest else False
True if ch_download_latest_multi else False
True if redownload_latest else False
True if download_claims else False

True if delete_single else False

True if ch_cleanup else False
True if ch_cleanup_multi else False
True if remove_media else False
True if remove_claims else False

True if measure_usage else False
True if cleanup_space else False

True if count_blobs else False
True if count_blobs_all else False

True if analyze_blobs else False
True if analyze_channel else False
True if print_channel_analysis else False
True if download_missing_blobs else False

True if blob_get else False
True if blobs_action else False
True if redownload_blobs else False

True if blobs_move else False
True if blobs_move_all else False

True if print_network_sd_blobs else False
True if sd_blobs_compared else False

True if claims_bids else False
True if list_trending_claims else False
True if list_search_claims else False

True if list_ch_subs else False
True if list_ch_subs_latest else False

True if list_accounts else False
True if list_channels else False
True if list_claims else False

True if list_playlists else False

True if get_all_supports else False
True if list_supports else False
True if get_base_support else False
True if create_support else False
True if abandon_support else False
True if abandon_support_inv else False
True if target_support else False

True if print_blobs_ratio else False

True if list_comments else False
True if create_comment else False
True if update_comment else False
True if abandon_comment else False

True if list_peers else False
True if list_m_peers else False
True if list_ch_peers else False
True if list_chs_peers else False
True if list_ch_subs_peers else False
