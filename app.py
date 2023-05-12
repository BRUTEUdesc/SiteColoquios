import json
import os

from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
import flask_login
from hashlib import sha256
from flask import Blueprint, Flask, render_template, request, redirect, flash, url_for
from utils.database import get_db, init_app
from flask_login import LoginManager, login_user
from models.forms import coloquioForm, editColoquioForm, adicionarForm, paricipanteForm, editParicipanteForm, \
    LoginForm, default_serializer, cpf_validate, cpf_search, cpf_search_palestrante
from utils.generateXLS import generate
from models.user import User
from utils.cursos import cursos

load_dotenv()

login_manager = LoginManager()
bootstrap = Bootstrap5()

blueprint = Blueprint('coloquios', __name__, template_folder='templates')


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        DB_NAME=os.environ.get('DB_NAME'),
        DB_HOST=os.environ.get('DB_HOST'),
        DB_PORT=os.environ.get('DB_PORT'),
        DB_USER=os.environ.get('DB_USER'),
        DB_PASSWORD=os.environ.get('DB_PASSWORD'),
    )

    login_manager.init_app(app)
    bootstrap.init_app(app)
    init_app(app)

    app.register_blueprint(blueprint)

    return app


admin = User(
    os.getenv('USER_USER'),
    os.getenv('USER_PASSWORD'),
)


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect('/login')


@login_manager.user_loader
def user_loader(user_id):
    if user_id == admin.id:
        return admin
    return None


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.user.data
        # TODO: use Werkzeug to hash the password
        password = sha256(form.password.data.encode('utf-8')).hexdigest()
        if username == admin.username and password == admin.password:
            admin.authenticated = True
            login_user(admin)
            return redirect('/')
        else:
            return render_template('login.html', form=form, erro='Email ou senha incorretos')
    return render_template('login.html', form=form, title='Login')


@blueprint.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))


@blueprint.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def home():
    con = get_db()
    with con.cursor() as cur:
        cur.execute('SELECT * FROM coloquios.apresentacao order by id;')
        con.commit()
        data_raw = cur.fetchall()
        data_table = json.dumps(data_raw, default=default_serializer)
        form = coloquioForm()
        data_table = json.loads(data_table)

        if form.validate_on_submit():
            nome = form.nome.data
            date = str(form.date.data)
            cur.execute('INSERT INTO coloquios.apresentacao(titulo, dataCol) VALUES (%s, %s);', (nome, date))
            con.commit()
            return redirect('/')
    return render_template('index.html', dataTable=data_table, form=form)


@blueprint.route('/pessoas', methods=['GET', 'POST'])
@flask_login.login_required
def pessoas():
    con = get_db()
    with con.cursor() as cur:
        cur.execute('SELECT * FROM coloquios.pessoa order by id;')
        con.commit()
        data_raw = cur.fetchall()
        data_table = json.dumps(data_raw, default=default_serializer)
        form = paricipanteForm()
        data_table = json.loads(data_table)

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
            return redirect('/pessoas')
    return render_template('pessoas.html', dataTable=data_table, form=form)


