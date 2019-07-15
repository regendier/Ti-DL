#!/usr/bin/env python3

# Experimental r2

# !!API PLAYLIST ISSUE ON LINE 141. SEE RESPONSE. PLAYLIST BROKEN!!

# Playlist support added. Max tracks per is currently 100. Implement code to iterate through multiple jsons to increase plist limit.
# Single track and downloading from txt file removed temporarily.
# New CLI untested.
# New fields in config file / cli options in [Main]: tokenOverride, [Playlist]: waitBetweenTracks, taggingScheme.

# standard
import os
import re
import sys
import json
import time
import platform
import argparse
import urllib.request
# from itertools import islice
# from urllib.error import HTTPError

# third party
import requests
import configparser
from mutagen import File
from mutagen.mp4 import MP4, MP4Cover
from mutagen.flac import FLAC, Picture

def GetOsType():
	osPlatform = platform.system()
	if osPlatform == 'Windows':
		return True
	else:
		return False

def osCommands(x):
	if x == "p":
		if GetOsType():
			os.system('pause')
		else:
			os.system("read -rsp $\"\"")
	elif x == "c":
		if GetOsType():
			os.system('cls')
		else:
			os.system("clear")
	else:
		if GetOsType():
			os.system('title Ti-DL R2 (by Sorrow446)')
		else:
			sys.stdout.write("\x1b]2;Ti-DL R2 (by Sorrow446)\x07")

def login(email, pwd, token):
	loginGetReq = requests.post("https://api.tidal.com/v1/login/username?",
	data = {
		"username": email,
		"password": pwd,
		"token": token,
		"clientUniqueKey": "x"
		}
	)
	if loginGetReq.status_code == 200:
		return(json.loads(loginGetReq.text))
	elif loginGetReq.status_code == 401:
		print("Sign in failed. Bad credentials.")
		error(isCli(), 'p', True, False)
	else:
		print(f"Sign in failed. Response from API: {loginGetReq.text}")
		error(isCli(), 'p', True, False)
	
def fetchSubInfo(userId, countryCode, sessionId):	
	subInfoGetReq = requests.get(f"https://api.tidal.com/v1/users/{userId}/subscription?countryCode={countryCode}&sessionid={sessionId}")
	if subInfoGetReq.status_code == 200:
		try:
			subInfoGetReqJ = json.loads(subInfoGetReq.text)
			subType = subInfoGetReqJ['subscription']['type']
		except KeyError:
			print("Account does not have a subscription. You cannot download any tracks without one.")
			error(isCli(), 'p', True, False)
		else:
			if not isCli():
				print(f"Signed in successfully - {subType} account.\n")
	else:
		print(f"Failed to fetch sub info. Response from API: {subInfoGetReq.text}")
		error(isCli(), 'p', True, False)
	
def getConfig(option, section):
	config = configparser.ConfigParser()
	if section == "Main":
		config.read('config.ini')
	else:
		# May not work when script frozen.
		config.read(f"{os.path.dirname(sys.argv[0])}/config.ini")	
	try:
		if option.lower() in ["email", "password", "locale", "quality", "coversize", "namingscheme", "cover"]:
			return config[section][option].strip('"')
		else:
			return config[section][option].strip('"').lower()	
	except KeyError:
		return

def wrap(trackTitle, trackNum, trackTotal, quality, type):
	def reporthook(blocknum, blocksize, totalsize):
		if quality == "LOW":
			qualSpec = "96 kbps AAC"				
		elif quality == "HIGH":
			qualSpec = "320 kbps AAC"
		elif quality == "LOSSLESS":
			qualSpec = "16-bit / 44.1 kHz FLAC"
		else:
			qualSpec = "24-bit FLAC"
		if type == "track":
			l = f"Downloading track 1 of 1: {trackTitle} - {qualSpec}"
		else:
			l = f"Downloading track {trackNum} of {trackTotal}: {trackTitle} - {qualSpec}"
		readsofar = blocknum * blocksize
		if totalsize > 0:
			percent = readsofar * 1e2 / totalsize
			s = "\r%5.f%%" % (
			percent)
			sys.stderr.write(f"{l}{percent:5.0f}%\r")			
			if readsofar >= totalsize:
				sys.stderr.write("\n")
	return reporthook

