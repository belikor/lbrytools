# Initialization

The LBRY daemon must be running before using the majority of these tools.
This can be done by launching the full LBRY Desktop application,
or by starting the console `lbrynet` program.
```
lbrynet start
```

Then in a Python terminal, or in a Python script, import `lbrtytools`
or the individual methods.
```py
import lbrytools as lbryt
```

Or
```py
from lbrytools import download_single
from lbrytools import ch_download_latest
from lbrytools import ch_download_latest_multi
from lbrytools import redownload_latest
from lbrytools import download_claims
from lbrytools import print_summary
from lbrytools import print_channels
from lbrytools import delete_single
from lbrytools import ch_cleanup
from lbrytools import ch_cleanup_multi
from lbrytools import remove_claims
from lbrytools import measure_usage
from lbrytools import cleanup_space
from lbrytools import remove_media
from lbrytools import count_blobs
from lbrytools import count_blobs_all
from lbrytools import analyze_blobs
from lbrytools import download_missing_blobs
from lbrytools import analyze_channel
from lbrytools import print_channel_analysis
from lbrytools import blobs_move
from lbrytools import blobs_move_all
from lbrytools import claims_bids
from lbrytools import channel_subs
from lbrytools import list_accounts
from lbrytools import list_playlists
```

# Download

Define the download directory.
```py
ddir = "/opt/download"
```

Download a single item from the LBRY network by URI (`'canonical_url'`),
`'claim_id'`, or `'claim_name'` (portion of the URI).
Place the file in a subdirectory in the download directory.
```py
d = lbryt.download_single(uri="dealing-with-pollution-in-a-free-market#3", ddir=ddir, own_dir=True)
d = lbryt.download_single(cid="37c6878fbd35b153c4f7807dfb74d45abf3dbee3", ddir=ddir, own_dir=True)
d = lbryt.download_single(name="dealing-with-pollution-in-a-free-market", ddir=ddir, own_dir=True)
```

# Download invalid claims

Invalid claims are those that were downloaded at some point but which now
cannot be resolved anymore from the online database (blockchain).
This probably means that the author decided to remove the claims
after they were downloaded originally.
This can be verified with the blockchain explorer, by following the claim ID,
and looking for the `unspent` transaction.

Invalid claims cannot actually be downloaded or redownloaded anymore
as the information about them is no longer online. However,
if their binary blobs are still in our system, then the media files
(mp4, mp3, mkv, etc.) can still be recreated from these offline blobs,
and placed in the download directory.
```py
d = lbryt.download_single(cid="2a6c48346ca2064a9c53dd129ad942fa01bb125a", ddir=ddir, invalid=True)
d = lbryt.download_single(name="firenvim-embed-neovim-into-every-textbox", ddir=ddir, invalid=True)
```

The `invalid=True` parameter only has an effect if `cid` or `name`
are used as inputs. If `uri` is used, it will always try to resolve the claim
by looking at the online database.

Since invalid claims cannot be redownloaded, once we have recreated
the media files, these can be saved to a secure location,
and then we could decide to completely delete the corresponding blobs
in order to free space on the disk.

# Multiple downloads

Download the latest claims from a single channel.
The channel may be specified fully, with the prefix `@` and characters after
`#` or `:`, or partially, without them.
Full names are necessary to distinguish two channels with the same base name.
```py
c = lbryt.ch_download_latest(channel="@lbry", number=3, ddir=ddir)
```

Various claims from many channels can be downloaded at the same time.
Define a list where each element is a list of two elements; the first item
is the name of the channel, and the second is a number indicating how
many items will be downloaded from that channel.
If the number is missing it will use the default value (2).
```py
channels = [
    ["@BrodieRobertson#5", 2],
#    ["@rossmanngroup:a", 4],
    ["@Odysee#8", 2],
#    ["@MoneroTalk:8", 1],
    ["@samtime#1", 3],
    ["@Veritasium:f", 2]
]

ch = lbryt.ch_download_latest_multi(channels=channels, ddir=ddir)
```

By using the `number` parameter, the individual numbers in `channels`
are overriden.
For exampe, download the 4 newest claims from each channel.
```py
ch = lbryt.ch_download_latest_multi(channels=channels, ddir=ddir, number=4)
```