@blueprint.route('/coloquios/<id>', methods=['GET', 'POST'])
@flask_login.login_required
def coloquios(id):
    con = get_db()
    with con.cursor() as cur:
        cur.execute(
            'select id, titulo, dataCol from coloquios.apresentacao where id = %s;',
            (id,))
        con.commit()
        data_coloquio = cur.fetchall()

        cur.execute(
            'SELECT idpar, nome, datanasc, cpf, curso FROM coloquios.pessoa pessoa JOIN '
            'coloquios.participante ba ON pessoa.id = ba.idpar JOIN coloquios.apresentacao b ON b.id = ba.idcol '
            'WHERE b.id = %s;',
            id
        )
        con.commit()
        data_raw = cur.fetchall()

        data_table = json.dumps(data_raw, default=default_serializer)
        data_table = json.loads(data_table)
        form = editColoquioForm()
        cpf_form = adicionarForm()
        if form.validate_on_submit():
            if request.form['submit_button'] == 'update':
                titulo = form.nome.data
                data = form.date.data
                idcol = id
                cur.execute('update coloquios.apresentacao SET titulo = %s, datacol = %s where '
                            'coloquios.apresentacao.id = %s', (titulo, data, idcol))
                con.commit()
                return redirect('/coloquios/' + id)
            if request.form['submit_button'] == 'delete':
                idcol = data_coloquio[0]
                cur.execute('delete from coloquios.apresentacao where coloquios.apresentacao.id = %s', (idcol))
                con.commit()
                return redirect('/')
        error = None

        if cpf_form.validate_on_submit():
            if request.form['submit_button'] == 'add_pessoa':
                cpf = cpf_form.cpf.data
                cur.execute('select id from coloquios.pessoa where cpf = %s', (cpf,))
                con.commit()
                idpar = cur.fetchone()

                cur.execute(
                    'SELECT idpar, nome, datanasc, cpf, curso FROM coloquios.pessoa pessoa '
                    'JOIN coloquios.participante ba ON pessoa.id = ba.idpar '
                    'JOIN coloquios.apresentacao b ON b.id = ba.idcol '
                    'WHERE b.id = %s and pessoa.id = %s;',
                    (id, idpar)
                )
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
                    return redirect('/coloquios/' + id)
            if request.form['submit_button'] == 'remove_pessoa':
                cpf = cpf_form.cpf.data
                cur.execute('select id from coloquios.pessoa where cpf = %s', (cpf,))
                con.commit()
                idpar = cur.fetchone()

                if idpar is None:
                    flash('CPF não cadastrado')
                else:
                    cur.execute('delete from coloquios.participante where idcol = %s and idpar = %s', (id, idpar))
                    con.commit()
                return redirect('/coloquios/' + id)
    return render_template('coloquio.html', id=id, form=form, dataColoquio=data_coloquio, dataTable=data_table,
                           cpfForm=cpf_form, error=error)


@blueprint.route('/coloquios/active/<id>', methods=['GET', 'POST'])
@flask_login.login_required
def active(id):
    con = get_db()
    with con.cursor() as cur:
        cur.execute(
            'select id, titulo, dataCol from coloquios.apresentacao where id = %s;',
            id
        )
        con.commit()
        data_coloquio = cur.fetchall()

        cur.execute(
            'SELECT idpar, nome, datanasc, cpf, curso FROM coloquios.pessoa pessoa JOIN '
            'coloquios.participante ba ON pessoa.id = ba.idpar JOIN coloquios.apresentacao b ON b.id = ba.idcol '
            'WHERE b.id = %s;',
            id
        )
        con.commit()
        data_raw = cur.fetchall()

        data_table = json.dumps(data_raw, default=default_serializer)
        data_table = json.loads(data_table)
        form = paricipanteForm()

        if form.validate_on_submit():
            cpf = form.cpf.data
            nome = form.nome.data
            date = str(form.dateNasc.data)
            curso = form.curso.data

            cur.execute('select id from coloquios.pessoa where cpf = %s', (cpf,))
            idpar = cur.fetchone()

            cur.execute(
                'SELECT idpar, nome, datanasc, cpf, curso FROM coloquios.pessoa pessoa JOIN '
                'coloquios.participante ba ON pessoa.id = ba.idpar JOIN coloquios.apresentacao b ON b.id = ba.idcol '
                'WHERE b.id = %s and pessoa.id = %s;',
                (id, idpar)
            )
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
                    cur.execute('select id from coloquios.pessoa where cpf = %s', (cpf,))
                    idpar = cur.fetchone()
                    cur.execute('insert into coloquios.participante(idcol, idpar) values (%s, %s)', (id, idpar))
                    con.commit()
                    return redirect('/coloquios/active/' + id)
                else:
                    cur.execute('insert into coloquios.participante(idcol, idpar) values (%s, %s)', (id, idpar))
                    con.commit()
                    return redirect('/coloquios/active/' + id)
            return redirect('/coloquios/active/' + id)

    return render_template('active.html', id=id, dataTable=data_table, dataColoquio=data_coloquio, form=form)


