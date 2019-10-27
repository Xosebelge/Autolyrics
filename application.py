import os
import json

from database import Database
from lyrics import GeniusLyrics
from convert import convert
from get_link import get_mp3
from unzip import unzip


class Application(object):
    def __init__(self, config_path):
        super(Application, self).__init__()
        self.__genius = GeniusLyrics()
        self.__config = json.load(open(config_path, "r"))
        self.__database = Database(self.__config)
        os.system("mkdir data -p")
        os.chdir("data")

    def get_database(self):
        return self.__database

    def load_new_song(self, song, artist):
        filename = get_mp3(song, artist)
        minus, voice = self.split_song(filename)
        lyrics = self.__genius.find_lyrics(song, artist)
        if lyrics is None:
            lyrics = ""
        timestamps = self.get_timestamps(voice, lyrics)
        self.__database.save_lyrics(song, artist, timestamps, filename, minus, voice)
        return filename, minus, voice, timestamps

    def get_song_full(self, song, artist):
        full, minus, voice = self.__database.find_files(song, artist)
        if full is None:
            full, minus, voice, lyrics = self.load_new_song(song, artist)
        return full

    def get_song_minus(self, song, artist):
        full, minus, voice = self.__database.find_files(song, artist)
        if full is None:
            full, minus, voice, lyrics = self.load_new_song(song, artist)
        return minus

    def get_song_voice(self, song, artist):
        full, minus, voice = self.__database.find_files(song, artist)
        if full is None:
            full, minus, voice, lyrics = self.load_new_song(song, artist)
        return voice

    def get_song_lyrics(self, song, artist):
        lyrics = self.__database.find_lyrics(song, artist)
        if lyrics is None or len(lyrics) == 0:
            full, minus, voice, lyrics = self.load_new_song(song, artist)
        return lyrics

    def split_song(self, filename):
        archive_name = filename + ".zip"
        cmd =f'curl -F \'file=@\"{filename}\"\' "http://127.0.0.1:9000/get_songs" --output \'{archive_name}\''
        print(cmd)
        os.system(cmd)
        tracks = unzip(archive_name)
        print(tracks)
        if "vocals" in tracks[0]:
            return tracks[::-1]
        return tracks

    def get_timestamps(self, voice_mp3, lyrics):
        lyrics_filename = voice_mp3 + "lyrics.txt"
        timestamp_filename = voice_mp3 + "timestamps.json"
        language = "en" if not self.is_russian(lyrics_filename) else "ru"
        with open(lyrics_filename, "w") as f:
            f.write(lyrics)
        os.system(f'python3 -m aeneas.tools.execute_task {voice_mp3} {lyrics_filename} "task_language={language}|os_task_file_format=json|is_text_type=plain" {timestamp_filename}')
        with open(timestamp_filename, "r") as f:
            return convert(json.load(f))

    def is_russian(self, name):
        russian_chars = r"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        return any(c in name for c in russian_chars)

