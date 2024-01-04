from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import date
from website.models import Utilizador
from website import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)
dataHoje = date.today()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        utilizador = Utilizador.query.filter_by(email=email).first()
        if utilizador:
            if check_password_hash(utilizador.password, password):
                flash('Login feito com sucesso!', category='sucesso')
                login_user(utilizador, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('A password não corresponde ao utilizador, por favor tenta de novo', category='erro')
        else:
            flash('O utilizador não existe, precisas de criar um para aceder ao site', category='erro')

    return render_template("login.html", utilizador=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        nome = request.form.get('nome')
        # dataNascimento = request.form.get('dataNascimento')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        utilizador = Utilizador.query.filter_by(email=email).first()
        if utilizador:
            flash('O email já existe, vai para o login', category='erro')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='erro')
        elif len(nome) < 2:
            flash('O nome tem que ter pelo menos duas letras.', category='erro')
        # elif dataHoje - dataNascimento < 18:
        # flash( 'a idade tem que ser superior a 18 anos', category='erro')
        elif password1 != password2:
            flash('A password não coíncide ', category='erro')
        elif len(password1) < 7:
            flash('A password tem que ter pelo menos 7 caractéres.', category='erro')
        else:
            new_user = Utilizador(email=email, nome=nome, password=generate_password_hash(password1, method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            login_user(utilizador, remember=True)
            flash('A conta foi criada com sucesso', category='sucesso')

            return redirect(url_for('views.home'))

    return render_template("sign_up.html", utilizador=current_user)
