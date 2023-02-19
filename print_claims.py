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


def get_fields(claim,
               long_chan=False,
               title=False, sanitize=False):
    """Common code to get information to print."""
    meta = claim["meta"]
    value = claim["value"]

    create_height = meta.get("creation_height", 0)
    create_height = f"{create_height:8d}"

    create_time = meta.get("creation_timestamp", 0)
    create_time = time.strftime(funcs.TFMTp, time.gmtime(create_time))

    block_height = claim["height"]
    block_height = f"{block_height:8d}"

    timestamp = claim["timestamp"]
    timestamp = time.strftime(funcs.TFMTp, time.gmtime(timestamp))

    rels_time = int(value.get("release_time", 0))

    if not rels_time:
        rels_time = create_time[:]
    else:
        rels_time = time.strftime(funcs.TFMTp, time.gmtime(rels_time))

    vtype = claim["value_type"]
    vtype = f"{vtype:10s}"

    stream_type = value.get("stream_type", 8 * "_")
    stream_type = f"{stream_type:9s}"

    mtype = 14 * "_"

    if "source" in value:
        mtype = value["source"].get("media_type", 14 * "_")

    mtype = f"{mtype:17s}"

    channel = 14 * "_"

    if "signing_channel" in claim:
        if "canonical_url" in claim["signing_channel"]:
            channel = claim["signing_channel"]["canonical_url"]
            channel = channel.split("lbry://")[1]
        elif "permanent_url" in claim["signing_channel"]:
            channel = claim["signing_channel"]["permanent_url"]
            _ch, _id = channel.split("#")
            _ch = _ch.split("lbry://")[1]
            channel = _ch + "#" + _id[0:3]
        else:
            channel = 14 * "_"

    if long_chan:
        channel = f"{channel:40s}"
    else:
        channel = f"{channel}"

    seconds = 0

    if "video" in value and "duration" in value["video"]:
        seconds = value["video"]["duration"]
    if "audio" in value and "duration" in value["audio"]:
        seconds = value["audio"]["duration"]

    mi = seconds // 60
    sec = seconds % 60
    duration = f"{mi:3d}:{sec:02d}"

    size = 0

    if "source" in value and "size" in value["source"]:
        size = float(value["source"]["size"])

    size_mb = size / (1024**2)  # to MB
    size_mb = f"{size_mb:9.4f} MB"

    support = meta.get("effective_amount", "")
    support = f"{support:>13s}"

    fee = " "

    if "fee" in value:
        fee = value["fee"].get("amount", "___")
        fee = f"{fee} " + value["fee"]["currency"]

    fee = f"f: {fee:>9s}"

    name = claim["name"]

    if title:
        name = value.get("title") or name

    if sanitize:
        name = funcs.sanitize_text(name)
        channel = funcs.sanitize_text(channel)

    name = f'"{name}"'

    return {"meta": meta,
            "value": value,
            "create_height": create_height,
            "create_time": create_time,
            "block_height": block_height,
            "timestamp": timestamp,
            "release_time": rels_time,
            "value_type": vtype,
            "stream_type": stream_type,
            "media_type": mtype,
            "channel": channel,
            "duration": duration,
            "size_mb": size_mb,
            "support": support,
            "fee": fee,
            "name": name}


def get_line(claim,
             create=False, height=False, release=True,
             claim_id=False, typ=True, ch_name=True,
             long_chan=True,
             sizes=True, supports=True, fees=True,
             title=False, sanitize=False,
             sep=";"):
    """Get a line to print information for a single claim."""
    fields = get_fields(claim, long_chan=long_chan,
                        title=title, sanitize=sanitize)

    create_height = fields["create_height"]
    create_time = fields["create_time"]
    block_height = fields["block_height"]
    timestamp = fields["timestamp"]
    rels_time = fields["release_time"]

    vtype = fields["value_type"]
    stream_type = fields["stream_type"]
    mtype = fields["media_type"]

    channel = fields["channel"]

    duration = fields["duration"]
    size_mb = fields["size_mb"]
    support = fields["support"]
    fee = fields["fee"]

    name = fields["name"]

    line = ""

    if create:
        line += f"{create_height}" + f"{sep} "
        line += f"{create_time}" + f"{sep} "

    if height:
        line += f"{block_height}" + f"{sep} "
        line += f"{timestamp}" + f"{sep} "

    if release:
        line += f"{rels_time}" + f"{sep} "

    if claim_id:
        line += claim["claim_id"] + f"{sep} "

    if typ:
        line += f"{vtype}" + f"{sep} "
        line += f"{stream_type}" + f"{sep} "
        line += f"{mtype}" + f"{sep} "

    if ch_name:
        line += f"{channel}" + f"{sep} "

    if sizes:
        line += f"{duration}" + f"{sep} "
        line += f"{size_mb}" + f"{sep} "

    if supports:
        line += f"{support}" + f"{sep} "

    if fees:
        line += f"{fee}" + f"{sep} "

    line += f"{name}"

    return line


def print_sch_claims(claims,
                     create=False, height=False, release=True,
                     claim_id=False, typ=True, ch_name=False,
                     long_chan=False,
                     sizes=True, supports=True, fees=True,
                     title=False, sanitize=False,
                     start=1, end=0,
                     reverse=False,
                     file=None, fdate=False, sep=";"):
    """Print the provided list of claims searched online."""
    n_claims = len(claims)

    if reverse:
        claims.reverse()

    out = []

    for num, claim in enumerate(claims, start=1):
        if num < start:
            continue
        if end != 0 and num > end:
            break

        line_add = get_line(claim, long_chan=long_chan,
                            create=create, height=height, release=release,
                            claim_id=claim_id, typ=typ, ch_name=ch_name,
                            sizes=sizes, supports=supports, fees=fees,
                            title=title, sanitize=sanitize,
                            sep=sep)

        line = f"{num:4d}/{n_claims:4d}" + f"{sep} "
        line += line_add

        out.append(line)

    funcs.print_content(out, file=file, fdate=fdate)
