from flask import Blueprint, render_template, redirect, url_for
from hashlib import sha256
import flask_login

from app.models.user import admin
from app.models.forms import LoginForm
from app.extensions.login_manager import login_manager

blueprint = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect('/auth/login')


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
            flask_login.login_user(admin)
            return redirect('/')
        else:
            return render_template('login.html', form=form, erro='Email ou senha incorretos')
    return render_template('login.html', form=form, title='Login')


@blueprint.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('auth.login'))
