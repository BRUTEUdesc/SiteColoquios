import json
import os

import flask_login
import flask
from hashlib import sha256
from flask import Flask, render_template, request, redirect, flash
from utils.connector import con, Cursos
from flask_login import LoginManager, login_user
from models.forms import coloquioForm, editColoquioForm, adicionarForm, paricipanteForm, editParicipanteForm, LoginForm, \
    default_serializer, cpf_validate, cpf_search, cpf_search_palestrante
from utils.generateXLS import generate
from models.user import User
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
#app.config['SECRET_KEY'] = "BAHSNSKJSDSDS"

login_manager = LoginManager()

login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect('/login')


@login_manager.user_loader
def user_loader(user):
    return User


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User()
        user.password = os.getenv("USER_PASSWORD")
        user.user = os.getenv("USER_USER")
        if user is not None:
            if user.password == sha256(form.password.data.encode('utf-8')).hexdigest():
                user.authenticated = True
                return redirect('/')
        else:
            return render_template('login.html', form=form, erro='Email ou senha incorretos')
    return render_template('login.html', form=form, title='Login')


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login'))


@app.route("/", methods=['GET', 'POST'])
@flask_login.login_required
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
            return redirect("/")
    return render_template("index.html", dataTable=dataTable, form=form)


@app.route("/pessoas", methods=['GET', 'POST'])
@flask_login.login_required
def pessoas():
    with con.cursor() as cur:
        cur.execute("SELECT * FROM coloquios.pessoa order by id;")
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

            if cpf_validate(cpf) is False:
                flash('CPF inválido')
            elif cpf_search(cpf) is True:
                flash('CPF já cadastrado')
            else:
                cur.execute('INSERT INTO coloquios.pessoa(nome, datanasc, curso, cpf) VALUES (%s, %s, %s, %s);',
                            (nome, date, curso, cpf))
                con.commit()
            return redirect("/pessoas")
    # print(dataTable[0].cpf)
    return render_template("pessoas.html", dataTable=dataTable, form=form)


@app.route("/coloquios/<id>", methods=['GET', 'POST'])
@flask_login.login_required
def coloquios(id):
    dataRaw = None
    with con.cursor() as cur:
        cur.execute(
            'select id, titulo, dataCol from coloquios.apresentacao where id = %s;',
            (id,))
        con.commit()
        dataColoquio = cur.fetchall()

        cur.execute(
            'SELECT idpar, nome, datanasc, cpf, curso FROM coloquios.pessoa pessoa JOIN '
            'coloquios.participante ba ON pessoa.id = ba.idpar JOIN coloquios.apresentacao b ON b.id = ba.idcol '
            'WHERE b.id = %s;',
            (id,))
        con.commit()
        dataRaw = cur.fetchall()

        dataTable = json.dumps(dataRaw, default=default_serializer)
        dataTable = json.loads(dataTable)
        form = editColoquioForm()
        cpfForm = adicionarForm()
        if form.validate_on_submit():
            if request.form['submit_button'] == 'update':
                titulo = form.nome.data
                data = form.date.data
                idcol = id
                cur.execute('update coloquios.apresentacao SET titulo = %s, datacol = %s where '
                            'coloquios.apresentacao.id = %s', (titulo, data, idcol))
                con.commit()
                return redirect("/coloquios/" + id)
            if request.form['submit_button'] == 'delete':
                idcol = dataColoquio[0]
                cur.execute('delete from coloquios.apresentacao where coloquios.apresentacao.id = %s', (idcol))
                con.commit()
                return redirect("/")
        idpar = None
        error = None

        if cpfForm.validate_on_submit():
            if request.form['submit_button'] == 'add_pessoa':
                cpf = cpfForm.cpf.data
                idpar = None
                cur.execute('select id from coloquios.pessoa where cpf = %s', (cpf,))
                con.commit()
                idpar = cur.fetchone()

                cadastrado = None
                cur.execute('SELECT idpar, nome, datanasc, cpf, curso FROM coloquios.pessoa pessoa JOIN '
                            'coloquios.participante ba ON pessoa.id = ba.idpar JOIN coloquios.apresentacao b ON b.id = ba.idcol '
                            'WHERE b.id = %s and pessoa.id = %s;',
                            (id, idpar))
                con.commit()
                cadastrado = cur.fetchone()

                if cpf_validate(cpf) is False:
                    flash('CPF inválido')
                elif not cpf_search(cpf):
                    flash('CPF não cadastrado')
                elif cadastrado is not None:
                    flash('CPF já cadastrado')
                else:
                    cur.execute('insert into coloquios.participante(idcol, idpar) values (%s, %s)', (id, idpar))
                    con.commit()
                    return redirect("/coloquios/" + id)
            if request.form['submit_button'] == 'remove_pessoa':
                cpf = cpfForm.cpf.data
                cur.execute('select id from coloquios.pessoa where cpf = %s', (cpf,))
                con.commit()
                idpar = cur.fetchone()

                if idpar is None:
                    flash('CPF não cadastrado')
                else:
                    cur.execute('delete from coloquios.participante where idcol = %s and idpar = %s', (id, idpar))
                    con.commit()
                return redirect("/coloquios/" + id)
    return render_template("coloquio.html", id=id, form=form, dataColoquio=dataColoquio, dataTable=dataTable,
                           cpfForm=cpfForm, error=error)