Another way of specifying the list of channels is as a simple list of strings.
In this case `number` must be specified explicitly to control the number
of downloads for each channel.
For example, download the latest claim for each channel in the list.
```py
channels = [
    "BrodieRobertson",
    "rossmanngroup",
    "MoneroTalk"
]

c = lbryt.ch_download_latest_multi(channels=channels, ddir=ddir, number=1)
```

If the list of channels is large, it is better to randomize it
so that we can start downloading from an arbitrary channel, and not
always from the first one in the list.
```py
c = lbryt.ch_download_latest_multi(channels=channels, ddir=ddir, shuffle=True)
```

# Downloading collections

A "collection" or playlist is a special type of claim that contains
a list of one or more claim IDs.
We cannot download the collection directly but we can parse the list of IDs,
and download these individually.
```py
c = lbryt.download_single("collection-music", collection=True, ddir=ddir)
```

If `collection=True` but the input URI or claim ID is not a collection
it will be treated like a regular claim.

A collection can have an arbitrary number of items, so to limit
the number of claims to download we can use `max_claims`,
which is 2 by default.

To reverse the order of the claims in the collection
use `reverse_collection=True`. This can be used to get the newest
items in the collection.
```py
c = lbryt.download_single("collection-music", collection=True,
                          max_claims=10, reverse_collection=True,
                          ddir=ddir)
```

# Printing

Print a list of claims that have been downloaded partially or fully
in chronological order, by `'release_time'`.
Older claims appear first.
Certain items don't have `'release time'`, so for these
the `'timestamp'` is used.

Specify a filename to print to that file, otherwise it will print to
the terminal. Optionally add the date to the filename to better keep track
of the written files.
```py
p = lbryt.print_summary()
p = lbryt.print_summary(file="summary.txt")
p = lbryt.print_summary(file="summary.txt", fdate=True)
```

Various options control which claims are actually printed.
Print all files (default),
or only those which have incomplete blobs,
or only those which have all their blobs,
or only those for which the full media file (mp4, mp3, mkv, etc.) exists,
or only those for which the media file is missing.
```py
p = lbryt.print_summary(show="all")
p = lbryt.print_summary(show="incomplete")
p = lbryt.print_summary(show="full")
p = lbryt.print_summary(show="media")
p = lbryt.print_summary(show="missing")
```

Normally only items that have all blobs also have a media file; however,
if the claim is currently being downloaded a partial media file may be present.

Various options control the type of information that is printed,
including title, type, download path, claim id, number of blobs,
name of channel, and name of claim.
We may specify the separator between the data fields; since a claim name
can have a comma as part of the name, a semicolon `;` is used by default.
```py
p = lbryt.print_summary(title=True, typ=False, path=False,
                        cid=True, blobs=True, ch=False,
                        name=True, sep=";")
```

We can also restrict printing only a range of items, or only the claims
by a specific channel (it implies `ch=True`).
```py
p = lbryt.print_summary(start=20)  # From this index until the end
p = lbryt.print_summary(end=40)  # From the beginning until this index
p = lbryt.print_summary(start=100, end=500)  # Delimited range
p = lbryt.print_summary(channel="Veritasium")
```

When printing the channel's name we can choose whether to find
the name by resolving the claim online or not.
```py
p = lbryt.print_summary(ch=True, ch_online=True)
p = lbryt.print_summary(channel="NaomiBrockwell", ch_online=False)
```

In the first case (default) we will obtain a full channel name
without ambiguity (in case two channels have the same base name).
However, this is slow because it has to resolve the item online first.

The second case uses the locally stored database to get the channel name,
and thus it is very fast. However, if that channel name has not been properly
resolved, it may not return an actual name, in which case it will just
print `_Unknown_`.

# Printing invalid claims

Print only the invalid claims by using the `invalid=True` parameter
of `print_summary`. This will be slower than with `invalid=False`
as it needs to resolve each claim online, to see if it's still valid or not.
```py
p = lbryt.print_summary(invalid=True)
p = lbryt.print_summary(file="summary_invalid.txt", invalid=True)
```

