# Automatic-Naming-Tool
Automatically names videos according to the jellyfin naming standards

This program can be used to automatically name entire series of videos at once. After ripping a bluray you can run this program to name all the ripped files and move them automatically to wherever your plex/jellyfin folder is in the correct format. for example, title_t00.mkv could be moved to Shows/Name (YEAR)/Season 01/Name S01E01.mkv. This program works perfectly with videos that are unedited, however it should work with videos that have been transcoded or even with burned subtitles. If your video has not been added to the hashlist, you can add it with this program too. Try to avoid adding hashes of videos that have been edited in any way. If you add hashes, add keywords to the json if there are folders or files you want to ignore.

Usage:

requires VideoHash

    pip install VideoHash

python3 hasher.py -h

for more details instructions
