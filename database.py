import psycopg2

class Database(object):
    def __init__(self, config):
        super(Database, self).__init__()
        self.__conn = psycopg2.connect(
            dbname=config["database"], 
            user=config["user"], 
            password=config["password"], 
            host=config["host"]
        )
        self.__conn.autocommit=True

    def find_lyrics(self, song, artist):
        query = """
            SELECT time_start, time_end, word, word_index
            FROM songs JOIN words ON (songs.song_id = words.song_id)
            WHERE title = %s AND artist = %s
            ORDER BY word_index ASC
        """
        with self.__conn.cursor() as cursor:
            cursor.execute(query, (song, artist))
            return [(start, end, word) for (start, end, word, index) in cursor]

    def find_files(self, song, artist):
        query = """
            SELECT filename_full, filename_minus, filename_voice
            FROM songs
            WHERE title = %s AND artist = %s
        """
        with self.__conn.cursor() as cursor:
            cursor.execute(query, (song, artist))
            result = cursor.fetchone()
        if result is None:
            result = (None, None, None)
        return result

    def save_lyrics(self, song, artist, lyrics, file_full, file_minus, file_voice):
        insert_song = """
            INSERT INTO 
            songs(title, artist, filename_full, filename_minus, filename_voice) 
            VALUES (%s, %s, %s, %s, %s) RETURNING song_id;
        """
        insert_word = """
            INSERT INTO
            words(song_id, word, word_index, time_start, time_end)
            VALUES 
        """ + ", ".join(["(%s, %s, %s, %s, %s)"] * len(lyrics["words"]))
        with self.__conn.cursor() as cursor:
            cursor.execute(insert_song, (song, artist, file_full, file_minus, file_voice))
            song_id = cursor.fetchone()[0]
            params = []
            for i, word in enumerate(lyrics["words"]):
                params += [song_id, word["word"], i, word["start"], word["end"]]
            cursor.execute(insert_word, tuple(params))

    def delete_lyrics(self, song, artist):
        query = """
            DELETE FROM songs WHERE title = %s AND artist = %s;
        """
        with self.__conn.cursor() as cursor:
            cursor.execute(query, (song, artist))

    def list_songs(self, artist=None):
        query = """
            SELECT title, artist FROM songs
        """
        params = ()
        if artist is not None:
            query = query + " WHERE artist = %s"
            params = (artist)
        query = query + ";"
        with self.__conn.cursor() as cursor:
            cursor.execute(query, params)
            return [(song, artist) for song, artist in cursor]

