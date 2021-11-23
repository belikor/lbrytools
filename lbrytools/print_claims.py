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
