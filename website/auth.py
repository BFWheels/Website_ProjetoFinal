from flask import Blueprint,render_template, request,flash


auth = Blueprint('auth',__name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    return render_template("login.html", boolean=True)

@auth.route('/logout')
def logout():
    return render_template("home.html")

@auth.route('/sign-up',methods=['GET','POST'])
def sign_up():
    if request.method== 'POST':
        email =request.form.get('email')
        Nome = request.form.get('Nome')
        password1=request.form.get('password1')
        password2= request.form.get('password2')

    if len(email) < 4:
        flash('Email must be greater than 3 characters.', category='erro')
    elif len(Nome)<2:
        flash('O nome tem que ter pelo menos duas letras.', category='erro')
    elif password1 != password2:
        flash('A password não coíncide ', category='erro')
    elif len(password1) < 7:
        flash('A password tem que ter pelo menos 7 caractéres.', category='erro')
    else:
        flash('A conta foi criada com sucesso', category='sucesso')

    return render_template("sign_up.html")