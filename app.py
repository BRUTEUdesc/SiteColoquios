import json
import requests

from config import BOT_TOKEN, CLIENT_SECRET, OAUTH_URL, REDIRECT_URI, PORT
from oauth import Oauth
from flask import Flask, jsonify, render_template, request, redirect, session

app = Flask(__name__)

app.config["SECRET_KEY"] = CLIENT_SECRET


@app.route("/")
def home():
    
    x = [{"id": "1", "titulo_coloquio" : "Pontos flutuantes", "data" : "23/04/2023"}, {"id": "2", "titulo_coloquio" : "AAAAA", "data" : "1/01/2023"},]

    return render_template("index.html", x=x)


@app.route("/coloquios/<id>")
def coloquios(id):
    
    x = [{"id": "1", "NomeCompleto": "Victor Hugo Moresco", "DataNasc" : "04/23/2002", "CPF" : "000.000.000-00", "Curso": "BCC"}]

    return render_template("coloquio.html", id=id, titulo_coloquio="Pontos flutuantes", x=x)

@app.route("/participantes")
def participantes():
    
    x = [{"id": "1", "NomeCompleto": "Victor Hugo Moresco", "DataNasc" : "04/23/2002", "CPF" : "000.000.000-00", "Curso": "Ciência da Computação"}]

    return render_template("participantes.html", x=x)

@app.route("/participantes/<id>")
def participante(id):
    
    x = [{"id": "1", "NomeCompleto": "Victor Hugo Moresco", "DataNasc" : "04/23/2002", "CPF" : "000.000.000-00", "Curso": "BCC"}]

    return render_template("pessoa.html", id=id, x=x)

@app.route("/api/players" , methods=['GET', 'POST'])
def test():
    select = request.json['guild_id']

    guild_raw = requests.get('http://localhost:4000/guilds/players', json={"guild_id": select}).json()

    leaderBoard = []
    #Just merges a bunch of data from the inhouse API and Discord
    for user_raw in guild_raw:
        id = user_raw['player_id']

        user = Oauth.get_any_user(id)
        player_raw = requests.get('http://localhost:4000/guilds/player', json={"guild_id": select, "player_id" : id}).json()

        games = player_raw['wins'] + player_raw['loses'] + player_raw['ties']

        if games > 0:
            wr = player_raw['wins'] / games
        else:
            wr = 0

        userJson = {"player_id" : id, "avatar" : user['avatar'] ,"username" : user['username'], "elo" : player_raw['elo'], "games" : games, "winrate" : wr}
        leaderBoard.append(userJson)
    return jsonify(leaderBoard)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=PORT)