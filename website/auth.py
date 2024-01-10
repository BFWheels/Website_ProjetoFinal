from flask import Blueprint, render_template, request, flash, redirect, url_for
import datetime
from website.models import Utilizador
from website import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)
dataHoje = datetime.date.today()



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
                flash('A password incorreta', category='erro')
        else:
            flash('O utilizador não existe, cria um para aceder ao site', category='erro')

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
        apelido = request.form.get('apelido')
        dataNascimento = request.form.get('dataNascimento')
        nascimento = datetime.datetime.strptime(dataNascimento,'%Y-%m-%d').date()
        ano = datetime.timedelta(dataHoje.year - nascimento.year)
        mes = datetime.timedelta(dataHoje.month - nascimento.month)
        dia = datetime.timedelta(dataHoje.day - nascimento.day)
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        utilizador = Utilizador.query.filter_by(email=email).first()
        if utilizador:
            flash('O email já existe, vai para o login', category='erro')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='erro')
        elif len(nome) < 2:
            flash('O nome tem que ter pelo menos duas letras.', category='erro')
        elif len(apelido) < 2:
            flash('O apelido tem que ter pelo menos duas letras.', category='erro')
        elif ano <= datetime.timedelta(18) and mes <= datetime.timedelta(0) and dia < datetime.timedelta(0):
            flash('a idade tem que ser superior a 18 anos', category='erro')
        elif password1 != password2:
            flash('A password não coíncide ', category='erro')
        elif len(password1) < 7:
            flash('A password tem que ter pelo menos 7 caractéres.', category='erro')
        elif any(char.isupper() for char in password1) < 1:
            flash('A password deve conter pelo menos uma letra maiúscula!', category='erro')
        elif any(not char.isalnum() for char in password1) < 1:
            flash('A password deve conter pelo menos um caracter especial!', category='erro')
        else:
            novo_utilizador = Utilizador(email=email, nome=nome, apelido=apelido, dataNascimento=nascimento,password=generate_password_hash(password1, method='scrypt'))
            db.session.add(novo_utilizador)
            db.session.commit()
            login_user(novo_utilizador, remember=True)
            flash('A conta foi criada com sucesso', category='sucesso')

            return redirect(url_for('views.home'))

    return render_template("sign_up.html", utilizador=current_user)
