import psycopg2
import datetime
import json
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError
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

Cursos = ['Ciência da Computação', 'Eng.Civil', 'Lic.Quí', 'Lic.Fis', 'Lic.Mat', 'Eng.Elétrica', 'Eng.Mecânica',
          'Eng.Produção', 'TADS']


def cpf_validate(numbers):
    cpf = [int(char) for char in numbers if char.isdigit()]
    if len(cpf) != 11:
        return False
    if cpf == cpf[::-1]:
        return False
    for i in range(9, 11):
        value = sum((cpf[num] * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != cpf[i]:
            return False
    return True


def cpf_search(cpf):
    with con.cursor() as cur:
        cur.execute('SELECT cpf FROM coloquios.participante WHERE cpf = %s;', (cpf,))
        con.commit()
        dataRaw = cur.fetchone()
        if dataRaw == None:
            return False
        return True


def default_serializer(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.__format__('%d/%m/%Y')


class coloquioForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    date = DateField(validators=[DataRequired()])
    botao = SubmitField()


class paricipanteForm(FlaskForm):
    def validate_cpf(form, field):
        listcpf = list(field.data)
        listcpf[3] = ''
        listcpf[7] = ''
        listcpf[11] = ''
        cpf = "".join(listcpf)
        if not cpf_validate(cpf):
            raise ValidationError('Campo de CPF inválido')
        if cpf_search(field.data):
            raise ValidationError('CPF já cadastrado')

    nome = StringField('nome', validators=[DataRequired()])
    cpf = StringField('cpf', [DataRequired(), Length(14, 14)])
    curso = SelectField('curso', choices=Cursos)
    dateNasc = DateField(validators=[DataRequired()])
    botao = SubmitField()

class editParicipanteForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    cpf = StringField('cpf', [DataRequired(), Length(14, 14)])
    curso = SelectField('curso', choices=Cursos)
    dateNasc = DateField(validators=[DataRequired()])
    botao = SubmitField()

app = Flask(__name__)
app.config['SECRET_KEY'] = "BAHSNSKJSDSDS"


@app.route("/", methods=['GET', 'POST'])
def home():
    with con.cursor() as cur:
        cur.execute("SELECT * FROM coloquios.apresentacao order by id;")
        con.commit()
        dataRaw = cur.fetchall()
        dataTable = json.dumps(dataRaw, default=default_serializer)
        form = coloquioForm()
        dataTable = json.loads(dataTable)

        if form.validate_on_submit():
            nome = form.nome.data
            date = str(form.date.data)
            cur.execute('INSERT INTO coloquios.apresentacao(titulo, dataCol) VALUES (%s, %s);', (nome, date))
            con.commit()

    return render_template("index.html", dataTable=dataTable, form=form)


@app.route("/coloquios/<id>")
def coloquios(id):
    x = [{"id": "1", "NomeCompleto": "Victor Hugo Moresco", "DataNasc": "04/23/2002", "CPF": "000.000.000-00",
          "Curso": "BCC"}]

    return render_template("coloquio.html", id=id, titulo_coloquio="Pontos flutuantes", x=x)


@app.route("/participantes", methods=['GET', 'POST'])
def participantes():
    with con.cursor() as cur:
        cur.execute("SELECT * FROM coloquios.participante order by id;")
        con.commit()
        dataRaw = cur.fetchall()
        dataTable = json.dumps(dataRaw, default=default_serializer)
        form = paricipanteForm()
        dataTable = json.loads(dataTable)

        if form.validate_on_submit():
            cpf = form.cpf.data
            nome = form.nome.data
            date = str(form.dateNasc.data)
            curso = form.curso.data
            cur.execute('INSERT INTO coloquios.participante(nome, datanasc, curso, cpf) VALUES (%s, %s, %s, %s);',
                        (nome, date, curso, cpf))
            con.commit()
    # print(dataTable[0].cpf)
    return render_template("participantes.html", dataTable=dataTable, form=form)


@app.route("/participantes/<cpf>", methods=['GET', 'POST'])
def participante(cpf):
    with con.cursor() as cur:
        cur.execute('SELECT * FROM coloquios.participante WHERE cpf = %s;', (cpf,))
        con.commit()
        dataRaw = cur.fetchone()
        dataTable = json.dumps(dataRaw, default=default_serializer)
        dataTable = json.loads(dataTable)
        form = None
        index = 0
        for i in range(0, 9):
            if dataRaw[3] == Cursos[i]:
                index = i+1

                form = editParicipanteForm(request.form, curso=Cursos[i])
        #form.nome.data = dataRaw[1]
        #form.dateNasc.data = dataRaw[2]
        #form.curso.data = dataRaw[3]
        form.cpf.data = dataRaw[4]

        if form.validate_on_submit():
            if request.form['submit_button'] == 'update':
                cpf = form.cpf.data
                nome = form.nome.data
                date = str(form.dateNasc.data)
                curso = form.curso.data
                cur.execute('UPDATE coloquios.participante SET nome = %s,  datanasc = %s, curso = %s WHERE cpf = %s;',
                            (nome, date, curso, cpf))
                updated_rows = cur.rowcount
                print('\n\n\n')
                print(cur.query)
                con.commit()
            elif request.form['submit_button'] == 'delete':
                print("\n\n\n\naaaaa")

    return render_template("pessoa.html", form=form, x=dataTable, dataRaw=dataRaw, index=index)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
