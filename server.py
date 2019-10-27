from flask import Flask, request, jsonify
import json
import os
from application import Application
import numpy as np
import pandas as pd
from crepe import process_file # tf > 1.6
from tslearn.metrics import dtw
import uuid

app = Flask(__name__,  static_folder='data')
a = Application('config.json')

@app.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
    return response  

def filter_ts(ts, rate):
    return ts[ts.confidence >= np.percentile(ts.confidence, 100*rate)]


def karaoke_score(dtw, kmin=5):
    k2 = 0.06
    k1 = 1 / np.exp(-k2 * kmin)
    return min([100 * k1 * np.exp(- k2 * dtw), 100])


def make_reference(mp3_filename):
    if not os.path.exists(mp3_filename[:-4] + '.f0.csv'):
        os.system(f'ffmpeg -i {mp3_filename} -acodec pcm_u8 -ar 16000 {mp3_filename[:-4]}.wav')

        process_file(mp3_filename[:-4]+'.wav', model_capacity='small', step_size=20, verbose=False)
    ref_f0 = pd.read_csv(mp3_filename[:-4] + '.f0.csv')
    return ref_f0

@app.route('/asdads')
def hello_world():
    json_name = request.args.get('json_name')
    with open(json_name, 'r') as f:
        return json.load(f)

@app.route('/get_song_full', methods=['GET', 'POST'])
def get_song_full():
    author = request.args.get('author')
    song = request.args.get('song')
    full = a.get_song_full(song, author)
    return app.send_static_file(full)


@app.route('/get_song_minus', methods=['GET', 'POST'])
def get_song_minus():
    author = request.args.get('author')
    song = request.args.get('song')
    minus = a.get_song_minus(song, author)
    return app.send_static_file(minus)

@app.route('/get_song_voice', methods=['GET', 'POST'])
def get_song_voice():
    author = request.args.get('author')
    song = request.args.get('song')
    voice = a.get_song_voice(song, author)
    return app.send_static_file(voice)


@app.route('/get_song_lyrics', methods=['GET', 'POST'])
def get_song_lyrics():
    author = request.args.get('author')
    song = request.args.get('song')
    lyrics = a.get_song_lyrics(song, author)
    return jsonify(lyrics)


@app.route('/all_jsons')
def return_all():
    return jsonify(a.get_database().list_songs())

@app.route('/score', methods=['GET', 'POST'])
def calculate_score():
    #def calculate_score(wav_filename, song, author, filter_rate=0.25):
    file_wav = request.files['file']   
    wav_filename = './'+uuid.uuid1().hex +'.wav'
    print(wav_filename)
    file_wav.save(wav_filename)
    filter_rate=0.25
    author = request.args.get('author')
    song = request.args.get('song')
    start = float(request.args.get('start') if request.args.get('start') is not None else 0)
    end = float(request.args.get('end') if request.args.get('end') is not None else 0)
    #end = float(request.args.get('end'))

    process_file(wav_filename, model_capacity='small', step_size=20, verbose=False)

    ref_f0 = make_reference(a.get_song_voice(song, author))
    if start and end:
        ref_f0 = ref_f0[(ref_f0.time >= start) & (ref_f0.time <=end)]
    user_f0 = pd.read_csv(wav_filename[:-4] + '.f0.csv')
    user_f0 = filter_ts(user_f0, filter_rate)

    dtw_dist = dtw(ref_f0.frequency.values, user_f0.frequency.values) / len(ref_f0)

    return {'score': karaoke_score(dtw_dist)}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')

