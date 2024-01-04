
from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import date
from website.models import Utilizador
from website import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)
dataHoje = date.today()



@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html", boolean=True)


@auth.route('/logout')
def logout():
    return render_template("home.html")


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')

        nome = request.form.get('nome')
        # dataNascimento = request.form.get('dataNascimento')

        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
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

            new_user = Utilizador(email=email, nome=nome, password=generate_password_hash(password1,method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            flash('A conta foi criada com sucesso', category='sucesso')
            return redirect(url_for('views.home'))


    return render_template("sign_up.html")
