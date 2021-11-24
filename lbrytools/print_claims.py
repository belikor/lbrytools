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
"""Functions to print found claims from the network.

The claims are obtained from calling `claim_search`.
"""
import time

import lbrytools.funcs as funcs


def print_tr_claims(claims,
                    claim_id=False, sanitize=False,
                    file=None, fdate=None, sep=";"):
    """Print generic claims, particularly trending or searched claims."""
    n_claims = len(claims)

    out = []
    for num, claim in enumerate(claims, start=1):
        vtype = claim["value_type"]

        if "stream_type" in claim["value"]:
            stream_type = claim["value"].get("stream_type")
        else:
            stream_type = 8 * "_"

        if "source" in claim["value"]:
            mtype = claim["value"]["source"].get("media_type", 14 * "_")
        else:
            mtype = 14 * "_"

        if "signing_channel" in claim:
            channel = claim["signing_channel"].get("name", 14 * "_")
            if sanitize:
                channel = funcs.sanitize_name(channel)
        else:
            channel = 14 * "_"

        name = claim["name"]
        if sanitize:
            name = funcs.sanitize_name(claim["name"])

        line = f"{num:2d}/{n_claims:2d}" + f"{sep} "

        if claim_id:
            line += claim["claim_id"] + f"{sep} "

        line += f"{vtype:9s}" + f"{sep} "
        line += f"{stream_type:9s}" + f"{sep} "
        line += f"{mtype:17s}" + f"{sep} "
        line += f"{channel:40s}" + f"{sep} "
        line += f'"{name}"'
        out.append(line)

    content = funcs.print_content(out, file=file, fdate=fdate)

    return content


def print_sch_claims(claims,
                     blocks=False, claim_id=False,
                     typ=False, ch_name=False,
                     title=False, sanitize=False,
                     start=1, end=0,
                     reverse=False,
                     file=None, fdate=None, sep=";"):
    """Print the provided list of claims, particularly those from a channel."""
    n_claims = len(claims)

    if reverse:
        claims.reverse()

    out = []
    for num, claim in enumerate(claims, start=1):
        if num < start:
            continue
        if end != 0 and num > end:
            break

        creation = claim["meta"]["creation_height"]
        height = claim["height"]
        res_time = int(claim["value"].get("release_time", 0))
        res_time = time.strftime("%Y-%m-%d_%H:%M:%S%z",
                                 time.localtime(res_time))

        vtype = claim["value_type"]

        if "stream_type" in claim["value"]:
            stream_type = claim["value"].get("stream_type")
        else:
            stream_type = 8 * "_"

        if "source" in claim["value"]:
            mtype = claim["value"]["source"].get("media_type", 14 * "_")
        else:
            mtype = 14 * "_"

        if "signing_channel" in claim:
            # channel = claim["signing_channel"].get("name", 14 * "_")
            channel = claim["signing_channel"]["canonical_url"]
            channel = channel.lstrip("lbry://")
            if sanitize:
                channel = funcs.sanitize_name(channel)
        else:
            channel = 14 * "_"

        if sanitize:
            channel = funcs.sanitize_name(channel)

        name = claim["name"]

        if title and "title" in claim["value"]:
            name = claim["value"]["title"]

        if sanitize:
            name = funcs.sanitize_name(name)

        length_s = 0
        rem_s = 0
        rem_min = 0

        if "video" in claim["value"] and "duration" in claim["value"]["video"]:
            length_s = claim["value"]["video"]["duration"]
        if "audio" in claim["value"] and "duration" in claim["value"]["audio"]:
            length_s = claim["value"]["audio"]["duration"]

        rem_s = length_s % 60
        rem_min = length_s // 60

        size = 0
        if "source" in claim["value"] and "size" in claim["value"]["source"]:
            size = float(claim["value"]["source"]["size"])
            size = size/(1024**2)  # to MB

        line = f"{num:4d}/{n_claims:4d}" + f"{sep} "

        if blocks:
            line += f"{creation:8d}" + f"{sep}"
            line += f"{height:8d}" + f"{sep} "

        line += res_time + f"{sep} "

        if claim_id:
            line += claim["claim_id"] + f"{sep} "

        if typ:
            line += f"{vtype:9s}" + f"{sep} "
            line += f"{stream_type:9s}" + f"{sep} "
            line += f"{mtype:17s}" + f"{sep} "

        if ch_name:
            line += f"{channel}" + f"{sep} "

        line += f"{rem_min:3d}:{rem_s:02d}" + f"{sep} "
        line += f"{size:9.4f} MB" + f"{sep} "
        line += f'"{name}"'

        out.append(line)

    content = funcs.print_content(out, file=file, fdate=fdate)

    return content