@app.route("/coloquios/active/<id>", methods=['GET', 'POST'])
@flask_login.login_required
def active(id):
    with con.cursor() as cur:
        cur.execute(
            'select id, titulo, dataCol from coloquios.apresentacao where id = %s;',
            (id,))
        con.commit()
        dataColoquio = cur.fetchall()

        cur.execute(
            'SELECT idpar, nome, datanasc, cpf, curso FROM coloquios.pessoa pessoa JOIN '
            'coloquios.participante ba ON pessoa.id = ba.idpar JOIN coloquios.apresentacao b ON b.id = ba.idcol '
            'WHERE b.id = %s;',
            (id,))
        con.commit()
        dataRaw = cur.fetchall()

        dataTable = json.dumps(dataRaw, default=default_serializer)
        dataTable = json.loads(dataTable)
        form = paricipanteForm()

        if form.validate_on_submit():
            cpf = form.cpf.data
            nome = form.nome.data
            date = str(form.dateNasc.data)
            curso = form.curso.data

            idpar = None
            cur.execute('select id from coloquios.pessoa where cpf = %s', (cpf,))
            idpar = cur.fetchone()

            cadastrado = None
            cur.execute('SELECT idpar, nome, datanasc, cpf, curso FROM coloquios.pessoa pessoa JOIN '
                        'coloquios.participante ba ON pessoa.id = ba.idpar JOIN coloquios.apresentacao b ON b.id = ba.idcol '
                        'WHERE b.id = %s and pessoa.id = %s;',
                        (id, idpar))
            con.commit()
            cadastrado = cur.fetchone()

            if cpf_validate(cpf) is False:
                flash('CPF inválido')
            elif cadastrado is not None:
                flash('CPF já cadastrado')
            else:
                if idpar is None:
                    cur.execute('INSERT INTO coloquios.pessoa(nome, datanasc, curso, cpf) VALUES (%s, %s, %s, %s);',
                                (nome, date, curso, cpf))
                    idpar = None
                    cur.execute('select id from coloquios.pessoa where cpf = %s', (cpf,))
                    idpar = cur.fetchone()
                    cur.execute('insert into coloquios.participante(idcol, idpar) values (%s, %s)', (id, idpar))
                    con.commit()
                    return redirect("/coloquios/active/" + id)
                else:
                    cur.execute('insert into coloquios.participante(idcol, idpar) values (%s, %s)', (id, idpar))
                    con.commit()
                    return redirect("/coloquios/active/" + id)
            return redirect("/coloquios/active/" + id)

    return render_template('active.html', id=id, dataTable=dataTable, dataColoquio=dataColoquio, form=form)


@app.route("/coloquios/download/<id>", methods=['GET', 'POST'])
@flask_login.login_required
def download(id):
    return generate(id)


