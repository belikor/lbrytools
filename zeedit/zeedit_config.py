#!/bin/python3
"""Configuration module for the `zeedit` script that uses `lbrytools`.

It defines all variables used by the `lbtytools` functions.
Make sure this module is in the same directory as `zeedit.py`.
"""
# =============================================================================
# 1. Download options
#
# LBRY channel name next to the number of claims that should be downloaded
# from them each time the script runs.
# If the number is omitted it will use a default value (2).
# This value will be overriden globally by `number` if it is non-zero.
channels = [
#    ["@lbry:3f", 4],
    ["@Odysee#8", 4],
    ["@RobBraxmanTech", 3],
    ["@samtime#1", 2],
    ["@Veritasium:f", 2],
]

# Download directory that is writeable by the user.
ddir = "/home/user/Downloads"

# Set to 1 (True) to create a directory for each channel,
# or 0 (False) to place all downloaded files in the download directory.
own_dir = 1

# A global number that will override the individual numbers in the `channels`
# list.
# Set to 0 or None to disable.
number = 0

# =============================================================================
# 2. Seeding options
#
# Set it to 1 (True) to delete all media files (mp4, mp3, mkv, etc.)
# after they are downloaded, while keeping the binary blobs intact.
# Only these blobs are used to seed the content.
# Set it to 0 (False) to keep the media files.
seeding_only = 0

# =============================================================================
# 3. Cleanup options
#
# Main directory that contains the downloaded files (ddir)
# and the downloaded blobs (blobfiles).
# In a typical Linux installation both directories are in the same partition.
# ddir  = $HOME/Downloads
# blobs = $HOME/.local/share/lbry/lbrynet/blobfiles
main_dir = "/home/user"

# If the blobfiles directory is symlinked to another partition, then `main_dir`
# can be updated accordingly.
# ddir  = /opt/download
# blobs = $HOME/.local/share/lbry/lbrynet/blobfiles -> /opt/lbryblobfiles/
# main_dir = "/opt"

# Maximum size of the disk in GB that will be used to store LBRY downloads
# and blobs.
# It assumes that `ddir` and `blobfiles` are under the same main directory.
size = 1000

# Percentage of `size` that can fill up before older videos are deleted.
percent = 90

# The content from these channels will not be deleted when the script
# tries to cleanup older files.
never_delete = [
    "@Odysee",
    "@RobBraxmanTech",
]

# Set it to `None` to delete files no matter the channel.
# never_delete = None

# What downloaded content will be deleted to free up space?
# "media" will delete only the final media file (mp4, mp3, mkv, etc.)
# "blobs" will delete only the binary blobs
# "both" will delete both files and blobs
#
# As long as the blobs are present, the content can be seeded to the network,
# and the full media file can be restored.
what_to_delete = "media"

# If `seeding_only = 1` in Section 2 above, `what_to_delete` will be set
# to `both` automatically, so that the older blobs can be deleted to make space
# for new blobs.

# =============================================================================
# 4. Summary options
#
# Most of these are boolean values 1 (True), 0 (False).
# Should a summary of claims be created? This can be used later on
# to redownload the claims in another computer.
sm_summary = 1

# Path and filename of the summary.
sm_file = "/home/user/Documents/lbry_summary.txt"

# Add the day and time to the summary filename.
sm_date = 1

# Which downloaded claims will be printed in the summary?
# "all", print all items
# "incomplete", items that have missing blobs
# "full", items that have all their blobs
# "media", items that have the media file available
# "missing", items that don't have the media file but may have all their blobs
sm_show = "all"

# Print the title of the claim.
sm_title = 0

# Print the type of the claim (video, audio, document, etc.).
sm_type = 0

# Print the path where the file was saved.
sm_path = 0

# Print the `claim_id`.
sm_cid = 1

# Print the total number of blobs and how many are actually downloaded.
sm_blobs = 1

# Print the name of the channel.
# This is slow because it needs to perform a reverse search.
sm_ch = 0

# Print the name of the claim.
sm_name = 1

