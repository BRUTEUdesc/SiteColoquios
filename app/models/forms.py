import datetime

from wtforms import StringField, SubmitField, DateField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from app.utils.cursos import cursos
from app.utils.database import get_db


def cpf_validate(cpf):
    print('\n\n\n\n')
    print(cpf)
    listcpf = list(cpf)
    listcpf[3] = ''
    listcpf[7] = ''
    listcpf[11] = ''
    numbers = "".join(listcpf)

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
    con = get_db()
    with con.cursor() as cur:
        cur.execute('SELECT cpf FROM coloquios.pessoa WHERE cpf = %s;', (cpf,))
        con.commit()
        dataRaw = cur.fetchone()
        if dataRaw is None:
            return False
        return True


def cpf_search_palestrante(cpf, id):
    con = get_db()
    with con.cursor() as cur:
        cur.execute(
            'SELECT cpf FROM coloquios.pessoa pessoa JOIN coloquios.palestrante ba ON pessoa.id = '
            'ba.idpal WHERE pessoa.cpf = '
            '%s and ba.idcol = %s;', (cpf, id))
        con.commit()
        dataRaw = cur.fetchone()
        if dataRaw == None:
            return False
        return True


def default_serializer(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.__format__('%d/%m/%Y')

class LoginForm(FlaskForm):
    user = StringField()
    password = PasswordField()


class coloquioForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    date = DateField(validators=[DataRequired()])
    botao = SubmitField()


class editColoquioForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    date = DateField(validators=[DataRequired()])
    botao = SubmitField()


class adicionarForm(FlaskForm):
    def validate_cpf(form, field):
        if not cpf_validate(field.data):
            return False

    cpf = StringField('cpf', [DataRequired(), Length(14, 14)])
    botao = SubmitField()


class paricipanteForm(FlaskForm):
    def validate_cpf(form, field):
        if not cpf_validate(field.data):
            return False
        elif cpf_search(field.data):
            return False

    nome = StringField('nome', validators=[DataRequired()])
    cpf = StringField('cpf', [DataRequired(), Length(14, 14)])
    curso = SelectField('curso', choices=cursos)
    dateNasc = DateField(validators=[DataRequired()])
    botao = SubmitField()


class editParicipanteForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    cpf = StringField('cpf', [DataRequired(), Length(14, 14)])
    curso = SelectField('curso', choices=cursos)
    dateNasc = DateField(validators=[DataRequired()])
    botao = SubmitField()
