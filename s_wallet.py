#!/usr/bin/env python3
# --------------------------------------------------------------------------- #
# The MIT License (MIT)                                                       #
#                                                                             #
# Copyright (c) 2022 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de>       #
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
"""Functions to help with logging into Odysee and synchronizing the wallet.

The online copy of the wallet is downloaded, and then synchronized
with the local LBRY installation's wallet.

This code was adapted from FastLBRY
https://notabug.org/jyamihud/FastLBRY-terminal/issues/17
https://notabug.org/jyamihud/FastLBRY-GTK/flbry/odysee.py
"""
import time

import requests

import lbrytools.funcs as funcs


def get_auth_token(api_server="https://api.odysee.com"):
    """Create a new temporary user on Odysee and return its `auth_token`.

    Parameters
    ----------
    api_server: str, optional
        It defaults to `'https://api.odysee.com'`.
        This is the address of the Odysee API server which allows us
        to access some information from Odysee.

    Returns
    -------
    str
        The `auth_token` is a 32-character alphanumeric string
        that can be used together with an Odysee account to access
        certain information from Odysee.
    False
        If there is a problem it will return `False`.
    """
    new_server = api_server + "/user/new"

    auth_token = False

    response = requests.post(new_server).json()

    if response["success"]:
        auth_token = response["data"]["auth_token"]
        out = ["ID: " + str(response["data"]["id"]),
               "Created: " + response["data"]["created_at"],
               "auth_token: " + auth_token]
    else:
        out = ["Error: " + response["error"]]

    funcs.print_content(out, file=None, fdate=False)

    return auth_token


def validate_token(email, password, auth_token,
                   api_server="https://api.odysee.com"):
    """Validate the `auth_token` by the Odysee account.

    Parameters
    ----------
    email: str
        Email for the account on Odysee.
    password: str
        Password for the email account on Odysee.
    auth_token: str
        Alphanumeric string 32-characters, created by `get_auth_token`
        that will be authenticated.
    api_server: str, optional
        It defaults to `'https://api.odysee.com'`.
        This is the address of the Odysee API server which allows us
        to access some information from Odysee.

    Returns
    -------
    dict
        Dictionary with the validated login information, if the correct
        `email`, `password`, and `auth_token` were used.
        At least 25 keys: `'id'`, `'language'`, `'given_name'`,
        `'family_name'`, `'created_at'`, `'updated_at'`, `'invited_by_id'`,
        `'invited_at'`, `'is_email_enabled'`, `'publish_id'`,
        `'is_odysee_user'`, `'location'`, `'youtube_channels'`,
        `'primary_email'`, `'password_set'`, `'latest_claimed_email'`,
        `'has_verified_email'`, `'is_identity_verified'`,
        `'is_reward_approved'`, `'groups'`, `'device_types'`,
        `'odysee_live_enabled'`, `'odysee_live_disabled'`, `'global_mod'`,
        `'experimental_ui'`, `'internal_feature'`, `'odysee_member'`,
        `'pending_deletion'`.
    False
        If there is a problem it will return `False`.
    """
    sign_server = api_server + "/user/signin"

    val_data = False

    data = {"auth_token": auth_token,
            "email": email,
            "password": password}

    response = requests.post(sign_server, data=data).json()

    out = ["Account validation"]

    if response["success"]:
        val_data = d = response["data"]

        out += ["ID: " + str(d.get("id", 0)),
                "Language: " + str(d.get("language", None)),
                "Given name: " + str(d.get("given_name", None)),
                "Family name: " + str(d.get("family_name", None)),
                "Created: " + d.get("created_at", "00"),
                "Updated: " + d.get("updated_at", "00"),
                "Invited by: " + str(d.get("invited_by_id", 0)),
                "Invited: " + d.get("invited_at", "00"),
                "Email enabled: " + str(d.get('is_email_enabled', False)),
                "Publish ID: " + str(d.get("publish_id", 0)),
                "Odysee user: " + str(d.get("is_odysee_user", False)),
                "Location: " + str(d.get("location", None)),
                "YT channels: " + str(d.get("youtube_channels", [])),
                "Email: " + d.get("primary_email", "(None)"),
                "Password set: " + str(d.get("password_set", False)),
                "Latest email: " + str(d.get("latest_claimed_email", None)),
                "Verified email: " + str(d.get("has_verified_email", False)),
                "Verified identity: " + str(d.get("is_identity_verified", False)),
                "Rewards approved: " + str(d.get("is_reward_approved", False)),
                "Groups: " + str(d.get("groups", [])),
                "Devices: " + str(d.get("device_types", [])),
                "Odysee Live enabled: " + str(d.get("odysee_live_enabled", False)),
                "Odysee Live disabled: " + str(d.get("odysee_live_disabled", False)),
                "Global mod: " + str(d.get("global_mod", False)),
                "Experimental UI: " + str(d.get("experimental_ui", False)),
                "Internal feature: " + str(d.get("internal_feature", False)),
                "Odysee member: " + str(d.get("odysee_member", False)),
                "Pending deletion: " + str(d.get("pending_deletion", False))]
    else:
        out += [">>> Error: " + response["error"],
                ">>> Check that the 'auth_token' (32-character), "
                "email and password are valid"]

    funcs.print_content(out, file=None, fdate=False)

    return val_data


