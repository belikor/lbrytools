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
"""Functions to manipulate the claims found in the network.

These methods are used with lists of claims returned by `claim_search`.
"""


def sort_and_filter(claims, number=0, reverse=False):
    """Sort the input list and remove duplicated items with same claim ID.

    Parameters
    ----------
    claims: list of dict
        List of claims obtained from `claim_search`.
    number: int, optional
        It defaults to 0, in which case the returned list will contain
        all unique claims.
        If this is any other number, it will cut the output list to have
        a maximum of `number` claims.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the output list.
        If it is `True` the newest items will come first in the output list.

    Returns
    -------
    list of dict
        List of claims obtained from `claim_search`, with the duplicates
        removed.
    """
    print("Sort claims and remove duplicates")
    new_items = []
    n_claims = len(claims)

    # Make sure the `release_time` exists, and use `timestamp` otherwise
    for num, claim in enumerate(claims, start=1):
        if "release_time" not in claim["value"]:
            name = claim["name"]
            print(f'{num:4d}/{n_claims:4d}; "{name}" using "timestamp"')
            claim["value"]["release_time"] = claim["timestamp"]
        new_items.append(claim)

    # Sort by using the original `release_time`.
    # New items will come first.
    sorted_items = sorted(new_items,
                          key=lambda v: int(v["value"]["release_time"]),
                          reverse=True)

    unique_ids = []
    unique_claims = []

    for item in sorted_items:
        if item["claim_id"] not in unique_ids:
            unique_claims.append(item)
            unique_ids.append(item["claim_id"])

    if number:
        # Cut the older items
        unique_claims = unique_claims[0:number]

    if not reverse:
        # Invert the list so that older items appear first
        unique_claims.reverse()

    return unique_claims


def downloadable_size(claims):
    """Calculate the size of the downloadable claims.

    Parameters
    ----------
    claims: list of dict
        List of claims obtained from `claim_search`.

    Returns
    -------
    int
        Total size of the claims in bytes.
        It can be divided by 1024 to obtain kibibytes, by another 1024
        to obtain mebibytes, and by another 1024 to obtain gibibytes.
    """
    print("Calculate size of downloadable claims")
    n_claims = len(claims)
    total_size = 0

    for num, claim in enumerate(claims, start=1):
        vtype = claim["value_type"]

        if "source" in claim["value"]:
            file_name = claim["value"]["source"].get("name", "None")
            size = int(claim["value"]["source"].get("size", 0))
        else:
            file_name = claim["name"]
            size = 0
            print(f"{num:4d}/{n_claims:4d}; type: {vtype}; "
                  f'no source: "{file_name}"')
        total_size += size

    return total_size


def sort_filter_size(claims, number=0, reverse=False):
    """Sort, filter the claims, and provide their entire download size.

    Parameters
    ----------
    claims: list of dict
        List of claims obtained from `claim_search`.
    number: int, optional
        It defaults to 0, in which case the returned list will contain
        all unique claims.
        If this is any other number, it will cut the output list to have
        a maximum of `number` claims.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        on the output list.
        If it is `True` the newest items will come first in the output list.

    Returns
    -------
    list of dict
        List of claims obtained from `claim_search`, with the duplicates
        removed.
    """
    claims = sort_and_filter(claims, number=number, reverse=reverse)

    print()
    total_size = downloadable_size(claims)

    n_claims = len(claims)
    GB = total_size / (1024**3)  # to GiB

    print(40 * "-")
    print(f"Total unique claims: {n_claims}")
    print(f"Total download size: {GB:.4f} GiB")

    return claims, total_size