def fetchMetadata(id, type, locale, countryCode, sessionId, token):
	if type == "album":
		metadataGetResp = requests.get(f"https://listen.tidal.com/v1/pages/album?albumId={id}&locale={locale}&deviceType=DESKTOP&countryCode={countryCode}&token={token}")
	elif type == "track":
		metadataGetResp = requests.get(f"https://listen.tidal.com/v1/tracks/{id}/&locale={locale}&deviceType=DESKTOP&countryCode={countryCode}&token={token}")
	else:
		metadataGetResp = requests.get(f"https://listen.tidal.com/v1/playlists/{id}?countryCode={countryCode}&token={token}")
	if metadataGetResp.status_code != 200:
		print(f"Failed to fetch metadata. Response from API: {metadataGetResp.text}")
		error(isCli(), 'p', True, False)
	else:
		return json.loads(metadataGetResp.text)

def fetchMetadataPlist(id, locale, countryCode, token):
	metadataGetResp = requests.get(f"https://listen.tidal.com/v1/playlists/{id}/items?offset=0&limit=100&locale={locale}&deviceType=BROWSER&countryCode={countryCode}&token={token}")
	if metadataGetResp.status_code != 200:
		print(f"Failed to fetch metadata. Response from API: {metadataGetResp.text}")
		error(isCli(), 'p', True, False)
	else:
		return json.loads(metadataGetResp.text)
		
def fetchTrackUrl(trackId, quality, sessionId):
	if quality == "HI_RES":
		trackUrlGetResp = requests.get(f"https://api.tidalhifi.com/v1/tracks/{trackId}/urlpostpaywall?audioquality={quality}&assetpresentation=FULL&urlusagemode=STREAM&sessionid={sessionId}")
	else:	
		trackUrlGetResp = requests.get(f"https://api.tidal.com/v1/tracks/{trackId}/urlpostpaywall?audioquality={quality}&assetpresentation=FULL&urlusagemode=STREAM&sessionid={sessionId}")
	if trackUrlGetResp.status_code != 200:
		print(f"Failed to fetch track URL. Response from API: {trackUrlGetResp.text}")
		error(isCli(), 'p', True, False)
	else:
		return json.loads(trackUrlGetResp.text)

def fetchTrack(trackUrl, trackTitle, trackNum, trackTotal, fExt, quality, type):
	# Do error handling.
	urllib.request.urlretrieve(trackUrl["urls"][0], f"{trackNum}{fExt}", wrap(trackTitle, trackNum, trackTotal, quality, type))

def multipleArtists(metaj):
	albumArtists = ""
	for item in metaj:
		albumArtists += f'{item["name"]}, '
	return albumArtists[:-2]


def multipleTrArtists(metaj):
	trackArtists = ""
	for item in metaj:
		trackArtists += f'{item["name"]}, '
	return trackArtists[:-2]
	
def fetchAlbumCov(albumCovUrl, coverSize):
	albumCovGetResp = requests.get(f"https://resources.tidal.com/images/{albumCovUrl}/{coverSize}.jpg")
	if albumCovGetResp.status_code == 404:
		print("This album does not have an album cover.")
	elif albumCovGetResp.status_code != 200:
		print(f"Failed to fetch album cover. Response from API: {albumCovGetResp.text}")
		error(isCli(), "p", True, False)
	else:
		with open ("cover.jpg", 'wb') as f:
			f.write(albumCovGetResp.content)

def writeAlbumCov(file):
	if file.endswith('c'):
		audio = File(file)
		image = Picture()
		image.type = 3
		mime = "image/jpeg"
		with open("cover.jpg", 'rb') as f:
			image.data = f.read()
			audio.clear_pictures()
			audio.add_picture(image)
			audio.save()
	else:
		audio = MP4(file)
		with open("cover.jpg", 'rb') as f:
			audio['covr'] = [MP4Cover(f.read(), imageformat = MP4Cover.FORMAT_JPEG)]
			audio.save(file)