def get_sync_hash(wallet_id="default_wallet",
                  server="http://localhost:5279"):
    """Get the sha256 hash of the local wallet.

    Parameters
    ----------
    wallet_id: str, optional
        It defaults to `'default_wallet'`.
        It is the wallet that will be hashed, and can be synchronized.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    str
        The `sync_hash` is the sha256 deterministic hash (64-characters)
        of the wallet.
        This can be used together with the validated `auth_token`
        to get the online wallet data.
    False
        If there is a problem it will return `False`.
    """
    sync_hash = False

    msg = {"method": "sync_hash",
           "params": {"wallet_id": wallet_id}}

    response = requests.post(server, json=msg).json()

    out = [f"Local wallet ID: '{wallet_id}'"]

    if response["result"]:
        sync_hash = response["result"]

        out += [f"Wallet sync hash: {sync_hash}"]
    else:
        out += [">>> Error: " + response.get("error", "(No information)")]

    funcs.print_content(out, file=None, fdate=False)

    return sync_hash


def get_sync_data(auth_token, sync_hash,
                  lbry_api="https://api.lbry.com"):
    """Retrieve the online wallet synchronization data.

    Parameters
    ----------
    auth_token: str
        A 32-character alphanumeric string, created by `get_auth_token`,
        and then validated by `validate_token`.
        If `validate_token` was not called or it failed the validation,
        this function will fail as well.
    sync_hash: str
        The sha256 deterministic hash (64-characters) of the local wallet.
    lbry_api: str, optional
        It defaults to `'https://api.lbry.com'`.
        This is the address of the LBRY API server which allows us
        to access the online wallet.
        It can also be `'https://api.odysee.com'`.

    Returns
    -------
    dict
        Dictionary with the information from the online wallet; four keys:
        - 'changed': `True` or `False`, whether the wallet changed.
        - 'hash': a sha256 hash (64-character).
        - 'data': long string that encodes the synchronization data
          that can be used as input to `lbrynet sync apply`.
        - 'last_updated': integer denoting the Unix time when the wallet
          was last updated.
    False
        If there is a problem it will return `False`.
    """
    sync_get_server = lbry_api + "/sync/get"

    sync_data = False

    data = {"auth_token": auth_token,
            "hash": sync_hash}

    response = requests.post(sync_get_server, data=data).json()

    out = ["Online wallet sync data"]

    if response["success"]:
        sync_data = d = response["data"]
        last = time.gmtime(d.get("last_updated", 0))
        last = time.strftime(funcs.TFMT, last)

        out += ["Changed: " + str(d.get("changed", False)),
                "Hash: " + d.get("hash", "0"),
                "Data: " + str(len(d.get("data", "0"))) + " characters",
                "Last updated: " + last]
    else:
        out += [">>> Error: " + response["error"],
                ">>> Check that the 'auth_token' (32-character) "
                "is properly validated, and the 'sync_hash' is correct."]

    funcs.print_content(out, file=None, fdate=False)

    return sync_data


def get_wallet_data(email, password,
                    wallet_id="default_wallet",
                    api_server="https://api.odysee.com",
                    lbry_api="https://api.lbry.com",
                    server="http://localhost:5279"):
    """Authenticate your account and retrieve the online wallet sync data."""
    auth_token = get_auth_token(api_server=api_server)

    if not auth_token:
        return False

    print(40 * "-")

    val_data = validate_token(email, password, auth_token,
                              api_server=api_server)

    if not val_data:
        return False

    print(40 * "-")

    sync_hash = get_sync_hash(wallet_id=wallet_id,
                              server=server)

    if not sync_hash:
        return False

    print(40 * "-")

    sync_data = get_sync_data(auth_token, sync_hash,
                              lbry_api=lbry_api)

    if not sync_data:
        return False

    return {"auth_token": auth_token,
            "validated": val_data,
            "wallet_id": wallet_id,
            "sync_hash": sync_hash,
            "sync_data": sync_data}


