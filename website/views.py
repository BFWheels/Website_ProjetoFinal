from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from website.models import Notas
from website import db


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        notas = request.form.get('notas')

        if len(notas) < 1:
            flash('Nota inixistente', category='erro')
        else:
            nova_nota = Notas(data=notas, utilizador_id=current_user.id)
            db.session.add(nova_nota)
            db.session.commit()
            flash('Nota criada', category='sucesso')
    return render_template("home.html", utilizador=current_user)


@views.route('/eliminar/<id>', methods=['POST'])
@login_required
def eliminar(id):
    if request.method == 'POST':
        Notas.query.filter_by(id=id).delete()
        db.session.commit()
        flash('Nota Apagada', category='sucesso')
    return redirect(url_for('views.home'))