def writeTags(file, albumTitle, albumArtist, trackTitle, year, trackNum, trackTotal, trackArtist, comment, copyright, stUrl):
	if file.endswith('c'):
		audio = FLAC(file)
		if getConfig("ALBUM", "Tags") == "y":
			audio['album'] = altitle
		if getConfig("ALBUMARTIST", "Tags") == "y":
			audio['albumartist'] = alartist
		if getConfig("ARTIST", "Tags") == "y":
			audio['artist'] = trackArtist	
		if getConfig("COPYRIGHT", "Tags") == "y":
			audio['copyright'] = copyright	
		if getConfig("DATE", "Tags") == "y":
			audio['date'] = year
		if getConfig("TRACK", "Tags") == "y":	
			audio['track'] = str(trackNum)
		if getConfig("TITLE", "Tags") == "y":		
			audio['title'] = title					
		if getConfig("YEAR", "Tags") == "y":			
			audio['year'] = year
		if getConfig("PERFORMER", "Tags") == "y":
			audio['performer'] = trackArtist
		if getConfig("TRACKNUMBER", "Tags") == "y":
			audio['tracknumber'] = str(trackNum)
		if getConfig("TRACKTOTAL", "Tags") == "y":
			audio['tracktotal'] = str(trackTotal)
		if getConfig("TOTALTRACKS", "Tags") == "y":
			audio['totaltracks'] = str(trackTotal)
		if comment:
			if comment.lower() == "url":
				audio['comment'] = stUrl
			else:
				audio['comment'] = comment
	else:
		audio = MP4(file)
		if getConfig("TITLE", "Tags") == "y":
			audio["\xa9nam"] = trackTitle
		if getConfig("ALBUM", "Tags") == "y":
			audio["\xa9alb"] = albumTitle
		if getConfig("ALBUMARTIST", "Tags") == "y":
			audio["aART"] = albumArtist
		if getConfig("ARTIST", "Tags") == "y":
			audio["\xa9ART"] = trackArtist
		if getConfig("TRACK", "Tags") == "y":
			audio["trkn"] = [(trackNum, trackTotal)]
		if getConfig("YEAR", "Tags") == "y":
			audio["\xa9day"] = year
		if getConfig("COPYRIGHT", "Tags") == "y":		
			audio["cprt"] = copyright
		if comment:
			if comment.lower() == "url":
				audio['\xa9cmt'] = stUrl	
			else:
				audio['\xa9cmt'] = comment
	audio.save()

def fileCheck(file):
	if os.path.isfile(file):
		os.remove(file)

def dirSetup(dir):
	if not os.path.isdir("Ti-DL Downloads"):
		os.mkdir("Ti-DL Downloads")
	os.chdir("Ti-DL Downloads")
	if GetOsType():
		dir = re.sub(r'[\\/:*?"><|]', '-', dir)
	else:
		dir = re.sub('/', '-', dir)
	if not os.path.isdir(dir):
		os.mkdir(dir)
	os.chdir(dir)

def isCli():
	try:
		x = sys.argv[1]
		return True
	except IndexError:
		return False

def error(isCli, x, y, z):
	if isCli:
		if y:
			if z:
				sys.exit(0)
			else:
				sys.exit(1)
	else:
		osCommands(x)

def renameFiles(trackTitle, trackNum, fExt, namingScheme):
	if not str(trackNum).startswith("0"):
		if int(trackNum) < 10:
			finalFilename = f"0{trackNum}{namingScheme}{trackTitle}{fExt}"
			finalFilename = f"0{trackNum}{namingScheme}{trackTitle}{fExt}"
		else:
			finalFilename = f"{trackNum}{namingScheme}{trackTitle}{fExt}"
	else:
		finalFilename = f"{trackNum}{namingScheme}{trackTitle}{fExt}"
	if GetOsType():
		finalFilename = re.sub(r'[\\/:*?"><|]', '-', finalFilename)
	else:
		finalFilename = re.sub('/', '-', finalFilename)
	if os.path.isfile(finalFilename):
		os.remove(finalFilename)
	os.rename(f"{trackNum}{fExt}", finalFilename)
		
