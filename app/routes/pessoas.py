import json

import flask_login
from flask import Blueprint, flash, redirect, render_template, url_for, request

from app.extensions.database import get_db
from app.models.forms import ParticipanteForm, default_serializer, ParticipanteEditForm
from app.utils.cpf import cpf_validate, cpf_search
from app.utils.cursos import cursos

blueprint = Blueprint('pessoas', __name__, url_prefix='/pessoas')


@blueprint.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def index():
    con = get_db()
    with con.cursor() as cur:
        cur.execute('SELECT * FROM coloquios.pessoa order by id;')
        con.commit()
        data_raw = cur.fetchall()
        data_table = json.dumps(data_raw, default=default_serializer)
        form = ParticipanteForm()
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
            return redirect(url_for('coloquios.pessoas.index'))
    return render_template('pessoas.html', dataTable=data_table, form=form)


@blueprint.route('<cpf>', methods=['GET', 'POST'])
@flask_login.login_required
def pessoa(cpf):
    con = get_db()
    with con.cursor() as cur:
        cur.execute('SELECT * FROM coloquios.pessoa WHERE cpf = %s;', (cpf,))
        data_raw = cur.fetchone()
        data = json.dumps(data_raw, default=default_serializer)
        data = json.loads(data)

        #Quero todas as colunas de apresentacao onde o id do participante é igual a ID
        cur.execute(
            'SELECT * FROM coloquios.apresentacao coloquio '
            'JOIN coloquios.participante pa ON coloquio.id = pa.idcol '
            'WHERE pa.idpar = %s',
            (data_raw[0],)
        )
        data_participacoes = cur.fetchall()
        updated_data_participacoes = [(row[0], row[1], row[2], 'Participante') for row in data_participacoes]

        cur.execute(
            'SELECT * FROM coloquios.apresentacao coloquio '
            'JOIN coloquios.palestrante pa ON coloquio.id = pa.idcol '
            'WHERE pa.idpal = %s',
            (data_raw[0],)
        )
        new_data = cur.fetchall()
        updated_data_participacoes += [(row[0], row[1], row[2], 'Apresentador') for row in new_data]

        idx = 0
        for i in range(0, 9):
            if data_raw[3] == cursos[i]:
                idx = i

        form = ParticipanteEditForm(request.form, curso=cursos[idx])
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
                return redirect(url_for('coloquios.pessoas.pessoa', cpf=cpf))
            elif request.form['submit_button'] == 'delete':
                cpf = form.cpf.data
                cur.execute('DELETE FROM coloquios.pessoa Where cpf = %s;', (cpf,))
                con.commit()
                return redirect(url_for('coloquios.pessoas.index'))

    return render_template('pessoa.html', form=form, x=data, data_participacoes=updated_data_participacoes, dataRaw=data_raw, index=idx)
