import json
import requests

from flask import Flask, jsonify, render_template, request, redirect, session

app = Flask(__name__)


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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)