#!/usr/bin/env python3
# --------------------------------------------------------------------------- #
# The MIT License (MIT)                                                       #
#                                                                             #
# Copyright (c) 2023 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de>       #
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
"""Functions to help with parsing claims of the LBRY network."""
import os


def parse_claim_file(file=None, sep=";",
                     start=1, end=0):
    """Parse a CSV file containing claim_ids.

    Parameters
    ----------
    file: str
        The path to a comma-separated-values (CSV) file with claim_ids.
        Each row indicates a particular claim, and at least one
        value in a row must be a 40 character `'claim_id'`.

        This file can be produced by `print_summary(file='summary.txt')`
    sep: str, optional
        It defaults to `;`. It is the separator character between
        the data fields in the read file. Since the claim name
        can have commas, a semicolon `;` is used by default.
    start: int, optional
        It defaults to 1.
        Operate on the item starting from this index in `file`.
    end: int, optional
        It defaults to 0.
        Operate until and including this index in `file`.
        If it is 0, it is the same as the last index.

    Returns
    -------
    list of dict
        It returns a list of dictionaries with the claims.
        Each dictionary has a single key, 'claim_id',
        whose value is the 40-character alphanumeric string
        which can be used with `download_single` to get that claim.
    False
        If there is a problem or non existing `file`,
        it will return `False`.
    """
    if not file or not isinstance(file, str) or not os.path.exists(file):
        print("File must exist, and be a valid CSV list of items "
              "with claim ids")
        print(f"file={file}")
        print("Example file:")
        print("  1/435; 70dfefa510ca6eee7023a2a927e34d385b5a18bd;  5/ 5")
        print("  2/435; 0298c56e0593b140c231229a065cc1647d4fedae; 24/24")
        print("  3/435; d30002fec25bff804f144655b3fe4495e00439de; 15/15")
        return False

    with open(file, "r") as fd:
        lines = fd.readlines()

    n_lines = len(lines)
    claims = []

    if n_lines < 1:
        print(">>> Empty file.")
        return False

    print(80 * "-")
    print(f"Parsing file with claims, '{file}'")

    for it, line in enumerate(lines, start=1):
        # Skip lines with only whitespace, and starting with # (comments)
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if it < start:
            continue
        if end != 0 and it > end:
            break

        out = "{:4d}/{:4d}".format(it, n_lines) + f"{sep} "

        # Split by using the separator, and remove whitespaces
        parts = line.split(sep)
        clean_parts = [i.strip() for i in parts]

        found = True
        for part in clean_parts:
            # Find the 40 character long alphanumeric string
            # without confusing it with an URI like 'lbry://@some/video#4'
            if (len(part) == 40
                    and "/" not in part
                    and "@" not in part
                    and "#" not in part
                    and ":" not in part):
                found = True
                claims.append({"claim_id": part})
                break
            found = False

        if found:
            print(out + f"claim_id: {part}")
        else:
            print(out + "no 'claim_id' found, "
                  "it must be a 40-character alphanumeric string "
                  "without special symbols like '/', '@', '#', ':'")

    n_claims = len(claims)
    print(f"Effective claims found: {n_claims}")

    return claims