@blueprint.route('/coloquios/download/<id>', methods=['GET', 'POST'])
@flask_login.login_required
def download(id):
    return generate(id)


@blueprint.route('/coloquios/apresentadores/<id>', methods=['GET', 'POST'])
@flask_login.login_required
def apresentadores(id):
    con = get_db()
    error = None
    with con.cursor() as cur:
        cur.execute(
            'select * from coloquios.apresentacao where id = %s;',
            (id,))
        data_coloquio = cur.fetchone()

        cur.execute(
            'select id, nome, datanasc, curso, cpf from coloquios.palestrante palestrante '
            'join coloquios.pessoa pessoa on palestrante.idpal = pessoa.id '
            'where pessoa.id = palestrante.idpal and idcol = %s;',
            id
        )
        con.commit()
        data_raw = cur.fetchall()

        data_table = json.dumps(data_raw, default=default_serializer)
        data_table = json.loads(data_table)
        print(data_table)
        form = adicionarForm()
        if form.validate_on_submit():
            if request.form['submit_button'] == 'add':
                cpf = form.cpf.data
                cur.execute('select * from coloquios.pessoa where coloquios.pessoa.cpf=%s', (cpf,))
                pal = cur.fetchone()

                cur.execute(
                    'SELECT idpar FROM coloquios.participante where idcol = %s and idpar = %s;',
                    (id, pal[0])
                )
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
                    return redirect('/coloquios/apresentadores/' + id)
            if request.form['submit_button'] == 'remove':
                cpf = form.cpf.data
                if not cpf_search_palestrante(cpf, id):
                    flash('CPF não cadastrado')
                else:
                    cpf = form.cpf.data
                    idcol = id
                    cur.execute('select * from coloquios.pessoa where coloquios.pessoa.cpf=%s', (cpf,))
                    pal = cur.fetchone()
                    cur.execute(
                        'delete from coloquios.palestrante '
                        'where coloquios.palestrante.idpal = %s '
                        'and coloquios.palestrante.idcol = %s;',
                        (pal[0], idcol[0])
                    )
                    con.commit()
                    return redirect('/coloquios/apresentadores/' + id)

    return render_template('apresentadores.html', id=id, form=form, dataColoquio=data_coloquio, dataTable=data_table,
                           error=error)


@blueprint.route('/pessoas/<cpf>', methods=['GET', 'POST'])
@flask_login.login_required
def pessoasCpf(cpf):
    con = get_db()
    with con.cursor() as cur:
        cur.execute('SELECT * FROM coloquios.pessoa WHERE cpf = %s;', (cpf,))
        data_raw = cur.fetchone()
        data_table = json.dumps(data_raw, default=default_serializer)
        data_table = json.loads(data_table)
        index = 0
        for i in range(0, 9):
            if data_raw[3] == cursos[i]:
                index = i + 1

        form = editParicipanteForm(request.form, curso=cursos[i])
        form.cpf.data = data_raw[4]

        if form.validate_on_submit():
            if request.form['submit_button'] == 'update':
                cpf = form.cpf.data
                nome = form.nome.data
                date = str(form.dateNasc.data)
                curso = form.curso.data
                cur.execute(
                    'UPDATE coloquios.pessoa SET nome = %s,  datanasc = %s, curso = %s WHERE cpf = %s;',
                    (nome, date, curso, cpf)
                )
                con.commit()
                return redirect('/pessoas/' + cpf)
            elif request.form['submit_button'] == 'delete':
                cpf = form.cpf.data
                cur.execute('DELETE FROM coloquios.pessoa Where cpf = %s;', (cpf,))
                con.commit()
                return redirect('/pessoas')

    return render_template('pessoa.html', form=form, x=data_table, dataRaw=data_raw, index=index)
