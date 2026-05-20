from flask import Flask, render_template, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="5cf8f18cfb4146ec87bedabec2968a41",
        client_secret="dc8b120ce5eb436cba048ab44653a0ae",
        redirect_uri="http://127.0.0.1:8888/callback",
        scope="user-top-read user-read-recently-played"
    )
)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/command", methods=["POST"])
def command():

    data = request.get_json()

    cmd = data["command"].lower()

    result = ""

    if cmd == "top tracks":

        tracks = sp.current_user_top_tracks(limit=10)

        for i, track in enumerate(tracks['items'], start=1):

            result += f"{i}. {track['name']} - {track['artists'][0]['name']}\n"


    elif cmd == "top artists":

        artists = sp.current_user_top_artists(limit=10)

        for i, artist in enumerate(artists['items'], start=1):

            result += f"{i}. {artist['name']}\n"


    elif cmd == "recent tracks":

        recent = sp.current_user_recently_played(limit=50)

        for i, item in enumerate(recent['items'], start=1):

            track = item['track']

            result += f"{i}. {track['name']} - {track['artists'][0]['name']}\n"


    else:

        result = "Unknown command"

    return jsonify({
        "result": result
    })


if __name__ == "__main__":
    app.run(debug=True)