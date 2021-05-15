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
claims. Initially tuxfoo's code was extended lightly but eventually an entire
library was written from scratch to provide more functionality.

# Installation

Copy the internal [lbrytools](./lbrytools) directory, and place it inside
a `site-packages` directory that is searched by Python.
This can be in the user's home directory, or in a system-wide directory.
```
/home/user/.local/lib/python3.8/site-packages/lbrytools

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

It uses a configuration file [zeedit_config.py](./zeedit/zeedit_config.py)
to set up a few options such as the channels to download content from,
when it should perform cleanup of older files, and whether to write
a summary file of all claims.

If `lbrytools` is correctly installed in the Python path, and the configuration
file is in the same directory as `zeedit.py`, it can be run:
```
python zeedit.py
```

To keep everything contained, the `lbrytools` package can be placed in the same
directory as `zeedit.py`.
```
zeedit/
      zeedit.py
      zeedit_config.py
      lbrytools/
               __init___.py
               blobs.py
               ...
```

