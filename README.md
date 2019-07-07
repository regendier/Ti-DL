# Ti-DL
Tool written in Python to download AACs & FLACs from Tidal for Windows, macOS & Linux.
Sister of [Qo-DL](https://github.com/Sorrow446/Qobuz-DL) and [GPM-DL](https://github.com/Sorrow446/GPM-DL).

**8th Jul: New build coming soon. Currently working on a complete refactor & playlist support.**

Latest versions:   

Windows:   
Ti-DL: 13th Mar 19 - Release 1d   
Ti-DL GUI: 13th Mar 19 - v0.0.5 **Malwarebytes machine learning false positive**   

Linux:   
Ti-DL: 13th Mar 19 - Release 1d

macOS:   
Ti-DL: 13th Mar 19 - Release 1d

Android:   
[Experimental ARM64 - Release 1d](https://thoas.feralhosting.com/sorrow/Tidal-DL/Ti-DL_ARM64.zip)   
Can use guide from Qo-DL GHub page.

![](https://thoas.feralhosting.com/sorrow/Tidal-DL/GUI1.png)
![](https://thoas.feralhosting.com/sorrow/Tidal-DL/GUI2.png)
![](https://thoas.feralhosting.com/sorrow/Tidal-DL/GUI3.png)
![](https://thoas.feralhosting.com/sorrow/Tidal-DL/GUI4.png)
![](https://thoas.feralhosting.com/sorrow/Tidal-DL/b1.jpg)
![](https://thoas.feralhosting.com/sorrow/Tidal-DL/b2.jpg)

# Setup
## Mandatory ##
The following need to be inputted into the config file:
- Email address
- Quality - 1 = LOW (96 kbps), 2 = HIGH (320 kbps), 3 = LOSSLESS, 4 = HI_RES. If the chosen qual is unavailable, the next best option will be used as a fallback.
- Plain text password
- Locale
- Naming scheme - file naming scheme (1 = "01. ", 2 = "01 -").
- Cover size - cover size to request from API (1 = 160x160, 2 = 320x320, 3 = 640x640, 4 = 1280x1280).
- Keep_cover' - leave folder.jpg in album dir, Y or N.
- All tags under "[Tags]" except comment - "Y" or "N".

**You can't download ANY tracks with a free account.**
## Optional ##
- Comment tag - custom comment. You can also input "URL" to write the album URL to the field. 
You can specify what you want to be put into the comment field in your tracks. Special characters will be escaped.
- Move_to - specify where to move album folder after downloading, "" = default.

# Usage
Fill in your config file first.
### Windows ###
Run the exe.
### Linux & macOS ###
CD to wherever the exe is.
```
cd Desktop
```
Make it executable.
```
chmod +x Ti-DL_Lin_x64
```
Launch it.
```
./Ti-DL_Lin_x64
```
or just:
```
chmod +x /Desktop/Ti-DL_Lin_x64
./Desktop/Ti-DL_Lin_x64
```

Ti-DL can also be used via command line.   
**Make sure you cd to Ti-DL's dir before calling it or it might not be able to read your config file properly.**   
```
usage: Ti-DL.py [-h] [-url URL] [-q Q] [-p P] [-list LIST] [-c C] [-s S]
                   [-k K]
optional arguments:
  -h, --help        show this help message and exit
  -url URL          Tidal web player URL.
  -q Q              Download quality. 1 = low (96 kbps), 2 = high (320 kbps),
                    3 = lossless, 4 = HI_RES. If the chosen qual is
                    unavailable, the next best option will be used as a
                    fallback.
  -p P              Where to move album after downloading. Make sure you wrap
                    this up in double quotes.
  -list LIST        Download from a list of URLs. -list <txt filename>.
  -c C              Cover size to fetch. 1 = 160x160, 2 = 320x320, 3 =
                    640x640, 4 = 1280x1280.
  -s S              File naming scheme. 1 = "01. ", 2 = "01 -"
  -k K              Leave folder.jpg in album dir. Y or N.
  -comment COMMENT  Custom comment. You can also input "URL" to write the
                    album URL to the field. Make sure you wrap this up in
                    double quotes.
```
# Update Log
## Ti-DL ##
### 24th Feb 19 - Release 1 ###
### 25th Feb 19 - Release 1a ###
The below would show for everyone but me. Fixed.
```
Account doesn't have a subscription.
```
### 28th Feb 19 - Release 1b ###
- Fixed downloading albums via CLI.
- Much more command line options.
### 3rd Mar 19 - Release 1c ###
- Linux build added.
- Single track download support. This can be used with the "-url" arg too.
- Fixed album artist & track artist tags. If there are more than one, they'll be written to the tags now.
- allowStreaming check for single tracks (still need to do for albums).
- New command line arg option: comment.
- Less strict filename & dir name replace regex. Brackets and commas were being replaced before.
- Windows' max path limit handled. I couldn't do much about this. Ti-DL won't crash anymore if it runs into this. The track's filename will be left as it was before the renaming attempt. Tags won't be affected.
- Unneeded cover.jpg wasn't being deleted before termination. This would only happen when used via command line.
### 13th Mar 19 - Release 1d ###
- Fixed filename / dir name replace regex. Only the characters the OS doesn't support in filenames will be replaced now.
- Fixed the below.
```
TypeError: string indices must be integers
```
This would only happen to tracks which contain artist(s) with only numbers in them.  
- Added x64 Linux and macOS builds.
- Default download folder changed from "Tidal-DL Downloads" to "Ti-DL Downloads".
# Misc Info
Written around Python v3.6.7.
Used libraries:
- argparse
- clint
- codecs
- configparser
- datetime
- glob
- mutagen
- os
- pathlib
- re
- requests
- shutil
- ssl (mac builds only)
- sys
- time
- urllib.request

Misc:
- Any specials characters that Windows doesn't support in filenames are replaced with "-".  
- If an album folder needs to be made, but already exists, it and its contents will be deleted.  
- **If the following files exist in the current working dir, they'll be deleted: (1-1000).flac/.m4a, cover.jpg. This is to avoid any filename clashes. Filename clashes are also handled inside of album folders.**

If you need to get in touch: Sorrow#5631

# To Do
- **Check for checking if users' subscription is eligible to get tracks in chosen quality. Need a Premium account for this (not a Hi-Fi one).**
- Playlist support.
- General code clean up.
- Option in config file to wipe misc tags from tracks after downloading.
Some tracks come with tags like encoder, MQA tags etc. straight from the API.

# Known Issues
- The below will show when downloading single tracks with the -p arg / Move_to active that belong to the same album while the destination album folder already exists. This would make sense for albums, but not for single tracks. You'll never run into this if you keep your download dir default.
```
The destination album folder already exists, and access to delete it was denied. Delete it manually and then press any key.
```
- Printing languages like Chinese, Japanese & Korean to the console prints garbage instead.

This can be fixed by temporarily changing your OS' locale.
- If the "Downloading track x out of y" line is too long for the console, it'll be spammed instead of printed on a single line.

This can be fixed by setting the width & height before calling the exe, like this:
```
REM 200 & 30 should be fine
MODE CON cols=200 lines=30
TI-DL_X64.EXE
```
Enlarging the console window manually by dragging out from the edges might also work.
- Tracks in albums with multiple track artists are broken, but are fine if you use the single tracks download feature.

# Disclaimer
Ti-DL does NOT contain code to decrypt encrypted tracks from Tidal.                  
I will not be responsible for how you use Ti-DL.              
Tidal brand and name is the registered trademark of its respective owner.    
Ti-DL has no partnership, sponsorship or endorsement with Tidal.      