@app.route("/coloquios/apresentadores/<id>", methods=['GET', 'POST'])
@flask_login.login_required
def apresentadores(id):
    dataRaw = None
    error = None
    with con.cursor() as cur:
        cur.execute(
            'select * from coloquios.apresentacao where id = %s;',
            (id,))
        dataColoquio = cur.fetchone()

        cur.execute('select id, nome, datanasc, curso, cpf from coloquios.palestrante palestrante join '
                    'coloquios.pessoa pessoa on palestrante.idpal = pessoa.id where pessoa.id '
                    '= palestrante.idpal and idcol = %s;',
                    (id,))
        con.commit()
        dataRaw = cur.fetchall()

        dataTable = json.dumps(dataRaw, default=default_serializer)
        dataTable = json.loads(dataTable)
        print(dataTable)
        form = adicionarForm()
        if form.validate_on_submit():
            if request.form['submit_button'] == 'add':
                cpf = form.cpf.data
                pal = None
                cur.execute('select * from coloquios.pessoa where coloquios.pessoa.cpf=%s', (cpf,))
                pal = cur.fetchone()

                cadastrado = None
                cur.execute('SELECT idpar FROM coloquios.participante where idcol = %s and idpar = %s;',
                            (id, pal[0]))
                con.commit()
                cadastrado = cur.fetchone()
                if cpf_search_palestrante(cpf, id):
                    flash('CPF já cadastrado como palestrante')
                elif not cpf_search(cpf):
                    flash('CPF não cadastrado')
                elif cadastrado is not None:
                    print(cadastrado)
                    flash('CPF já cadastrado como participante!')
                else:
                    idcol = id
                    cur.execute('select * from coloquios.pessoa where coloquios.pessoa.cpf=%s', (cpf,))
                    pal = cur.fetchone()
                    con.commit()
                    cur.execute('insert into coloquios.palestrante(idpal, idcol) values (%s, %s);', (pal[0], idcol))
                    con.commit()
                    return redirect("/coloquios/apresentadores/" + id)
            if request.form['submit_button'] == 'remove':
                cpf = form.cpf.data
                if not cpf_search_palestrante(cpf, id):
                    flash('CPF não cadastrado')
                else:
                    cpf = form.cpf.data
                    idcol = id
                    cur.execute('select * from coloquios.pessoa where coloquios.pessoa.cpf=%s', (cpf,))
                    pal = cur.fetchone()
                    cur.execute('delete from coloquios.palestrante where coloquios.palestrante.idpal = %s and '
                                'coloquios.palestrante.idcol = %s;', (pal[0], idcol[0]))
                    con.commit()
                    return redirect("/coloquios/apresentadores/" + id)

    return render_template("apresentadores.html", id=id, form=form, dataColoquio=dataColoquio, dataTable=dataTable,
                           error=error)


@app.route("/pessoas/<cpf>", methods=['GET', 'POST'])
@flask_login.login_required
def pessoasCpf(cpf):
    with con.cursor() as cur:
        cur.execute('SELECT * FROM coloquios.pessoa WHERE cpf = %s;', (cpf,))
        dataRaw = cur.fetchone()
        dataTable = json.dumps(dataRaw, default=default_serializer)
        dataTable = json.loads(dataTable)
        form = None
        index = 0
        for i in range(0, 9):
            if dataRaw[3] == Cursos[i]:
                index = i + 1

        form = editParicipanteForm(request.form, curso=Cursos[i])
        # form.nome.data = dataRaw[1]
        # form.dateNasc.data = dataRaw[2]
        # form.curso.data = dataRaw[3]
        form.cpf.data = dataRaw[4]

        if form.validate_on_submit():
            if request.form['submit_button'] == 'update':
                cpf = form.cpf.data
                nome = form.nome.data
                date = str(form.dateNasc.data)
                curso = form.curso.data
                cur.execute('UPDATE coloquios.pessoa SET nome = %s,  datanasc = %s, curso = %s WHERE cpf = %s;',
                            (nome, date, curso, cpf))
                updated_rows = cur.rowcount
                con.commit()
                return redirect("/pessoas/" + cpf)
            elif request.form['submit_button'] == 'delete':
                cpf = form.cpf.data
                cur.execute('DELETE FROM coloquios.pessoa Where cpf = %s;', (cpf,))
                con.commit()
                return redirect("/pessoas")

    return render_template("pessoa.html", form=form, x=dataTable, dataRaw=dataRaw, index=index)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
