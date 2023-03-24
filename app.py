import psycopg2
import datetime
import json
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Length
from urllib.parse import urlparse

conStr = "localhost://postgres:postgres@postgres:5432"
p = urlparse(conStr)

pg_connection_dict = {
    'dbname': p.hostname,
    'user': p.username,
    'password': p.password,
    'port': p.port,
    'host': p.scheme
}

con = psycopg2.connect(**pg_connection_dict)
cur = con.cursor()

Cursos = ['Ciência da Computação', 'Eng.Civil', 'Lic.Quí', 'Lic.Fis', 'Lic.Mat', 'Eng.Elétrica', 'Eng.Mecânica',
          'Eng.Produção', 'TADS']


def default_serializer(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.__format__('%d/%m/%Y')


class coloquioForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    date = DateField(validators=[DataRequired()])
    botao = SubmitField()

class paricipanteForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    cpf = StringField('cpf', validators=[DataRequired(), Length(14,14)])
    curso = SelectField('curso', choices=Cursos)
    dateNasc = DateField(validators=[DataRequired()])
    botao = SubmitField()


app = Flask(__name__)
app.config['SECRET_KEY'] = "BAHSNSKJSDSDS"


@app.route("/", methods=['GET', 'POST'])
def home():
    cur.execute("SELECT * FROM coloquios.apresentacao;")
    con.commit()
    dataRaw = cur.fetchall()
    dataTable = json.dumps(dataRaw, default=default_serializer)
    form = coloquioForm()
    dataTable = json.loads(dataTable)

    if form.validate_on_submit():
        nome = form.nome.data
        date = str(form.date.data)
        cur.execute('INSERT INTO coloquios.apresentacao(titulo, dataCol) VALUES (%s, %s);', (nome, date))

    return render_template("index.html", dataTable=dataTable, form=form)


@app.route("/coloquios/<id>")
def coloquios(id):
    x = [{"id": "1", "NomeCompleto": "Victor Hugo Moresco", "DataNasc": "04/23/2002", "CPF": "000.000.000-00",
          "Curso": "BCC"}]

    return render_template("coloquio.html", id=id, titulo_coloquio="Pontos flutuantes", x=x)


@app.route("/participantes", methods=['GET', 'POST'])
def participantes():
    cur.execute("SELECT * FROM coloquios.participante;")
    con.commit()
    dataRaw = cur.fetchall()
    dataTable = json.dumps(dataRaw, default=default_serializer)
    form = paricipanteForm()
    dataTable = json.loads(dataTable)

    if form.validate_on_submit():
        nome = form.nome.data
        date = str(form.dateNasc.data)
        cpf = form.cpf.data
        curso = form.curso.data

        cpf = cpf.replace('.', '')
        cpf = cpf.replace('-', '')

        cur.execute('INSERT INTO coloquios.participante(nome, datanasc, curso, cpf) VALUES (%s, %s, %s, %s);',
                    (nome, date, curso, cpf))

    return render_template("participantes.html", dataTable=dataTable, form=form)


@app.route("/participantes/<id>")
def participante(id):
    x = [{"id": "1", "NomeCompleto": "Victor Hugo Moresco", "DataNasc": "04/23/2002", "CPF": "000.000.000-00",
          "Curso": "BCC"}]

    return render_template("pessoa.html", id=id, x=x)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
