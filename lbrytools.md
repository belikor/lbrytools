# Documentation

## Content

- [Initialization](#initialization)
- [Download](#download)
    - [Download reposts](#download-reposts)
    - [Download invalid claims](#download-invalid-claims)
    - [Multiple downloads](#multiple-downloads)
    - [Downloading collections](#downloading-collections)
    - [Download from file](#download-from-file)
    - [Re-download](#re-download)
- [Printing](#printing)
    - [Printing invalid claims](#printing-invalid-claims)
    - [Printing channels](#printing-channels)
- [Delete](#delete)
    - [Delete invalid claims](#delete-invalid-claims)
    - [Delete claims from channel](#delete-claims-from-channel)
    - [Delete from file](#delete-from-file)
- [Measure disk usage](#measure-disk-usage)
- [Clean up disk space](#clean-up-disk-space)
- [Blobs](#blobs)
    - [Analyze blobs](#analyze-blobs)
    - [Download missing blobs](#download-missing-blobs)
    - [Analyze channel](#analyze-channel)
    - [Print channels analysis](#print-channels-analysis)
    - [Move blobs](#move-blobs)
- [Claims](#claims)
    - [Trending claims](#trending-claims)
    - [Search for claims](#search-for-claims)
    - [Search channel claims](#search-channel-claims)
    - [List created channels](#list-created-channels)
    - [List created claims](#list-created-claims)
- [Channel subscriptions](#channel-subscriptions)
    - [Latest claims from subscriptions](#latest-claims-from-subscriptions)
- [Accounts](#accounts)
- [Playlists](#playlists)
- [Supports](#supports)
    - [Create support](#create-support)
    - [Abandon or change support](#abandon-or-change-support)
    - [Target a certain support](#target-a-certain-support)
    - [Abandon support for invalid claims](#abandon-support-for-invalid-claims)
- [Seeding ratio](#seeding-ratio)
- [Comments](#comments)
    - [Create comments](#create-comments)
    - [Update comments](#update-comments)
    - [Abandon comments](#abandon-comments)
- [Peers](#peers)
    - [Peers in a single claim](#peers-in-a-single-claim)
    - [Peers in multiple claims](#peers-in-multiple-claims)
    - [Peers in a single channel](#peers-in-a-single-channel)
    - [Peers in multiple channels](#peers-in-multiple-channels)
    - [Peers in subscribed channels](#peers-in-subscribed-channels)
- [Wallet](#wallet)
- [Status](#status)
- [Server](#server)

## Initialization

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
from lbrytools import list_ch_subs
from lbrytools import list_ch_subs_latest
from lbrytools import list_accounts
from lbrytools import list_channels
from lbrytools import list_claims
from lbrytools import list_playlists
from lbrytools import list_supports
from lbrytools import print_blobs_ratio
from lbrytools import create_support
from lbrytools import abandon_support
from lbrytools import abandon_support_inv
from lbrytools import target_support
from lbrytools import list_trending_claims
from lbrytools import list_search_claims
from lbrytools import print_ch_claims
from lbrytools import list_comments
from lbrytools import create_comment
from lbrytools import update_comment
from lbrytools import abandon_comment
from lbrytools import list_peers
from lbrytools import list_m_peers
from lbrytools import list_ch_peers
from lbrytools import list_chs_peers
from lbrytools import list_ch_subs_peers
from lbrytools import sync_wallet
from lbrytools import list_lbrynet_status
from lbrytools import list_lbrynet_settings
```

[Go back to _Content_](#content)

## Download

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

By default all blobs will be downloaded, and the media file (mp4, mp3, mkv, etc.)
will be placed in the download directory.
If we want to save the blobs only we can use `save_file=False`.
Only the blobs are required to seed the file in the network.
```py
d = lbryt.download_single("murray-sabrin's-new-book-on-escaping", ddir=ddir, save_file=False)
```

This argument, `save_file`, is `True` by default, and is also present
in other functions that download multiple claims such as `ch_download_latest`,
`redownload_latest`, `download_claims`, and `ch_download_latest_multi`.

[Go back to _Content_](#content)

### Download reposts

A "repost" is a special type of claim that contains a reference
to another claim. It can be thought of as a symbolic link to another claim
created by the same or a different channel.
We cannot download a repost directly but we can extract
the reposted (original) claim, and then download it.
This is controlled with the `repost` parameter:
```py
d = lbryt.download_single(uri="some-repost", repost=True, ddir=ddir)  # download the original claim
d = lbryt.download_single(uri="some-repost", repost=False, ddir=ddir)  # will not download the claim
```

This argument, `repost`, is `True` by default, and is also present
in other functions that download multiple claims such as `ch_download_latest`
and `ch_download_latest_multi`.

The `repost` argument cannot be used with `redownload_latest`
nor `download_claims`, as these only operate on actually downloaded claims,
and a repost cannot be downloaded, it only exists online as a reference
to other online claims.

[Go back to _Content_](#content)

### Download invalid claims

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

[Go back to _Content_](#content)

### Multiple downloads

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

[Go back to _Content_](#content)

### Downloading collections

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

[Go back to _Content_](#content)

### Download from file

Download claims from a file that lists one claim per row,
with the `'claim_id'` in one column.
This type of file can be generated by `print_summary`;
the same separator must be used for producing the file and for parsing it.
```py
p = lbryt.print_summary(file="summary.txt", sep=";")

q = lbryt.download_claims(ddir=ddir, own_dir=True, file="summary.txt", sep=";")
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

[Go back to _Content_](#content)

### Re-download

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

[Go back to _Content_](#content)

## Printing

Print a list of claims that have been downloaded partially or fully
in chronological order, by `'release_time'`.
Older claims appear first.
Certain items don't have `'release time'`, so for these
the `'timestamp'` is used.

Specify a filename to print to that file, otherwise it will print to
the terminal. Optionally add the date to the filename to better keep track
of the written files:
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
or only those for which the media file is missing:
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
including block height, claim id, number of blobs, length (video and audio)
and size in mebibytes (MB), type, name of channel, name of claim,
title of claim, and download path.
The `sanitize` parameter removes the emojis that may be found in the name
of the claim or channel, or in the title. This may be useful if you are
copying this information to a document that doesn't display emojis properly.
We may specify the separator between the data fields; since a claim name
can have a comma as part of the name, a semicolon `;` is used by default:
```py
p = lbryt.print_summary(blocks=False, cid=True, blobs=True, size=True,
                        typ=False, ch=False,
                        name=True, title=True, path=False,
                        sanitize=False,
                        sep=";")
```

We can also restrict printing only a range of items, or only the claims
by a specific channel (it implies `ch=True`).
By default older claims (by release time) are printed first,
but we can reverse the order so that newer items appear first:
```py
p = lbryt.print_summary(start=20)  # From this index until the end
p = lbryt.print_summary(end=40)  # From the beginning until this index
p = lbryt.print_summary(start=100, end=500)  # Delimited range
p = lbryt.print_summary(channel="Veritasium")
p = lbryt.print_summary(reverse=True)
```

When printing the channel's name we can choose whether to find
the name by resolving the claim online or not:
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

[Go back to _Content_](#content)

### Printing invalid claims

Print only the invalid claims by using the `invalid=True` parameter
of `print_summary`. This will be slower than with `invalid=False`
as it needs to resolve each claim online, to see if it's still valid or not:
```py
p = lbryt.print_summary(invalid=True)
p = lbryt.print_summary(file="summary_invalid.txt", invalid=True)
```

By default, it uses a maximum of 32 threads to resolve the claims in parallel;
the number can be lowered or increased depending on the CPU power:
```py
p = lbryt.print_summary(invalid=True, threads=128)
```

If `invalid=True` and `ch=True` or `channel` is used, this will automatically
set `ch_online=False` because for invalid claims the channel name
can only be resolved from the offline database:
```py
p = lbryt.print_summary(invalid=True, ch=True)
p = lbryt.print_summary(invalid=True, channel="mises")
```

[Go back to _Content_](#content)

### Printing channels

Print a list of all unique channels that published the downloaded claims
that we have.
Specify the separator, or it will use a semicolon by default:
```py
o = lbryt.print_channels()
o = lbryt.print_channels(sep=";")
```

Since LBRY allows channels to have the same "base" name, by default
channels are printed in their "full" form (`@MyChannel#3`, `@MyChannel#c6`)
in order to avoid ambiguity.
Certain claims were published anonymously, so for these the channel
is `@_Unknown_`.
Two parameters control whether to use the full name or the canonical name:
```py
o = lbryt.print_channels(full=False)
o = lbryt.print_channels(canonical=True)
```

By default, channel names are printed in three columns for clarity.
Use the `simple` parameter to print all channels in a single string,
each channel separated from another by a `sep` symbol:
```py
o = lbryt.print_channels(simple=True, sep=",")
```

By default, each claim is resolved online in order to get the channel
information from the online database (blockchain).
By default, it uses a maximum of 32 threads to resolve claims,
the number can be lowered or increased depending on the CPU power:
```py
o = lbryt.print_channels(threads=64)
```

With `offline=True` we can resolve the claims from the offline database;
this is quicker but may not print all existing channels
as some of them might have not been resolved when the claims were originally
downloaded.

If `offline=True` is used, `full` and `canonical` have no effect,
and only the base name is printed.
The reason is that the offline database stores only the base name:
```py
o = lbryt.print_channels(offline=True)
```

If we wish to print only channels from invalid claims
we can use `invalid=True`. This implies `offline=True` as well,
as invalid claims cannot be resolved online:
```py
o = lbryt.print_channels(invalid=True)
```

Print the list of channels to a file.
Optionally add the date to the name of the file:
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

If you wish to manually resolve a channel you can use the following function:
```py
ch = lbryt.resolve_channel("@MyChannel")
```

[Go back to _Content_](#content)

## Delete

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

[Go back to _Content_](#content)

### Delete invalid claims

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

[Go back to _Content_](#content)

### Delete claims from channel

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

[Go back to _Content_](#content)

### Delete from file

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

[Go back to _Content_](#content)

## Measure disk usage

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

[Go back to _Content_](#content)

## Clean up disk space

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

[Go back to _Content_](#content)

## Blobs

When a claim is downloaded a group of binary blobs is downloaded into
the `blobfiles` directory. All blobs from all claims are dumped
into this directory without much organization.
By default, the `blobfiles` directory is located in the user's home directory:
```py
bdir = /home/user/.local/share/lbry/lbrynet/blobfiles
```

Count the blobs that exist for a particular claim.
Use the canonical URL, the claim ID, or the claim name.
The `blobfiles` directory can be provided if it's not in the standard location
defined by the daemon configuration:
```py
c = lbryt.count_blobs(uri="how-monero-works-and-why-its-a-better")
c = lbryt.count_blobs(cid="b4f73ad1e09e21457e18e4b3f8da0cc4319f8688", blobfiles=bdir)
```

Print each of the blobs, indicating whether they are present
or not in `blobfiles`:
```py
c = lbryt.count_blobs(uri="The-Essence-of-Money-(2009)", print_each=True)
```

Count all blobs in the system, or consider only the claims by a specific
channel:
```py
c = lbryt.count_blobs_all()
c = lbryt.count_blobs_all(channel="AfterSkool")
```

By default, only a summary is printed; two parameters control whether
to display more information on each claim and its blobs:
```py
c = lbryt.count_blobs_all(print_msg=True)
c = lbryt.count_blobs_all(print_msg=True, print_each=True)
```

By default, the method uses a maximum of 32 threads to resolve claims online
and count their blobs.
The number can be lowered or increased depending on the CPU power:
```py
c = lbryt.count_blobs_all(threads=64)
```

[Go back to _Content_](#content)

### Analyze blobs

If we manually do something with the blobs in the `blobfiles` directory,
we may want to count all files in this directory to see if they match
the blobs that each claim is supposed to have:
```py
a = lbryt.analyze_blobs(blobfiles=bdir)
```

The information on the blobs is contained in the first blob of each claim,
called the "manifest" blob, whose name corresponds to the claim's `'sd_hash'`.

This function wraps around the `count_blobs_all` function so it has the same
input parameters:
```py
a = lbryt.analyze_blobs(channel="Odysee")
a = lbryt.analyze_blobs(threads=64, print_msg=True, print_each=False)
```

[Go back to _Content_](#content)

### Download missing blobs

We can identify claims with missing blobs, either data blobs
or the initial `'sd_hash'` blob, and automatically redownload the claims:
```py
b = lbryt.download_missing_blobs(blobfiles=bdir, ddir=ddir)
```

If we already have many claims in our system this may take a while,
so we may decide to restrict this to only a single channel:
```py
b = lbryt.download_missing_blobs(ddir=ddir, channel="@EatMoreVegans")
```

[Go back to _Content_](#content)

### Analyze channel

We can display a summary of a particular channel by counting all blobs
from all its downloaded claims, both complete and incomplete,
and measure the space that they take in gibibytes (GiB):
```py
c = lbryt.analyze_channel(blobfiles=bdir, channel="@EatMoreVegans")
```

If the channel is not specified, it will analyze all blobs from all valid
claims in the system, and thus provide an overall summary of all downloads.
Beware that this may take considerable time (more than 10 minutes)
if there is a large number of downloaded claims and blobs, for example,
1000 claims with 100 thousand blobs.

Threads are used to reduce processing time (32 by default):
```py
c = lbryt.analyze_channel(threads=128)
```

[Go back to _Content_](#content)

### Print channels analysis

Print a summary for all channels in tabular form.
It will print the number of claims, the number of blobs, and the disk space
in gibibytes (GiB) that those blobs use.

This method uses `analyze_channel` internally with each channel,
so it takes a considerable amount of time to run (more than one hour)
if there is a large number of downloaded claims and blobs.
Threads are used to reduce processing time by processing claims
in parallel (32 by default) and channels in parallel (32 by default):
```py
d = lbryt.print_channel_analysis(blobfiles=bdir)
d = lbryt.print_channel_analysis(threads=128)
d = lbryt.print_channel_analysis(ch_threads=64, threads=96)
```

Print the information split in complete claims, and incomplete claims
in parentheses:
```py
d = lbryt.print_channel_analysis(split=True)
```

Print a bar for each channel representing their disk usage.
In this case, it will show the numerical values combined as if `split=False`:
```py
d = lbryt.print_channel_analysis(bar=True)
```

We can sort the channels by disk usage.
If `reverse=False` it is ascending order (higher usage last),
and with `reverse=True` it will be in descending order (higher usage first):
```py
d = lbryt.print_channel_analysis(bar=True, sort=True, reverse=True)
```

Print the list of channels to a file.
Optionally add the date to the name of the file:
```py
d = lbryt.print_channel_analysis(file="ch_summary.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

### Move blobs

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

[Go back to _Content_](#content)

## Claims

A claim is any object that is recorded in the blockchain,
and that has some LBC supporting its `'name'`.
This is typically channels (the highest bid controls the default `'name'`),
streams (video and audio files, documents), but also reposts, playlists,
and other types.
We may want to see information on our claims, and how many other claims
are competing for the same `'name'`.

We can display claims that are "controlling" and "non-controlling",
depending on whether they have the highest bid for a particular name.
```py
s = lbryt.claims_bids(show_controlling=True, show_non_controlling=False)
s = lbryt.claims_bids(show_non_controlling=True, show_controlling=False)
```

Showing only non-controlling claims helps us know which of our claims
we can support with more LBC if we want them to appear higher
in search results.
In most cases we want to omit our reposts because we don't need reposts
to have a higher bid than the original claim.
```py
s = lbryt.claims_bids(show_non_controlling=True, skip_repost=True)
```

Since LBRY allows two or more channels to have the same base `'name'`,
we can inspect only our channels to see if they are unique,
or if they are outbid by others.
```py
s = lbryt.claims_bids(show_non_controlling=True, channels_only=True)
```

Due to `lbry-sdk` [issue #3381](https://github.com/lbryio/lbry-sdk/issues/3381),
at the moment only 50 competing claims having the same `'name'` can be compared.

Print the information on the claims to a file.
Optionally add the date to the name of the file.
If `compact=True`, the information from a claim will be printed
in a single line, and use the specified separator.
```py
s = lbryt.claims_bids(file="claims.txt", fdate=True)
s = lbryt.claims_bids(file="claims.txt", fdate=True, compact=True, sep=";")
```

Some options only work with `compact=True`, to produce more or less detail
on the claims.
```py
s = lbryt.claims_bids(show_claim_id=True, show_repost_status=True, compact=True)
s = lbryt.claims_bids(show_competing=True, show_reposts=True, compact=True)
```

[Go back to _Content_](#content)

### Trending claims

Display the trending claims in the network.
We can specify different claim types: `'stream'` (downloadable),
`'channel'`, `'repost'`, `'collection'`, or `'livestream'`.
By default, `page=None` so it will display 1000 claims of results.
If we specify a page in the range of 1 to 20, it will only display 50 claims
from that page:
```py
g = lbryt.list_trending_claims()  # all types, 1000 claims
g = lbryt.list_trending_claims(page=12, claim_type="stream")
g = lbryt.list_trending_claims(page=7, claim_type="channel")
```

Some names have complex unicode characters in them, especially emojis.
We can remove these clusters so that the names can be displayed
without problem in all systems.
With the `sanitize` option the complex unicode symbols are replaced
by a monospace heavy vertical bar `'❚'` (unicode U+275A):
```py
g = lbryt.list_trending_claims(sanitize=True)
```

We may decide to display the claim ID, to be able to download
this claim by ID rather than by name. We can also display the title
of the claim instead of its name:
```py
g = lbryt.list_trending_claims(claim_id=True, title=True, sanitize=True)
```

If the claim type is a stream (downloadable content), we can further specify
the type of media: `'video'`, `'audio'`, `'document'`, `'image'`, `'binary'`,
and `'model'`:
```py
g = lbryt.list_trending_claims(claim_type="stream",
                               video_stream=True, audio_stream=True,
                               doc_stream=True, img_stream=True,
                               bin_stream=False, model_stream=False)
```

The trending claims can be printed to a file.
```py
g = lbryt.list_trending_claims(file="claims.txt", fdate=True, sep=';')
```

[Go back to _Content_](#content)

### Search for claims

Display the claims found by searching for a textual string
and by a list of tags:
```py
h = lbryt.list_search_claims(text="lbry")
h = lbryt.list_search_claims(page=3, text="", tags=["cook", "food"])
```

If the string has spaces, both terms will be searched,
but if the words are surrounded by additional quotation marks the search
will be restricted to the entire phrase:
```py
h = lbryt.list_search_claims(text="cooked food", title=True)
h = lbryt.list_search_claims(text='"cooked food"', title=True)
```

This search is performed by the SDK, and thus it isn't very good.
Adding many words to the `text` string will return few results or none.

Other options are the same as for `list_trending_claims`, that is,
`claim_id`, `title`, `claim_type`, `video_stream`, `audio_stream`,
`doc_stream`, `img_stream`, `bin_stream`, `model_stream`,
`sanitize`, `file`, `fdate`, `sep`.

[Go back to _Content_](#content)

### Search channel claims

Display the latest claims by the specified `channel`.
The `number` parameter specifies how many claims will be returned
starting with the newest claim, and going back in time.

With `reverse=True` the newest claims will come first in the printed output,
otherwise the oldest claims will be first:
```py
k = lbryt.print_ch_claims("@lbry:3f", number=10, reverse=True)
```

Various options allow us to display different fields of information.
If `sanitize=True`, it will remove emojis from the displayed names,
which may be necessary if we want to use the output in other programs:
```py
k = lbryt.print_ch_claims("@lbry:3f", number=20,
                          typ=True, ch_name=True, blocks=True, sanitize=True)
```

Instead of displaying the claim name, we can display the title
of the claim. If we want to download the item, we must use
either the claim name or the claim ID, so the latter
can be displayed as well:
```py
k = lbryt.print_ch_claims("@lbry:3f", number=15,
                          claim_id=True, title=True)
```

If `number` is not provided, it defaults to zero,
in which case all claims from the channel will be printed.
If this is done we can also choose an arbitrary range of claims to print:
```py
k = lbryt.print_ch_claims("@TomWoodsTV", start=1005)
k = lbryt.print_ch_claims("@TomWoodsTV", end=75)
k = lbryt.print_ch_claims("@TomWoodsTV", start=445, end=600)
```

The list of claims can be printed directly to a file:
```py
k = lbryt.print_ch_claims("@TomWoodsTV",
                          file="ch_claims.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

### List created channels

Display the channels that we have created in the current wallet:
```py
cc = lbryt.list_channels()
```

In addition to showing channel name and title,
various types of information can be displayed for each channel
including time when the channel was created and last updated, claim ID,
address of the transaction, account of the address,
and amount of LBC staked (base and total):
```py
cc = lbryt.list_channels(updates=True, claim_id=True, addresses=True,
                         accounts=True, amounts=True)
```

With `reverse=True` the newest channels will come first in the list.
If `sanitize=True`, it will remove emojis from the displayed names and titles,
which may be necessary if we want to use the output in other programs:
```py
cc = lbryt.list_channels(reverse=True, sanitize=True)
```

By default the channels will be searched from the wallet
that is called `'default_wallet'`, but this can be changed if needed.
The option `is_spent=True` will get the channel claims
with a transaction that has already been spent.
This means it may show some channels that are expired or no longer exist:
```py
cc = lbryt.list_channels(wallet_id="default_wallet", is_spent=True)
```

The list of channels can be printed directly to a file:
```py
cc = lbryt.list_channels(file="channels.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

### List created claims

Display all claims that we have created in all channels of the current wallet:
```py
ss = lbryt.list_claims()
```

Display the claims corresponding to a single channel, given by name
or claim ID (40-character string).
These must be channels that we control, that is, that are in our wallet:
```py
ss = lbryt.list_claims(channel="@MyPersonalChannel")
ss = lbryt.list_claims(channel_id="c64a02da7f080a81572cac1a51cf7f3464c67058")
```

To display claims for any random channel we can use `print_ch_claims`.

To display only those claims that were published anonymously by us,
that is, without channel:
```py
ss = lbryt.list_claims(anon=True)
```

Various types of information can be displayed for each claim
including time when the claim was created and last updated, claim ID,
address of the transaction, type of claim, type of stream,
and media type (if any), amount of LBC staked (base and total),
channel name, and claim title:
```py
ss = lbryt.list_claims(updates=True, claim_id=True, addresses=True,
                       typ=True, amounts=True, ch_name=True, title=True)
```

With `reverse=True` the newest claims will come first in the list.
If `sanitize=True`, it will remove emojis from the displayed names and titles,
which may be necessary if we want to use the output in other programs:
```py
cc = lbryt.list_claims(reverse=True, sanitize=True)
```

By default the claims will be searched from the wallet
that is called `'default_wallet'`, but this can be changed if needed.
The option `is_spent=True` will get the claims
with a transaction that has already been spent.
This means it may show some claims that are expired or no longer exist:
```py
ss = lbryt.list_claims(wallet_id="default_wallet", is_spent=True)
```

The list of claims can be printed directly to a file:
```py
ss = lbryt.list_claims(file="claims.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

## Channel subscriptions

Display the channels to which we are subscribed,
and whether they are valid (resolved) and have notifications
enabled or not:
```py
q = lbryt.list_ch_subs()
```

By default, it will display all channels.
We can restrict the output to only those
channels that are valid (resolved) or invalid:
```py
q = lbryt.list_ch_subs(show_all=False, filtering="valid", valid=True)
q = lbryt.list_ch_subs(show_all=False, filtering="valid", valid=False)
```

Or to those with or without notifications enabled:
```py
q = lbryt.list_ch_subs(show_all=False, filtering="notifications", notifications=True)
q = lbryt.list_ch_subs(show_all=False, filtering="notifications", notifications=False)
```

By default, the method searches the `"shared"` database,
but it can also search the `"local"` database:
```py
q = lbryt.list_ch_subs(shared=False)
```

By default, the method uses a maximum of 32 threads
to resolve the channels online.
The number can be lowered or increased depending on the CPU power:
```py
q = lbryt.list_ch_subs(threads=64)
```

The information can be printed to a file as well:
```py
q = lbryt.list_ch_subs(file="subs.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

### Latest claims from subscriptions

Display the latest claims from each of the channels to which we are subscribed:
```py
qq = lbryt.list_ch_subs_latest(number=4)
```

By default, `number` cannot be 0; it will be set to 1.
To allow `number=0` we can set `override=True`.
If `number=0` it will search and display all claims of all subscribed channels,
which may take a very long time depending on how many channels
we are subscribed to, and how many claims they have.

The options to filter the list of subscribed channels are the same
from `list_ch_subs`:
```py
qq = lbryt.list_ch_subs_latest(number=3,
                               shared=True,
                               show_all=False, filtering="valid", valid=True,
                               threads=128)
```

We can display some information on the claims, including the claim ID,
type of claim and stream, and title (instead of claim name).
If `sanitize=True`, it will remove emojis from the displayed names,
which may be necessary if we want to use the output in other programs:
```py
qq = lbryt.list_ch_subs_latest(number=5,
                               claim_id=True, type=True, title=False,
                               sanitize=True)
```

We can filter the list of channels also by indices,
and print the information directly to a file:
```py
qq = lbryt.list_ch_subs_latest(number=4,
                               start=33, end=222,
                               file="subs_claims.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

## Accounts

List the accounts in the current wallet,
along with the balance in each account, and the total balance:
```py
a = lbryt.list_accounts()
```

Normally the default wallet is specified, but another wallet
can also be explicitly given:
```py
a = lbryt.list_accounts(wallet_id="default_wallet")
```

It can also show the individual addresses that have been used
for each account:
```py
a = lbryt.list_accounts(addresses=True)
```

The information can be printed to a file as well.
```py
a = lbryt.list_accounts(file="accounts.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

## Playlists

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

[Go back to _Content_](#content)

## Supports

List the supports, along with the amount of LBC staked, the total support,
and the trending score.
By default it will show both claim and channel supports,
but we can specify only one of them if we want.
If `sanitize=True`, it will remove emojis from the displayed names and titles,
which may be necessary if we want to use the output in other programs:
```py
w = lbryt.list_supports()
w = lbryt.list_supports(channels=False)
w = lbryt.list_supports(claims=False)
w = lbryt.list_supports(sanitize=True)
```

We can also choose to show the `'claim_id'`, and choose a specific separator:
```py
w = lbryt.list_supports(claim_id=True, sep=";.;")
```

There may be claims that are 'invalid', meaning that they were removed
but are still supported by us. These will be displayed with their name
between `[brackets]`.
We can choose to display these claims only:
```py
w = lbryt.list_supports(invalid=True)
```

Each claim is resolved online in order to get the full support information.
By default, it uses a maximum of 32 threads to resolve claims,
the number can be lowered or increased depending on the CPU power:
```py
w = lbryt.list_supports(threads=64)
```

There are four trending scores; they are normally combined into one
so that the information displayed is more compact.
This can be controlled with the `combine` argument:
```py
w = lbryt.list_supports(combine=False)
```

The information can be printed to a file as well.
```py
w = lbryt.list_supports(file="supports.txt", fdate=True)
```

[Go back to _Content_](#content)

### Create support

Create a new support for a specified claim, by URL or claim ID,
regardless if there is already a previous support.
```py
w = lbryt.create_support(uri="ep.-1981-forbidden-thinkers-and-their", amount=10)
w = lbryt.create_support(cid="2b6b11a42f51dba3baf06532cbcb1d3b6cc57057", amount=990)
```

[Go back to _Content_](#content)

### Abandon or change support

If the claim already has a support, we can abandon it, or we can update it,
meaning decrease it or increase it.
```py
w = lbryt.abandon_support(uri="how-to-make-it-as-a-controversial")
w = lbryt.abandon_support(cid="e6315c25446e80bd0bc6077126dbb93019055532", keep=100)
```

[Go back to _Content_](#content)

### Target a certain support

We can add a specific amount of support to a claim so that the final support
on it is equal to the specified `target`.
If `target` is above the existing support, some support will be added;
if `target` is below the existing support, some support will be removed;
if `target` is exactly at the existing support, nothing will be added nor removed.
```py
w = lbryt.target_support(uri="@rossmanngroup", target=1000)
w = lbryt.target_support(cid="4494604ae93fe6995cb61dccb1c6a29202155af3", target=333)
```

Each claim has a base support that is provided by the author
and by other users. Our specified `target` cannot be smaller than this value.
If we specify a lower value, all of our existing support, if any,
will be removed.
```
target = base + our_support
target = (author + others) + our_support
```

[Go back to _Content_](#content)

### Abandon support for invalid claims

Invalid claims cannot be resolved online but they may still have
an active support. It is best to completely remove the support or diminish it
as much as possible.

In this case, we cannot use a canonical URL, we can use the `name` or `cid`,
which should refer to a claim that is invalid, otherwise it will be skipped:
```py
w = lbryt.abandon_support_inv(name="@InvalidChannel")
w = lbryt.abandon_support_inv(cid="ff013pghnav...", keep=10)
```

To know if the claim is invalid, it will search the list of all supports
which may take a while. We can also pass this list directly,
by extracting the information from the output of `get_all_supports`.
```py
all_supports = lbryt.get_all_supports()
invalids = all_supports['invalid_supports']
w = lbryt.abandon_support_inv(invalids=invalids, name="cancelled-claim")
```

[Go back to _Content_](#content)

## Seeding ratio

The blob seeding ratio is estimated from the number of times that the words
`"sent"` and `"downloaded"` are found in the log files of `lbrynet`,
normally under `~/.local/share/lbry/lbrynet`.

If Numpy and Matplotlib are available we can generate a plot with histograms
of the blobs processed (uploaded or downloaded) per hour
versus the day they were processed, counting back from today.
```py
vv = lbryt.print_blobs_ratio(plot_hst=True)
```

The logs are normally read automatically from the default `data_dir` directory,
but a specific directory can also be given containing log files
named `lbrynet.log.{n}`.
The analysis of the seeding ratio can be printed to a file as well.
```py
vv = lbryt.print_blobs_ratio(data_dir="many_logs/",
                             file="summary_ratio.txt", fdate=True)
```

[Go back to _Content_](#content)

## Comments

To list the comments from a claim specify the claim by URI, claim ID,
or claim name:
```py
cc = lbryt.list_comments(uri="how-to-shred-an-expert-witness-on-cross:7")
cc = lbryt.list_comments(cid="58414df292294ce894a0907dc064e7a686edb538")
cc = lbryt.list_comments(name="linux-easy-anti-cheat-can't-be-easier")
```

By default, it will show all comments, but we can also list only the
hidden comments or only the visible comments:
```py
cc = lbryt.list_comments("...", hidden=True)
cc = lbryt.list_comments("...", visible=True)
```

By default, it will show all comments with their replies. If we want only
the root level comments, we can use `sub_replies=False`:
```py
cc = lbryt.list_comments("...", sub_replies=False)
```

By default, the comments are only a preview, meaning it will show only
the first 80 characters of the first line of the comment. To show the entire
comments we can use `full=True`:
```py
cc = lbryt.list_comments("...", full=True)
```

By default, the comments are shown with all emojis intact,
however, if we want to use the output in programs that don't suppor emojis
we can remove them with the `sanitize` option:
```py
cc = lbryt.list_comments("...", full=True, sanitize=True)
```

Comments are not part of the LBRY protocol, they are stored in a comments
server, which is Odysee's by default; a different server can be specified:
```py
cc = lbryt.list_comments("...",
                         comm_server="https://comments.odysee.com/api/v2")
```

The comments can be printed to a file:
```py
cc = lbryt.list_comments("what-were-medieval-guilds-really-like",
                         file="comments.txt", fdate=True)
```

[Go back to _Content_](#content)

### Create comments

To create a comment we specify the comment text including any newlines
and markup formatting, a claim by URI or claim ID,
and the author's URI or claim ID:
```py
comment = "Some long comment.\nSecond _line_ of the comment."

cr = lbryt.create_comment(comment=comment,
                          uri="some-claim-name",
                          parent_id=None,
                          author_uri="@MyChannel")

cr = lbryt.create_comment(comment=comment,
                          cid="3e17195d3aa12977e584e0d651bdd89689f80c10",
                          parent_id=None,
                          author_cid="4f26204g2bb02967m47301e752cnn99548g71d22")
```

If `parent_id` is given it should be a 64-bit ID of a previously
published comment. Then the new comment will appear as a reply to it:
```py
parent_id="c7cf405b355f44e55ad2158ed99ed997906db4b1c40cee9d377c7c9f4a492a73"
```

We can only create comments with a channel that we control, meaning that
we must have the private keys of the specified channel with `author_uri`
or `author_cid`. By the default it will search the default wallet
created by `lbrynet`, but we can specify another wallet if we want:
```py
cr = lbryt.create_comment("...", wallet_id="default_wallet")
```

Comments are not part of the LBRY protocol, they are stored in a comments
server, which is Odysee's by default; a different server can be specified:
```py
cr = lbryt.create_comment("...",
                          comm_server="https://comments.odysee.com/api/v2")
```

[Go back to _Content_](#content)

### Update comments

To update a comment we have previously created we specify the new comment text
and then the 64-bit ID of the comment:
```py
comment = "Long edited comment.\nSecond _line_ of the comment."

up = lbryt.update_comment(comment=comment,
                          comment_id="c7cf405b305f24e35ad2158ed89ed187906db4b1c40cge9d367c7c9f4a492a73")
```

We can only update comments made by a channel that we control, meaning that
we have the private keys for this channel.
The channel will be automatically inferred from the `comment_id`.
By default it will search the default wallet created by `lbrynet`,
but we can specify another wallet if we want.
A different comment server can be specified also:
```py
up = lbryt.update_comment("...",
                          wallet_id="default_wallet",
                          comm_server="https://comments.odysee.com/api/v2")
```

[Go back to _Content_](#content)

### Abandon comments

To abandon or remove a comment from the comment server
we specify the 64-bit ID of the comment:
```py
ab = lbryt.abandon_comment(comment_id="c7cf405b305f24e35ad2158ed89ed187906db4b1c40cge9d367c7c9f4a492a73")
```

We can only remove comments made by a channel that we control, meaning that
we have the private keys for this channel.
The channel will be automatically inferred from the `comment_id`.
By default it will search the default wallet created by `lbrynet`,
but we can specify another wallet if we want.
A different comment server can be specified also:
```py
ab = lbryt.abandon_comment("...",
                           wallet_id="default_wallet",
                           comm_server="https://comments.odysee.com/api/v2")
```

[Go back to _Content_](#content)

## Peers

The LBRY network allows anybody to host downloaded files and share them
with the rest of the peers in the network.
Only claims that can be downloaded (streams) will have peers,
other types such as channels, reposts or collections will not have peers.

[Go back to _Content_](#content)

### Peers in a single claim

We can get the peers that are hosting a particular claim provided by URI,
claim ID, or just name:
```py
uu = lbryt.list_peers(uri="but-what-is-a-neural-network-deep:f")
uu = lbryt.list_peers(cid="095962495000d8b052da48649e80ef664f2fab27")
```

If the `claim` argument is provided it should be an already resolved claim,
and not just a string:
```py
claim = lbryt.search_item("vim-alchemy-with-macros")
uu = lbryt.list_peers(claim=claim)
```

The output will present various types of information on the claim,
such as duration, size, `sd_hash`, and the number of user and tracker peers.

If we want to produce a single line of information, we can use `inline=True`;
then we can control whether we print the claim ID, the type of claim,
or the title of the claim.
If we use the `sanitize` option, it will remove the emojis from the output,
which may be useful if we use the output in applications
that don't support emojis:
```
py
uu = lbryt.list_peers("vim-alchemy-with-macros",
                      inline=True,
                      claim_id=True, typ=True, title=True,
                      sanitize=True)
```

The output can be printed to a file:
```py
uu = lbryt.list_peers("ai-generated-artwork-takes-first-place:1",
                      file="peers.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

### Peers in multiple claims

We can get the peers from a list of claims:
```py
claims = ["vim-alchemy-with-macros#b",
          "ai-generated-artwork-takes-first-place:1",
          "thanksgivingroundup:7",
          "did-elon-musk-just-save-free-speech:1",
          "83a23b2e2f20bf9af0d46ad38132e745c35d9ff4",
          "uncharted-expleened:b"]

vv = lbryt.list_m_peers(claims=claims)
```

If `resolve=False` the list of claims is assumed to be
already resolved claims, so we don't need to resolve it again:
```py
c1 = lbryt.search_item("vim-alchemy-with-macros")
c2 = lbryt.search_item("ai-generated-artwork-takes-first-place:1")
c3 = lbryt.search_item("thanksgivingroundup:7")
claims = [c1, c2, c3]
vv = lbryt.list_m_peers(claims=claims, resolve=False)
```

By default it uses maximum 32 threads to search for the peers
in parallel but we can increase or reduce this value.
We can also choose to display the claim ID of the claims, their type,
and show their titles instead of the claim name.
If we sanitize the name or title, it will remove the emojis from the output,
which may be useful if we use the output in applications
that don't support emojis:
```py
vv = lbryt.list_m_peers(claims=claims, threads=64,
                        claim_id=True, typ=True, title=True,
                        sanitize=True)
```

By default the peer search summary of each claim is printed in its own line
but we can choose to print a small paragraph for each claim instead,
by setting `inline=False`:
```
vv = lbryt.list_m_peers(claims=claims, inline=False)
```

The peer search summary of each claim can be printed to a file:
```py
vv = lbryt.list_m_peers(claims=claims,
                        file="claims_peers.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

### Peers in a single channel

We can get the peers that are hosting the latest claims of a particular channel,
starting from the newest claim and going back in time:
```py
ff = lbryt.list_ch_peers("@GTV-Japan", number=50)
```

By default it uses maximum 32 threads to search for the peers of 32 claims
in parallel but we can increase or reduce this value.
We can also choose to display the claim ID of the claims, their type,
and show their titles instead of the claim name.
If we sanitize the name or title, it will remove the emojis from the output,
which may be useful if we use the output in applications
that don't support emojis:
```py
ff = lbryt.list_ch_peers("@fireship", number=50, threads=64,
                         claim_id=True, typ=True, title=True,
                         sanitize=True)
```

By default the summary of each claim is printed in its own line
but we can choose to print a small paragraph for each claim instead,
by setting `inline=False`:
```py
ff = lbryt.list_ch_peers("@fireship", number=4, inline=False)
```

The peer search summary of each claim can be printed to a file:
```py
ff = lbryt.list_ch_peers("@fireship", number=50,
                         file="peers.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

### Peers in multiple channels

We can list the peers for multiple channels at the same time.

Define a list where each element is a list of two elements; the first item
is the name of the channel, and the second is a number indicating how
many claims will be searched for that channel.
If the number is missing it will use the default value (2).
```py
channels = [
    ["@BrodieRobertson#5", 10],
    ["@GTV-Japan", 100],
    ["@VGDocs#6", 50],
]
```

```py
gg = lbryt.list_chs_peers(channels=channels)
```

By using the `number` parameter, the individual numbers in `channels`
are overriden, so the number of claims searched for peers
will be the same for all channels. If the list of channels is long,
they can be shuffled so the channels and claims are searched in a random order:
```py
gg = lbryt.list_chs_peers(channels=channels, number=25, shuffle=True)
```

We can specify threads for searching channels in parallel (8 by default),
and similarly, for each channel, threads for searching claims in parallel
(32 by default).
If the number of claims to search and the number of channels is large,
the channel threads should be increased while the claim threads
should be decreased.
The total number of threads shouldn't be increased too much because
it may cause the peer search to fail completely:
```py
gg = lbryt.list_chs_peers(channels=channels, number=50,
                          ch_threads=8, claim_threads=32)
```

The summary of the peer search per channel can be printed to a file:
```py
gg = lbryt.list_chs_peers(channels=channels, number=25,
                          file="ch_peers.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

### Peers in subscribed channels

We can search the peers of all channels to which we are subscribed.

As the subscribed channels are not part of the blockchain data,
this method searches the local wallet file which is read by `lbrynet`
for the subscribed channels, then it calls `list_chs_peers` on that list.

Search peers for a maximum of 50 claims for all channels
in our subscribed list:
```py
mm = lbryt.list_ch_subs_peers(number=50)
```

By default it uses the shared database, which is synchronized with Odysee,
but we can also use the local database if we want (`shared=False`).
By default, only the channels that actually resolve online will be listed,
however, we can also list all channels in our subscriber list (`valid=False`).
In any case, only valid channels that resolve online
will be searched for peers:
```py
mm = lbryt.list_ch_subs_peers(number=25, shared=True, valid=False)
```

If the number of channels to which we are subscribed is large, we can decide
to restrict the number of channels searched for peers. We can also shuffle
the list to search the channels randomly:
```py
mm = lbryt.list_ch_subs_peers(number=25, start=100)  # starting index
mm = lbryt.list_ch_subs_peers(number=25, end=45)  # ending index
mm = lbryt.list_ch_subs_peers(number=25, start=120, end=245)  # range
mm = lbryt.list_ch_subs_peers(number=25, end=450, shuffle=True)
```

We can specify threads for searching channels in parallel (32 by default),
and similarly, for each channel, threads for searching claims in parallel
(16 by default).
If the number of claims to search and the number of channels is large,
the channel threads should be increased while the claim threads
should be decreased.
The total number of threads shouldn't be increased too much because
it may cause the peer search to fail completely:
```py
mm = lbryt.list_ch_subs_peers(number=50,
                              ch_threads=50, claim_threads=16)
```

The summary of the peer search per channel can be printed to a file:
```py
mm = lbryt.list_ch_subs_peers(number=50,
                              file="ch_subs_peers.txt", fdate=True, sep=";")
```

[Go back to _Content_](#content)

## Wallet

The LBC wallet can be created locally by running `lbrynet`, or by using
Odysee.
If the wallet is created on Odysee, we can authenticate our account,
download that online wallet, and synchronize it locally,
so that the local wallet has the same information as the online wallet
such as followed channels.

We only need the email and password associated with the Odysee account
to perform the synchronization.
By default, it will only download the online data;
we need to specify `sync=True` to complete the operation:
```py
ww = lbryt.sync_wallet(email, password)
ww = lbryt.sync_wallet(email, password, sync=True)
```

By default, it will use the default wallet in our local system,
simply named `'default_wallet'`, but we can choose another wallet if we want:
```py
ww = lbryt.sync_wallet(email, password, wallet_id="default_wallet")
```

The server addresses to authenticate the account and obtain
the online wallet can be provided optionally:
```py
ww = lbryt.sync_wallet(email, password,
                       api_server="https://api.odysee.com",
                       lbry_api="https://api.lbry.com")
```

The address of the local `lbrynet` daemon which applies
the synchronization data can also be specified:
```py
ww = lbryt.sync_wallet(email, password,
                       server="http://localhost:5279")
```

[Go back to _Content_](#content)

## Status

To show the status of the `lbrynet` daemon we can run
```py
ss = lbryt.list_lbrynet_status()
```

To show the settings of the `lbrynet` daemon we can run
```py
st = lbryt.list_lbrynet_settings()
```

These settings can be modified by editing the `daemon_settings.yml`,
and restarting the `lbrynet` daemon.

The information can also be printed to a file:
```py
ss = lbryt.list_lbrynet_status(file="status.txt", fdate=True)
st = lbryt.list_lbrynet_settings(file="setts.txt", fdate=True)
```

[Go back to _Content_](#content)

## Server

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
lbryt.list_ch_subs(..., server=server)
lbryt.list_ch_subs_latest(..., server=server)
lbryt.list_accounts(..., server=server)
lbryt.list_channels(..., server=server)
lbryt.list_claims(..., server=server)
lbryt.list_playlists(..., server=server)
lbryt.list_supports(..., server=server)
lbryt.print_blobs_ratio(..., server=server)
lbryt.create_support(..., server=server)
lbryt.abandon_support(..., server=server)
lbryt.abandon_support_inv(..., server=server)
lbryt.target_support(..., server=server)
lbryt.list_trending_claims(..., server=server)
lbryt.list_search_claims(..., server=server)
lbryt.print_ch_claims(..., server=server)
lbryt.list_comments(..., server=server)
lbryt.create_comment(..., server=server)
lbryt.update_comment(..., server=server)
lbryt.abandon_comment(..., server=server)
lbryt.list_peers(..., server=server)
lbryt.list_m_peers(..., server=server)
lbryt.list_ch_peers(..., server=server)
lbryt.list_chs_peers(..., server=server)
lbryt.list_ch_subs_peers(..., server=server)
lbryt.sync_wallet(..., server=server)
lbryt.list_lbrynet_status(..., server=server)
lbryt.list_lbrynet_settings(..., server=server)
```

[Go back to _Content_](#content)
