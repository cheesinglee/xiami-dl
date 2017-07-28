#!/usr/bin/python

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from shutil import copyfileobj
import re
import subprocess
import sys

url = sys.argv[1]

song_url_template = 'http://www.xiami.com/song/%s'
regex = r'/(?P<id>\d+)_.+\.mp3'

# parse song page for artist, title, and lyrics
song_id = re.search(regex,url).group('id')
song_url = song_url_template % song_id

print('Reading song info for ID:', song_id)

req = Request(song_url,headers={'User-Agent':'Mozilla/5.0'})
resp = urlopen(req)

body = resp.read()

soup = BeautifulSoup(body,'html.parser')

title = list(soup.find('div',id='title').stripped_strings)[0]

artist_tr = soup.find('table',id='albums_info').find_all('tr')[1]
artist = artist_tr.find('a').get_text()

lrc_div = soup.find('div',class_='lrc_main')
lyrics = lrc_div.get_text()

# download the song
filename_template = '%s - %s.mp3'
filename = filename_template % (artist,title)
print('Downloading', filename)
req = Request(url,headers={'User-Agent':'Mozilla/5.0'})
with urlopen(req) as in_stream, open(filename,'wb') as out_file:
    copyfileobj(in_stream,out_file)

# set metadata
print('writing metadata')
subprocess.run(['id3','-2',
                    '--title',title,
                    '--artist',artist,
                    '-wUSLT',lyrics,
                    filename])

# replaygain
print('running replaygain')
subprocess.run(['mp3gain','-r',filename])