If `invalid=True` and `ch=True` or `channel` is used, this will automatically
set `ch_online=False` because for invalid claims the channel name
can only be resolved from the offline database.
```py
p = lbryt.print_summary(invalid=True, ch=True)
p = lbryt.print_summary(invalid=True, channel="mises")
```

# Printing channels

Print a list of all unique channels that published the downloaded claims
that we have.
Specify the separator, or it will use a semicolon by default.
```py
o = lbryt.print_channels()
o = lbryt.print_channels(sep=";")
```

Since LBRY allows channels to have the same "base" name, by default
channels are printed in their "full" form (`@MyChannel#3`, `@MyChannel#c6`)
in order to avoid ambiguity.
Certain claims were published anonymously, so for these the channel
is `@_Unknown_`.
Two parameters control whether to use the full name or the canonical name.
```py
o = lbryt.print_channels(full=False)
o = lbryt.print_channels(canonical=True)
```

By default, channel names are printed in three columns for clarity.
Use the `simple` parameter to print all channels in a single string,
each channel separated from another by a `sep` symbol.
```py
o = lbryt.print_channels(simple=True, sep=",")
```

By default, each claim is resolved online in order to get the channel
information from the online database (blockchain).
This takes significant time, so the function may take several minutes
to return if there are thousands of downloaded claims.
With `offline=True` we can resolve the claims from the offline database;
this is quicker but may not print all existing channels
as some of them might have not been resolved when the claims were originally
downloaded.

If `offline=True` is used, `full` and `canonical` have no effect,
and only the base name is printed.
The reason is that the offline database stores only the base name.
```py
o = lbryt.print_channels(offline=True)
```

If we wish to print only channels from invalid claims
we can use `invalid=True`. This implies `offline=True` as well,
as invalid claims cannot be resolved online.
```py
o = lbryt.print_channels(invalid=True)
```

Print the list of channels to a file.
Optionally add the date to the name of the file.
```py
o = lbryt.print_channels(file="channels.txt", fdate=True)
```

Notice that only channels that can be successfully resolved will be
printed. If a channel cannot be resolved online or offline
for any reason, it will be set to `None`, and it will not be counted
nor printed.
Thus, even if we have claims from a particular channel, if it hasn't
been resolved, it may not appear in the output.

