# lbrytools

A library of functions that can be used to manage the download of claims from
the LBRY network. It includes methods to download claims by
URI (canonical url), claim ID, or from specific channels.

It also includes methods to clean up older files and free space, so
the functions are suitable for use in a headless computer that will download
files, and seed them to the network with little user intervention.

This libary is released as free software under the MIT license.

# Motivation

The LBRY Desktop application provides basic functionality to manage downloaded
claims. Real control of the system is achieved with the `lbrynet` headless
client.

This library provides convenience functions that wrap around `lbrynet` in order
to search, download, and delete many claims easier.

This library is inspired by tuxfoo's [lbry-seedit](https://github.com/tuxfoo/lbry-seedit) script,
which provides basic functions, and a configuration file to download and seed
claims. Initially tuxfoo's code was extended slightly but eventually an entire
library was written from scratch to provide more functionality.

# Installation

Copy the internal [lbrytools](./lbrytools) directory, and place it inside
a `site-packages` directory that is searched by Python.
This can be in the user's home directory,
```
/home/user/.local/lib/python3.8/site-packages/lbrytools
```

or in a system-wide directory.
```
/usr/local/lib/python3.8/dist-packages/lbrytools
/usr/lib/python3/dist-packages/lbrytools
```

This library was developed and tested with Python 3.8 but it may also work with
earlier versions with small changes.

# Usage

Make sure the `lbrynet` daemon is running either by launching
the full LBRY Desktop application, or by starting the console `lbrynet`
program.
```
lbrynet start
```

Then open a Python console, import the module, and use its methods.
```py
import lbrytools as lbryt

lbryt.download_single(...)
lbryt.ch_download_latest(...)
lbryt.ch_download_latest_multi(...)
lbryt.redownload_latest(...)
lbryt.redownload_claims(...)
lbryt.print_summary()
lbryt.delete_single(...)
lbryt.measure_usage(...)
lbryt.cleanup_space(...)
lbryt.remove_media()
```

Read the [lbrytools.md](./lbrytools/lbrytools.md) file for a short explanation
on the most useful functions in the library.

# Zeedit script

This script uses the `lbrytools` methods to achieve the same objective as
tuxfoo's original [lbry-seedit](https://github.com/tuxfoo/lbry-seedit).
It downloads content from various channels, and then seeds the blobs to
the network. 
This script should be run periodically to constantly download new content,
and remove the older files if they take too much space.
See [zeedit.py](./zeedit/zeedit.py).

It uses a configuration file to set up a few options such as the channels
to download content from, the download directory, at which point
it should perform cleanup of older files, and whether to write a summary
of all downloaded claims.
Read the comments in [zeedit_config.py](./zeedit/zeedit_config.py)
to know about the options that can be configured.

If `lbrytools` is correctly installed in the Python path, the script can be
executed directly, or through the Python interpreter.
```
python zeedit.py [config.py]
```

The configuration file can be passed as the first argument, so it is possible
to have different configurations to download content of different channels.
```
python zeedit.py funny_config.py
python zeedit.py tech_channels_config.py
```

If no argument is given, or the provided configuration file does not exist,
it will try to load a configuration under the name `zeedit_config.py`.

To keep everything contained, the `lbrytools` package can be placed in the same
directory as `zeedit.py` and `zeedit_config.py`.
```
zeedit/
      zeedit.py
      zeedit_config.py
      lbrytools/
               __init___.py
               blobs.py
               ...
```

# Development

Ideally, this collection of tools can be merged into the official
LBRY sources so that everybody has access to them.
Where possible, the tools should also be available from a graphical
interface such as the LBRY Desktop application.
* [lbryio/lbry-sdk](https://github.com/lbryio/lbry-sdk)
* [lbryio/lbry-desktop](https://github.com/lbryio/lbry-desktop)

If you wish to support this work you can send a donation:
```
LBC: bY38MHNfE59ncq3Ch3zLW5g41ckGoHMzDq
XMR: 8565RALsab2cWsSyLg4v1dbLkd3quc7sciqFJ2mpfip6PeVyBt4ZUbZesAAVpKG1M31Qi5k9mpDSGSDpb3fK5hKYSUs8Zff
```
