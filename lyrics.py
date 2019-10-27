import re
import lyricsgenius

ACCESS_TOKEN = "HDWJiimEMVmlMGQbrqDprcQY2G_lrEVSZYMCYKJp2lNo9G1Iwm96-Ix1WtNE_FBC"

class GeniusLyrics(object):
    def __init__(self, access_token=ACCESS_TOKEN):
        super(GeniusLyrics, self).__init__()
        self.__token = access_token
        self.__genius = lyricsgenius.Genius(self.__token)
        self.__genius.verbose = False
        self.__genius.remove_section_headers = True
        self.__bracket_selector = r"\[[\w\s\n\'\"\.\,\-\?\!\:\;]+\]|\([\w\s\n\'\"\.\,\-\?\!\:\;]+\)"

    def find_lyrics(self, song, artist):
        song = self.__genius.search_song(song, artist=artist, get_full_info=False)
        if song is None:
            return None
        return re.sub(self.__bracket_selector, "", song.lyrics)

    def save_lyrics(self, lyrics, filename):
        with open(filename, "w") as f:
            f.write(lyrics)
