import urllib.request
from bs4 import BeautifulSoup
import os
def get_mp3(song, author):
    textToSearch = author +' - ' + song
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    video = soup.findAll(attrs={'class':'yt-uix-tile-link'})[0]
    filename = author + '-' + song
    os.popen(f"youtube-dl -q -f 140 -x --audio-format mp3  https://www.youtube.com{video['href']} -o '{filename}.%(ext)s'").read()
    filename += '.mp3'
    print(filename)
    return filename


