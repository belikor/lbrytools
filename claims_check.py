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
"""Functions to display basic information on claims."""
import lbrytools.search as srch
import lbrytools.print as prnt


def check(uri=None, cid=None, name=None,
          repost=True, offline=False,
          print_text=True, print_error=True,
          server="http://localhost:5279"):
    """Check for the existence of a claim, and print information about it.

    If all inputs are provided, `uri` is used.
    If only `cid` and `name` are given, `cid` is used.

    Parameters
    ----------
    uri: str
        A unified resource identifier (URI) to a claim on the LBRY network.
        It can be full or partial.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            uri = '@MyChannel#3/some-video-name#2'
            uri = 'some-video-name'

        The URI is also called the `'canonical_url'` of the claim.
    cid: str, optional
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            name = 'some-video-name'
    repost: bool, optional
        It defaults to `True`, in which case it will check if the claim
        is a repost, and if it is, it will return the original claim.
        If it is `False`, it won't check for a repost, it will simply return
        the found claim.
    offline: bool, optional
        It defaults to `False`, in which case it will use
        `lbrynet claim search` to search `cid` or `name` in the online
        database.

        If it is `True` it will use `lbrynet file list` to search
        `cid` or `name` in the offline database, that is,
        in the downloaded content.
        This is required for 'invalid' claims, which have been removed from
        the online database but may still exist locally.

        When `offline=True`, `repost=True` has no effect because reposts
        must be resolved online. In this case, if `uri` is provided,
        and `name` is not, `uri` will be used as the value of `name`.
    print_text: bool, optional
        It defaults to `True`, in which case it will print
        the summary of the claim to the terminal.
        If it is `False` it will just return the summary text
        but it won't be printed.
    print_error: bool, optional
        It defaults to `True`, in which case it will print the error message
        that `lbrynet resolve` or `lbrynet claim search` returns.
        If it is `False` no error messages will be printed;
        this is useful inside other functions when we want to limit
        the terminal output.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with two keys:
        - 'claim': the dictionary that represents the `claim` that was found
          matching `uri`, `cid` or `name`. It can be `False`
          if nothing was found.
        - 'summary': a paragraph of text with information from the claim
          that can be directly printed to the terminal or to another interface.
          It will be an empty string if no claim was found.
    """
    claim = srch.search_item(uri=uri, cid=cid, name=name,
                             offline=offline, repost=repost,
                             print_error=print_error,
                             server=server)

    summary = ""

    if claim:
        summary = prnt.print_info_pre_get(claim=claim, offline=offline,
                                          print_text=print_text)

    return {"claim": claim,
            "summary": summary}


if __name__ == "__main__":
    check(uri="@lbry")
    print()
    check(cid="37c6878fbd35b153c4f7807dfb74d45abf3dbee3")
    print()
    check(name="1M")
    check("grin-hunter-defi", repost=True)
    print()
    check("grin-hunter-defi", repost=False)
    print()
    # The claim must be downloaded for `offline=True` to work
    check(name="hubba-hubba", offline=False)
    print()
    check(name="hubba-hubba", offline=True)
