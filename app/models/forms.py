import datetime

from wtforms import StringField, SubmitField, DateField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm

from app.utils.cpf import cpf_validate, cpf_search
from app.utils.cursos import cursos


def default_serializer(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.__format__('%d/%m/%Y')


class LoginForm(FlaskForm):
    user = StringField()
    password = PasswordField()


class ColoquioForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    date = DateField(validators=[DataRequired()])
    botao = SubmitField()


class ColoquioEditForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    date = DateField(validators=[DataRequired()])
    botao = SubmitField()


class CpfForm(FlaskForm):
    def validate_cpf(form, field):
        if not cpf_validate(field.data):
            return False

    cpf = StringField('cpf', [DataRequired(), Length(14, 14)])
    botao = SubmitField()


class ParticipanteForm(FlaskForm):
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


class ParticipanteEditForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    cpf = StringField('cpf', [DataRequired(), Length(14, 14)])
    curso = SelectField('curso', choices=cursos)
    dateNasc = DateField(validators=[DataRequired()])
    botao = SubmitField()