# clean up.
def main(quality, sessionId, countryCode, locale, token, namingScheme, coverSize, keepAlbumCover, url):
	if not isCli():
		url = input("Input Tidal web player URL: ")
	try:
		if not url.strip():
			osCommands('c')
			return
		elif url.split('/')[-2] not in ["album", "track", "playlist"]:
			print("Invalid URL.")
			time.sleep(1)
			error(isCli(), 'c', False, True)
		else:	
			type = url.split('/')[-2]
			osCommands('c')
			metaj = fetchMetadata(url.split('/')[-1], type, locale, countryCode, sessionId, token)
			if int(quality) < 4:
				fExt = ".m4a"
				if quality == "1":
					quality = "LOW"
				else:
					quality = "HIGH"
			else:
				fExt = ".flac"
				if quality == "3":
					quality = "LOSSLESS"
				else:
					quality = "HI_RES"
			i = 0
			if type == "album":
				trackTotal = metaj['rows'][0]['modules'][0]['album']['numberOfTracks']
				if len(metaj['rows'][0]['modules'][0]['album']['artists']) > 1:
					albumArtist = multipleArtists(metaj['rows'][0]['modules'][0]['album']['artists'])
				else:	
					albumArtist = metaj['rows'][0]['modules'][0]['album']['artists'][0]['name']
				albumTitle = metaj['rows'][0]['modules'][0]['album']['title']			
				year = metaj['rows'][0]['modules'][0]['album']['releaseDate'].split('-')[0].strip()	
				copyright = metaj['rows'][0]['modules'][0]['album']['copyright']
				comment = ""
				dirSetup(f"{albumArtist} - {albumTitle}")
				print(f"{albumArtist} - {albumTitle}\n")
				fileCheck("cover.jpg")
				fetchAlbumCov(re.sub('-', '/', metaj['rows'][0]['modules'][0]['album']['cover']), coverSize)
				for item in metaj['rows'][1]['modules'][0]['pagedList']['items']:
					i += 1
					fileCheck(f"{i}{fExt}")
					fetchTrack(fetchTrackUrl(item['item']['url'].split('/')[-1], quality, sessionId), item['item']['title'], i, trackTotal, fExt, quality, type)
					if len(item['item']['artists']) > 1:
						trackArtist = multipleTrArtists(item['item']['artists'])
					else:
						trackArtist = item['item']['artists'][0]['name']
					trackTitle = item['item']['title']
					writeAlbumCov(f"{i}{fExt}")
					print(f"{i}{fExt}")
					writeTags(f"{i}{fExt}", albumTitle, albumArtist, trackTitle, year, i, trackTotal, trackArtist, comment, copyright, metaj["rows"][0]["modules"][0]["album"]["url"])
					renameFiles(item['item']['title'], i, fExt)
				# sort this (keepCover).
				os.remove('cover.jpg')
			elif type == "track":
				print("Experimental build. Single track support has been temporarily removed.")
				osCommands('p')
			else:
				if not metaj["publicPlaylist"]:
					if isCli():
						print("Playlist is not public.")
						sys.exit(1)
					else:
						print("Playlist is not public. Returning to URL input screen...")
						time.sleep(2)
						return
				trackTotal = metaj['numberOfTracks']
				if int(trackTotal) > 100:
					print("Support for playlists with more than 100 tracks hasn't been implemented yet.")
					osCommands('p')
				plistTitle = metaj['title']
				dirSetup(plistTitle)
				print(f"{plistTitle}\n")
				metaj = fetchMetadataPlist(url.split('/')[-1], locale, countryCode, token)
				for item in metaj['items']:
					i += 1
					metaj2 = fetchMetadata(item['item']['url'].split('/')[-1], "album", locale, countryCode, sessionId, token)
					albumArtist = metaj2['rows'][0]['modules'][0]['album']['artists'][0]['name']		
					try:
						albumArtist2 = metaj2['rows'][0]['modules'][0]['album']['artists'][1]['name']
					except IndexError:
						pass
					else:
						albumArtist = multipleArtists(item['rows'][0]['modules'][0]['album']['artists'])
					year = metaj2["rows"][0]["modules"][0]["album"]["releaseDate"].split('-')[0].strip()
					fetchTrack(fetchTrackUrl(item['item']['url'].split('/')[-1], quality, sessionId), item['item']['title'], i, trackTotal, fExt, quality, type)
					fetchMetadata(url.split('/')[-1], type, locale, countryCode, sessionId, token)
					if len(item['item']['artists']) > 1:
						trackArtist = multipleTrArtists(item['item']['artists'])
					else:
						trackArtist = item['item']['artists'][0]['name']
					copyright = item['item']['copyright']
					fetchAlbumCov(re.sub('-', '/', item['album']['cover']), getConfig("coverSize", "Main"))
					if item['item']['version']:
						trackTitle = f"{item['item']['title']} ({item['item']['version']})"
					else:
						trackTitle = item['item']['version']
					writeTags(f"{i}{fExt}", item['item']['album']['title'], albumArtist, trackTitle, year, i, trackTotal, trackArtist, comment, copyright, item['item']['url'])
					writeAlbumCov(f"{i}{fExt}")
					renameFiles(item['item']['title'], i, fExt)
					# untested
					if getConfig("waitBetweenTracks", "Playlist"):
						print(f"Waiting for {int(getConfig('waitBetweenTracks', 'Playlist'))} seconds...")
						time.sleep(int(getConfig("waitBetweenTracks", "Playlist")))
				os.chdir(os.path.dirname(sys.argv[0]))
			if isCli():
				sys.exit(0)
			else:
				print("Returning to URL input screen...")
				time.sleep(1)
	except IndexError:
		print("Invalid URL.")
		if not isCli():
			time.sleep(1)
		error(isCli(), 'c', True, False)

