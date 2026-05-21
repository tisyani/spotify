from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    session
)

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import os
import json

from datetime import datetime

app = Flask(__name__)

# ====================================
# SECRET KEY
# ====================================

app.secret_key = "spotify-secret-key"

# ====================================
# SPOTIFY CONFIG
# ====================================

CLIENT_ID = "5cf8f18cfb4146ec87bedabec2968a41"

CLIENT_SECRET = "77841ce84f27463ba42d8bc5279f94ad"

REDIRECT_URI = "http://127.0.0.1:5000/callback"

SCOPE = "user-top-read user-read-recently-played"

# ====================================
# SPOTIFY OAUTH
# ====================================

sp_oauth = SpotifyOAuth(

    client_id=CLIENT_ID,

    client_secret=CLIENT_SECRET,

    redirect_uri=REDIRECT_URI,

    scope=SCOPE
)

# ====================================
# GLOBAL SPOTIFY OBJECT
# ====================================

sp = None

# ====================================
# CREATE DATA FOLDER
# ====================================

if not os.path.exists("data"):

    os.makedirs("data")

# ====================================
# HOME
# ====================================

@app.route("/")
def home():

    global sp

    token_info = session.get("token_info", None)

    # NOT LOGGED IN
    if not token_info:

        auth_url = sp_oauth.get_authorize_url()

        return redirect(auth_url)

    # LOGGED IN
    sp = spotipy.Spotify(

        auth=token_info["access_token"]
    )

    return render_template("index.html")

# ====================================
# CALLBACK
# ====================================

@app.route("/callback")
def callback():

    global sp

    code = request.args.get("code")

    token_info = sp_oauth.get_access_token(

        code,

        check_cache=False
    )

    session["token_info"] = token_info

    sp = spotipy.Spotify(

        auth=token_info["access_token"]
    )

    return redirect("/")

# ====================================
# SAVE HISTORY
# ====================================

def save_history():

    global sp

    results = sp.current_user_recently_played(limit=50)

    tracks = []

    for item in results["items"]:

        track = item["track"]

        tracks.append({

            "song": track["name"],

            "artist": track["artists"][0]["name"]

        })

    today = datetime.now().strftime("%Y-%m-%d")

    filename = f"data/{today}.json"

    with open(

        filename,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            tracks,

            file,

            indent=4
        )

# ====================================
# TERMINAL COMMANDS
# ====================================

@app.route("/command", methods=["POST"])
def command():

    global sp

    data = request.json

    cmd = data["command"].lower()

    result = ""

    # ====================================
    # HELP
    # ====================================

    if cmd == "help":

        result = """

AVAILABLE COMMANDS

top tracks
top artists
recent tracks
save
clear
help

"""

    # ====================================
    # TOP TRACKS
    # ====================================

    elif cmd == "top tracks":

        results = sp.current_user_top_tracks(

            limit=10
        )

        result += "\n=== TOP TRACKS ===\n\n"

        for i, track in enumerate(

            results["items"],

            start=1
        ):

            result += (

                f"{i}. "

                f"{track['name']} - "

                f"{track['artists'][0]['name']}\n"
            )

    # ====================================
    # TOP ARTISTS
    # ====================================

    elif cmd == "top artists":

        results = sp.current_user_top_artists(

            limit=10
        )

        result += "\n=== TOP ARTISTS ===\n\n"

        for i, artist in enumerate(

            results["items"],

            start=1
        ):

            result += (

                f"{i}. "

                f"{artist['name']}\n"
            )

    # ====================================
    # RECENT TRACKS
    # ====================================

    elif cmd == "recent tracks":

        results = sp.current_user_recently_played(

            limit=50
        )

        result += "\n=== RECENT TRACKS ===\n\n"

        for i, item in enumerate(

            results["items"],

            start=1
        ):

            track = item["track"]

            result += (

                f"{i}. "

                f"{track['name']} - "

                f"{track['artists'][0]['name']}\n"
            )

    # ====================================
    # SAVE HISTORY
    # ====================================

    elif cmd == "save":

        save_history()

        result = "\nHistory saved successfully.\n"

    # ====================================
    # CLEAR TERMINAL
    # ====================================

    elif cmd == "clear":

        result = "__CLEAR__"

    # ====================================
    # UNKNOWN COMMAND
    # ====================================

    else:

        result = "\nUnknown command.\n"

    return jsonify({

        "result": result

    })

# ====================================
# HISTORY WIDGETS
# ====================================

@app.route("/history-data")
def history_data():

    files = os.listdir("data")

    files.sort(reverse=True)

    return jsonify(files)

# ====================================
# LOAD DAY DATA
# ====================================

@app.route("/day/<filename>")
def day(filename):

    with open(

        f"data/{filename}",

        "r",

        encoding="utf-8"

    ) as file:

        data = json.load(file)

    return jsonify(data)

# ====================================
# START APP
# ====================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True
    )