The channel name resolution is affected by a bug in the SDK,
which is documented in
[lbry-sdk issue #3316](https://github.com/lbryio/lbry-sdk/issues/3316).

If you wish to manually resolve a channel you can use the following function.
```py
ch = lbryt.resolve_channel("@MyChannel")
```

# Download from file

Download claims from a comma-separated values (CSV) file that lists
one claim per row, with the `'claim_id'` in one column.
This type of file can be generated by `print_summary`.
```py
p = lbryt.print_summary(file="summary.txt")

q = lbryt.download_claims(ddir=ddir, own_dir=True, file="summary.txt")
```

The list of claims can be limited by a range of indices.
```py
q = lbryt.download_claims(ddir=ddir, start=20, end=80, file="summary.txt")
```

Sharing a list of claims in this way allows different systems to download,
and seed the same content.

The `invalid` argument must be used if the file being processed is a list
of invalid items.
```py
p = lbryt.print_summary(file="summary_invalid.txt", invalid=True)

q = lbryt.download_claims(file="summary_invalid.txt", invalid=True)
```

# Re-download

Re-downloading a claim that was previously downloaded will get the missing
blobs of that claim in order to create the media file. If the blobs are
complete but the media file is missing, this file will simply be recreated
in the download directory.

Attempt to re-download the latest (newest) items that were already downloaded.
This can be done to resume the download of claims that for some reason
were not fully downloaded.
```py
r = lbryt.redownload_latest(number=10, ddir=ddir, own_dir=True)
```

If the list of claims is shuffled, then we can re-download random claims,
not necessarily the latest ones.
```py
r = lbryt.redownload_latest(number=20, ddir=ddir, own_dir=True, shuffle=True)
```

----

With `download_claims` if the `file` argument is omitted, it will try to
redownload all claims previously downloaded.
```py
q = lbryt.download_claims(ddir=ddir)
```

# Delete

Delete a single downloaded item by URI or `'claim_id'`.
Choose to delete the media file (mp4, mp3, mkv, etc.), the blobs, or both.
```py
s = lbryt.delete_single(cid="099ace3145fba6bef6b529bcf03efcc0eb8ebfc9", what="media")
s = lbryt.delete_single(uri="if-samsung-made-a-macbook", what="blobs")
s = lbryt.delete_single(uri="ftc-rulemaking-testimony-from-louis:9", what="both")
```

As long as the blobs are present, the content can be seeded to the network,
and the full file can be restored.
That is, while the blobs exist the file is not completely deleted.

# Delete invalid claims

By default, before a claim is deleted with `delete_single`, every claim
is checked in the online database (blockchain) to get more information
about it.

For invalid claims, those that have been removed by their authors,
they won't be able to be found online anymore. Therefore, the `invalid=True`
parameter must be used in order to resolve the claims in the offline database,
and be able to delete them.
```py
s = lbryt.delete_single(uri="right-to-repair-introduced-federally-for:7", invalid=True)
```

# Delete claims from channel

Delete all downloaded claims from a single channel with the exception
of the newest claims, as determined by their `'release_time'`,
or `'timestamp'` if the former is missing.
Choose to delete the media files, the blobs, or both.
This is useful to only seed the newest videos from a particular channel.
```py
s = lbryt.ch_cleanup(channel="@gothix", number=5, what="both")
s = lbryt.ch_cleanup(channel="@classical", number=10, what="media")
s = lbryt.ch_cleanup(channel="@samtime", number=4, what="blobs")
```

Similar to the `ch_download_latest_multi` method, you can define
the channels in a list, and the number of items to keep for each channel.
```py
channels = [
    ["@AlphaNerd#8", 3],
    ["@gothix:c", 8],
    ["@samtime#1", 2],
    ["@AfterSkool", 5]
]

ch = lbryt.ch_cleanup_multi(channels=channels, what="media")
```

By using the `number` parameter, the individual numbers in `channels`
are overriden.
For exampe, keep only the 3 newest claims from each channel.
```py
ch = lbryt.ch_cleanup_multi(channels=channels, number=3)
```

Another way of specifying the list of channels is as a simple list of strings.
In this case `number` must be specified explicitly to control the number
of claims that will remain for every channel.
```py
channels = [
    "AlisonMorrow",
    "ThePholosopher",
    "ChrissieMayr",
    "Karlyn"
]

c = lbryt.ch_cleanup_multi(channels=channels, number=4)
```

# Delete from file

Delete claims from a comma-separated values (CSV) file that lists
one claim per row, with the `'claim_id'` in one column.
This type of file can be generated by `print_summary`.
```py
p = lbryt.print_summary(file="summary.txt")

q = lbryt.remove_claims(file="summary.txt")
```

The list of claims can be limited by a range of indices, and we can choose
to delete the media file, the blobs, or both.
```py
q = lbryt.remove_claims(start=200, file="summary.txt", what="media")
q = lbryt.remove_claims(end=500, file="summary.txt", what="blobs")
q = lbryt.remove_claims(start=100, end=900, file="summary.txt", what="both")
```

If the `file` argument is omitted, it will delete all claims
previously downloaded.
```py
q = lbryt.remove_claims()  # Deletes media files by default.
q = lbryt.remove_claims(what="both")  # Deletes everything!
```

The `invalid ` argument must be used if the file being processed is a list
of invalid items.
```py
p = lbryt.print_summary(file="summary_invalid.txt", invalid=True)

q = lbryt.remove_claims(file="summary_invalid.txt", invalid=True)
```

# Measure disk usage

Measure the space that is being used by downloaded content and their blobs;
`main_dir` is assumed to be the hard disk or partition that holds both
the downloaded files and the blobs.

In a typical Linux installation both directories are in the same partition
```
ddir  = /home/user/Downloads
blobs = /home/user/.local/share/lbry/lbrynet/blobfiles
```
therefore
```py
main_dir = "/home/user"
```

If the blobfiles directory is symbolically linked to another partition,
and the download directory is also specified in this partition,
then `main_dir` should be specified accordingly.
```
ddir  = /opt/download
blobs = /home/user/.local/share/lbry/lbrynet/blobfiles -> /opt/lbryblobfiles/
```
therefore
```py
main_dir = "/opt"
```

Then `size` is the space in gigabytes (GB) in `main_dir` dedicated
to the media and blobs; `percent` is how much it will fill up before space
needs to be freed.
```py
m = lbryt.measure_usage(main_dir=main_dir, size=1000, percent=90)
m = lbryt.measure_usage(main_dir=main_dir, size=1000, percent=90, bar=False)
```

# Clean up space

Free space by deleting older media files when 90% of `size` is full.
```py
n = lbryt.cleanup_space(main_dir=main_dir, size=1000, percent=90, what="media")
```

We can choose to delete media files, blobs, or both.
While the blobs exist, the media file can be seeded and recreated.
More space is freed by deleting both media and blobs.
```py
n = lbryt.cleanup_space(main_dir=main_dir, what="media")
n = lbryt.cleanup_space(main_dir=main_dir, what="blobs")
n = lbryt.cleanup_space(main_dir=main_dir, what="both")
```

Free space but avoid deleting the content from certain channels.
This is slow as it needs to perform an additional search for the channel.
```py
never_delete = [
    "@lbry",
    "@Odysee",
    "@samtime",
    "@RobBraxmanTech"
]

n = lbryt.cleanup_space(main_dir=main_dir, size=2000, never_delete=never_delete)
```

----

Remove all downloaded media files (mp4, mp3, mkv, etc.) and leave only
the binary blobs.
This is useful for systems that will only seed the downloaded content,
as only the blobs are necessary in this case.
```py
k = lbryt.remove_media()
```

The `never_delete` list can be used, although for headless systems that will
only seed it should be avoided.
```py
k = lbryt.remove_media(never_delete=never_delete)
```

# Blobs

When a claim is downloaded a group of binary blobs is downloaded into
the `blobfiles` directory. All blobs from all claims are dumped
into this directory without much organization.
```py
bdir = /home/user/.local/share/lbry/lbrynet/blobfiles
```

Count the blobs that exist for a particular claim.
Use the canonical URL, the claim ID, or the claim name.
```py
c = lbryt.count_blobs(uri="how-monero-works-and-why-its-a-better", blobfiles=bdir)
c = lbryt.count_blobs(cid="b4f73ad1e09e21457e18e4b3f8da0cc4319f8688", blobfiles=bdir)
```

Print each of the blobs, indicating whether they are present
or not in `blobfiles`.
```py
c = lbryt.count_blobs(uri="The-Essence-of-Money-(2009)", blobfiles=bdir, print_each=True)
```

Count all blobs in the system, or consider only the claims by a specific
channel, or by a range of items.
```py
c = lbryt.count_blobs_all(blobfiles=bdir)
c = lbryt.count_blobs_all(blobfiles=bdir, channel="AfterSkool")
c = lbryt.count_blobs_all(blobfiles=bdir, start=10, end=100)
```

By default only a summary is printed. Two parameters control whether
to display more information on each claim and its blobs.
```py
c = lbryt.count_blobs_all(blobfiles=bdir, print_msg=True)
c = lbryt.count_blobs_all(blobfiles=bdir, print_msg=True, print_each=False)
```

# Analyze blobs

If we manually do something with the blobs in the `blobfiles` directory,
we may want to count all files in this directory to see if they match
the blobs that each claim is supposed to have.
This information is contained in the first blob of each claim,
called the "manifest" blob, whose name corresponds to the claim's `'sd_hash'`.
```py
a = lbryt.analyze_blobs(blobfiles=bdir)
```

This function wraps around the `count_blobs_all` function so it has the same
input parameters.
```py
a = lbryt.analyze_blobs(blobfiles=bdir, channel="Odysee")
a = lbryt.analyze_blobs(blobfiles=bdir, start=5, end=33)
a = lbryt.analyze_blobs(blobfiles=bdir, print_msg=True, print_each=False)
```

# Download missing blobs

We can identify claims with missing blobs, either data blobs
or the initial `'sd_hash'` blob, and automatically redownload the claims.
```py
b = lbryt.download_missing_blobs(blobfiles=bdir, ddir=ddir)
```

If we already have many claims in our system this may take a while,
so we may decide to restrict this to only a single channel,
or a range of items.
```py
b = lbryt.download_missing_blobs(blobfiles=bdir, ddir=ddir, channel="@EatMoreVegans")
b = lbryt.download_missing_blobs(blobfiles=bdir, ddir=ddir, start=20, end=50)
```

# Analyze channel

We can display a summary of a particular channel by counting all blobs
from all its downloaded claims, both complete and incomplete,
and measure the space that they take in gigabytes (GB).
```py
c = lbryt.analyze_channel(blobfiles=bdir, channel="@EatMoreVegans")
```

If the channel is not specified, it will analyze all blobs from all valid
claims in the system, and thus provide an overall summary of all downloads.
Beware that this takes considerable time (more than one hour)
if there is a large number of downloaded claims and blobs, for example,
1000 claims with 100 thousand blobs.
```py
c = lbryt.analyze_channel(blobfiles=bdir)
```

# Print channels analysis

Print a summary for all channels in tabular form.
It will print the number of claims, the number of blobs, and the disk space
in gigabytes (GB) that those blobs use.

This method uses `analyze_channel` internally with each channel,
so it takes a considerable amount of time to run (more than one hour)
if there is a large number of downloaded claims and blobs, for example,
1000 claims with 100 thousand blobs.
```py
d = lbryt.print_channel_analysis(blobfiles=bdir)
```

Print the information split in complete claims, and incomplete claims
in parentheses.
```py
d = lbryt.print_channel_analysis(blobfiles=bdir, split=True)
```

Print a bar for each channel representing their disk usage.
In this case, it will show the numerical values combined as if `split=False`.
```py
d = lbryt.print_channel_analysis(blobfiles=bdir, bar=True)
```

We can sort the channels by disk usage.
If `reverse=False` it is ascending order (higher usage last),
and with `reverse=True` it will be in descending order (higher usage first).
```py
d = lbryt.print_channel_analysis(blobfiles=bdir, bar=True, sort=True, reverse=True)
```

Print the list of channels to a file.
Optionally add the date to the name of the file.
```py
d = lbryt.print_channel_analysis(blobfiles=bdir, file="ch_summary.txt", fdate=True)
```

# Move blobs

If you wish to organize the blobs better you may copy or move the blobs
to a different location. This can be done to backup the claim data
in an external hard drive. However, to seed the file, the blobs must be
in the `blobfiles` directory.

Define the path of the directory where the blobs will be placed,
and of the original `blobfiles` directory.
```py
mdir = /home/user/Downloads
bdir = /home/user/.local/share/lbry/lbrynet/blobfiles
```

The `blobfiles` directory is located inside the `'data_dir'`
as indicated by `lbrynet settings get`.

To specify a claim use the canonical URL, the claim ID, or the claim name.
You can specify whether to copy the blobs (default) or move the blobs.
Moving the blobs will free space in `blobfiles`.
```py
f = lbryt.blobs_move(uri="can-you-turn-a-samsung-into-a-blackberry:0", move_dir=mdir, blobfiles=bdir)
f = lbryt.blobs_move(cid="70dfefa510ca6eee7023a2a927e34d385b5a18bd", move_dir=mdir, blobfiles=bdir, action="copy")
f = lbryt.blobs_move(name="new-stimulus-approved-only-with-crypto", move_dir=mdir, blobfiles=bdir, action="move")
```

The function will copy or move the blobs that actually exist in
the `blobfiles` directory. Missing blobs will be skipped; this usually means
that the claim was not downloaded fully; in this case, redownload the claim.

To see which blobs are missing, pass the `print_missing=True` argument.
```py
f = lbryt.blobs_move(name="new-stimulus-approved-only-with-crypto", move_dir=mdir, blobfiles=bdir, print_missing=True)
```

We can copy or move the blobs from all downloaded claims.
```py
g = lbryt.blobs_move_all(move_dir=mdir, blobfiles=bdir, print_missing=True)
g = lbryt.blobs_move_all(move_dir=mdir, blobfiles=bdir, action="copy")
g = lbryt.blobs_move_all(move_dir=mdir, blobfiles=bdir, action="move")
```

The number of claims can be limited by a range of indices, by a channel name,
or by both.
```py
g = lbryt.blobs_move_all(move_dir=mdir, blobfiles=bdir, start=100, end=200)
g = lbryt.blobs_move_all(move_dir=mdir, blobfiles=bdir, channel="@ragreynolds")
g = lbryt.blobs_move_all(move_dir=mdir, blobfiles=bdir, channel="@ragreynolds", start=5, end=10)
```

# Claims

A claim is any object that is recorded in the blockchain,
and that has some LBC supporting its `'name'`.
This is typically channels (the highest bid controls the default `'name'`),
streams (video and audio files, documents), but also reposts, playlists,
and other types.
We may want to see information on our claims, and how many other claims
are competing for the same `'name'`.

In most cases we want to omit the claims that are "controlling",
meaning that we only want to see claims that don't have the highest bid.
This is so that we know which of our claims we should support with more LBC
if we want them to appear higher in search results.
In most cases we should also omit our reposts because we don't need reposts
to have a higher bid than the original claim.
```py
s = lbryt.claims_bids(skip_max=True, skip_repost=True)
```

Since LBRY allows two or more channels to have the same base `'name'`,
we can inspect only our channels to see if they are unique,
or if they are outbid by others.
```py
s = lbryt.claims_bids(skip_max=True, channels_only=True)
```

Due to `lbry-sdk` [issue #3381](https://github.com/lbryio/lbry-sdk/issues/3381),
at the moment only 50 competing claims having the same `'name'` can be compared.

Print the information on the claims to a file.
Optionally add the date to the name of the file.
If `compact=True`, the information from a claim will be printed
in a single line.
```py
s = lbryt.claims_bids(file="claims.txt", fdate=True)
s = lbryt.claims_bids(file="claims.txt", fdate=True, compact=True)
```

# Channel subscriptions

Display the channels to which we are subscribed,
and whether we receive notifications from them.
```py
q = lbryt.channel_subs(notifications=True)
```

By default, the command searches the `"shared"` database,
but it can also search the `"local"` database.
```py
q = lbryt.channel_subs(shared=False)
```

The information can be printed to a file as well.
```py
q = lbryt.channel_subs(file="subs.txt", fdate=True)
```

# Accounts

List the accounts in the current wallet,
along with the balance in each account.
```py
a = lbryt.list_accounts()
```

It can also show the individual addresses that have been
used for each account.
```py
a = lbryt.list_accounts(addresses=True)
```

The information can be printed to a file as well.
```py
a = lbryt.list_accounts(file="accounts.txt", fdate=True)
```

# Playlists

List the playlists saved in the current preferences.
```py
v = lbryt.list_playlists()
```

By default, the command searches the `"shared"` database,
but it can also search the `"local"` database.
```py
v = lbryt.list_playlists(shared=False)
```

The information can be printed to a file as well.
```py
v = lbryt.list_playlists(file="playlists.txt", fdate=True)
```

# Server

Internally, the functions communicate with the LBRY daemon through
a local JSON-RCP server.
By default, the server is listening on `http://localhost:5279`.

Most functions accept an optional parameter to specify the server address,
although this rarely needs to be provided.
```py
server = "http://localhost:5279"

lbryt.download_single(..., server=server)
lbryt.ch_download_latest(..., server=server)
lbryt.ch_download_latest_multi(..., server=server)
lbryt.redownload_latest(..., server=server)
lbryt.download_claims(..., server=server)
lbryt.print_summary(..., server=server)
lbryt.print_channels(..., server=server)
lbryt.delete_single(..., server=server)
lbryt.ch_cleanup(..., server=server)
lbryt.ch_cleanup_multi(..., server=server)
lbryt.remove_claims(..., server=server)
lbryt.measure_usage(...)
lbryt.cleanup_space(..., server=server)
lbryt.remove_media(..., server=server)
lbryt.count_blobs(..., server=server)
lbryt.count_blobs_all(..., server=server)
lbryt.analyze_blobs(..., server=server)
lbryt.download_missing_blobs(..., server=server)
lbryt.analyze_channel(..., server=server)
lbryt.print_channel_analysis(..., server=server)
lbryt.blobs_move(..., server=server)
lbryt.blobs_move_all(..., server=server)
lbryt.claims_bids(..., server=server)
lbryt.channel_subs(..., server=server)
lbryt.list_accounts(..., server=server)
lbryt.list_playlists(..., server=server)
```