# clean up.
if __name__ == '__main__':
	osCommands('t')
	if isCli():
		parser = argparse.ArgumentParser(description="A tool written in Python to download AACs & FLACs from Tidal.")
		parser.add_argument('-e', "--email", help="Email address.")
		parser.add_argument('-pw', "--password", help="Password.")
		parser.add_argument('-u', "--url", help= "Tidal web player URL. Album, track or playlist.", required=True)
		parser.add_argument('-q', "--quality", choices = ['1', '2', '3', '4'], help="Download quality. 1 = low - 96 kbps AAC, 2 = high - 320 kbps AAC, 3 = lossless - 16-bit FLAC, 4 = HI_RES - 24-bit FLAC."
																					"If the chosen qual is unavailable, the next best option will be used as a fallback.")
		parser.add_argument('-d', "--dir", help="Where to download and work in. Make sure you wrap this up in double quotes.")
		parser.add_argument('-l', "--list", help="Download from a list of URLs. -list <txt filename>.")
		parser.add_argument('-cs', "--covsize", choices=['1', '2', '3', '4'], help="Cover size to fetch. 1 = 160x160, 2 = 320x320, 3 = 640x640, 4 = 1280x1280.")
		parser.add_argument('-s', "--scheme", choices=['1', '2'], help="Track naming scheme. 1 = 01. , 2 = 01 -.")
		parser.add_argument('-k', "--keepcov", action='store_true', help="Leave folder.jpg in album dir.")
		parser.add_argument('-c', "--comment", action='store_true', help="Custom comment. You can also input \"URL\" to write the album URL to the field. Make sure you wrap this up in double quotes.")	
		parser.add_argument('-t', "--token", help = "Override default token. Ti-DL doesn't contain code to decrypt encrypted tracks.")
		parser.add_argument('-lo', "--locale", help = "Locale.")
		args = parser.parse_args()
		if args.email:
			email = args.email
		if args.password:
			pwd = args.password
		if args.url:
			url = args.url
		if args.quality:
			quality = args.quality
		if args.covsize:
			coverSize = args.covsize
		if args.dir:
			downloadDir = args.dir
		if args.list:
			txtFile = args.list
		if args.comment:
			comment = args.comment
		if args.token:
			token = args.token
		if args.locale:
			locale = args.locale
		if args.scheme:
			namingScheme = args.scheme
		if args.keepcov:
			keepAlbumCover = args.keepcov				
	if not 'email' in locals():
		email = getConfig("email", "Main")
	if not 'pwd' in locals():
		pwd = getConfig("password", "Main")
	if not 'quality' in locals():
		quality = getConfig("quality", "Main")
	if not 'locale' in locals():	
		locale = getConfig("locale", "Main")
	if not 'keepAlbumCover' in locals():
		keepAlbumCover = getConfig("keepAlbumCover", "Main")
	if not 'namingScheme' in locals():
		namingScheme = getConfig("locale", "Main")
	if not 'token' in locals():
		if not getConfig("tokenOverride", "Main"):
			token = "BI218mwp9ERZ3PFI"
	if not 'coverSize' in locals():
		coverSize = getConfig("coverSize", "Main")
	if not 'downloadDir' in locals():
		downloadDir = getConfig("downloadDir", "Main")
	if not 'url' in locals():
		url = ""
	if downloadDir:
		try:
			os.chdir(getConfig(downloadDir))
		except Exception as e:
			print(f"Failed to CD into {downloadDir}. {e}")
		error(isCli(), '', True, True)
	if namingScheme == "1":
		namingScheme = ". "
	else:
		namingScheme = " - "
	if coverSize == "1":
		coverSize = "160x160"
	elif coverSize == "2":
		coverSize = "320x320"
	elif coverSize == "3":
		coverSize = "640x640"
	else:
		coverSize = "1280x1280"
	loginGetReqJ = login(email, pwd, token)	
	userId = loginGetReqJ['userId']
	countryCode = loginGetReqJ['countryCode']
	sessionId = loginGetReqJ['sessionId']
	fetchSubInfo(userId, countryCode, sessionId)
	while True:
		main(quality, sessionId, countryCode, locale, token, namingScheme, coverSize, keepAlbumCover, url)
