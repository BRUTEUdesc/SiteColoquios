from flask import Blueprint, render_template, redirect, request, flash, url_for
import json
import flask_login

from app.extensions.database import get_db
from app.models.forms import ColoquioForm, default_serializer, ColoquioEditForm, CpfForm, ParticipanteForm
from app.utils.cpf import cpf_validate, cpf_search, cpf_search_palestrante

blueprint = Blueprint('coloquios', __name__, url_prefix='/coloquios')


@blueprint.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def index():
    con = get_db()
    with con.cursor() as cur:
        cur.execute('SELECT * FROM coloquios.apresentacao order by id;')
        con.commit()
        data_raw = cur.fetchall()
        data_table = json.dumps(data_raw, default=default_serializer)
        form = ColoquioForm()
        data_table = json.loads(data_table)

        if form.validate_on_submit():
            nome = form.nome.data
            date = str(form.date.data)
            cur.execute('INSERT INTO coloquios.apresentacao(titulo, dataCol) VALUES (%s, %s);', (nome, date))
            con.commit()
            return redirect(url_for('coloquios.coloquios.index'))
    return render_template('coloquios.html', dataTable=data_table, form=form)


@blueprint.route('/<id>', methods=['GET', 'POST'])
@flask_login.login_required
def coloquio(id):
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
        form = ColoquioEditForm()
        cpf_form = CpfForm()
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
                return redirect(url_for('coloquios.coloquios.index'))
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
                    return redirect(url_for('coloquios.coloquios.coloquio', id=id))
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
                return redirect(url_for('coloquios.coloquios.coloquio', id=id))
    return render_template('coloquio.html', id=id, form=form, dataColoquio=data_coloquio, dataTable=data_table,
                           cpfForm=cpf_form, error=error)


@blueprint.route('/active/<id>', methods=['GET', 'POST'])
@flask_login.login_required
def active(id):
    con = get_db()
    with con.cursor() as cur:
        cur.execute(
            'select id, titulo, dataCol from coloquios.apresentacao where id = %s;',
            id
        )
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
        form = ParticipanteForm()

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


@blueprint.route('/download/<id>', methods=['GET', 'POST'])
@flask_login.login_required
def download(id):
    from app.utils.generateXLS import generate
    return generate(id)


@blueprint.route('/apresentadores/<id>', methods=['GET', 'POST'])
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
        form = CpfForm()
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