def s_wallet(sync_data,
             wallet_id="default_wallet",
             server="http://localhost:5279"):
    """Synchronize the local wallet with the online wallet sync data.

    The local wallet must be unlocked to perform this operation.

    If 'encrypt-on-disk' preference is `True` and the supplied password
    is different from local password, or there is no local password
    (because local wallet was not encrypted), then the supplied password
    will be used for local encryption (overwriting previous local encryption
    password).

    In this case it assumes no password encryption, as the password is empty.

    Parameters
    ----------
    sync_data: dict
        The online wallet sync data obtained from `get_sync_data`.
        It should have the 'data' key whose value will be used
        as input to `lbrynet sync apply`.
    wallet_id: str, optional
        It defaults to `'default_wallet'`.
        It is the local wallet that will be synchronized with the online data.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        Dictionary with the output of the synchronization operation; two keys:
        - 'hash': a sha256 hash (64-character).
        - 'data': long string that encodes the output wallet data
          after using `lbrynet sync apply`.
    False
        If there is a problem it will return `False`.
    """
    sync_result = False

    in_data = sync_data["data"]

    password = ""

    msg = {"jsonrpc": "2.0",
           "method": "sync_apply",
           "params": {"password": password,
                      "wallet_id": wallet_id,
                      "blocking": True,
                      "data": in_data}}

    response = requests.post(server, json=msg).json()

    out = ["Synchronization result",
           f"Local wallet ID: '{wallet_id}'"]

    if response["result"]:
        sync_result = d = response["result"]

        out += ["Hash: " + d.get("hash", "0"),
                "Data: " + str(len(d.get("data", "0"))) + " characters"]
    else:
        out += [">>> Error: " + response.get("error", "(No information)")]

    funcs.print_content(out, file=None, fdate=False)

    return sync_result


def sync_wallet(email, password,
                wallet_id="default_wallet", sync=False,
                api_server="https://api.odysee.com",
                lbry_api="https://api.lbry.com",
                server="http://localhost:5279"):
    """Download the online wallet, and synchronize it locally.

    Parameters
    ----------
    email: str
        Email for the account on Odysee.
    password: str
        Password for the email account on Odysee.
    wallet_id: str, optional
        It defaults to `'default_wallet'`.
        It is the local wallet that will be synchronized with the online data.
    sync: bool, optional
        It defaults to `False`, in which case it will only download
        the sync data, but it won't perform the local wallet synchronization.
        If it is `True` it will actually run `lbrynet sync apply`.
    api_server: str, optional
        It defaults to `'https://api.odysee.com'`.
        This is the address of the Odysee API server which allows us
        to access some information from Odysee.
    lbry_api: str, optional
        It defaults to `'https://api.lbry.com'`.
        This is the address of the LBRY API server which allows us
        to access the online wallet.
        It can also be `'https://api.odysee.com'`.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.

    Returns
    -------
    dict
        Dictionary with the wallet synchronization input and output:
        - 'auth_token': a 32-character alphanumeric string
          that can be used together with an Odysee account to access
          certain information from Odysee.
        - 'validated': dictionary with the validated login information,
          if the correct `email`, `password`, and `auth_token` were used.
        - 'wallet_id': it is the local wallet that will be synchronized
          with the online data.
        - 'sync_hash': the sha256 deterministic hash (64-characters)
          of the local `wallet_id`. It can be used together with
          the validated `auth_token` to get the online sync data.
        - 'sync_data': dictionary with the information from the online
          wallet, with four keys, including a sha256 `'hash'`,
          and the input sync `'data'`.
        - 'sync_result': dictionary with the output of the synchronization
          operation, with two keys, a sha256 `'hash'`,
          and the output sync `'data'`.
          If `sync=False`, this last key will have a value of `None`,
          since no synchronization was performed.
    False
        If there is a problem it will return `False`.
    """
    wallet_data = get_wallet_data(email, password,
                                  wallet_id=wallet_id,
                                  api_server=api_server,
                                  lbry_api=lbry_api,
                                  server=server)

    if not wallet_data:
        return False

    w_sync_result = {**wallet_data,
                     "sync_result": None}

    print(40 * "-")

    if sync:
        sync_result = s_wallet(wallet_data["sync_data"],
                               wallet_id=wallet_id,
                               server=server)

        if not sync_result:
            return False

        print()
        print("Synchronization complete")
        w_sync_result["sync_result"] = sync_result
    else:
        print()
        print("Synchronization not performed")

    return w_sync_result
