from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from website.models import Reservas, Carro, Modelo

from website import db


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        reservas = request.form.get('reservas')
        if len(reservas) < 1:
            flash('Nota inixistente', category='erro')
        else:
            nova_reserva = Reservas(data=reservas, utilizador_id=current_user.id)
            db.session.add(nova_reserva)

            db.session.commit()
            flash('Nota criada', category='sucesso')
    return render_template("home.html", utilizador=current_user)


@views.route('/rent-a-car', methods=['GET', 'POST'])
@login_required
def rent():
    if request.method == 'POST':
        reservas = request.form.get('reservas')

        if len(reservas) < 1:
            flash('Nota inixistente', category='erro')
        else:
            nova_reserva = Reservas(data=reservas, utilizador_id=current_user.id)
            db.session.add(nova_reserva)
            db.session.commit()
            flash('Reserva criada', category='sucesso')
    return render_template("rent-a-car.html", utilizador=current_user)


@views.route('/eliminar/<id>', methods=['POST'])
@login_required
def eliminar(id):
    if request.method == 'POST':
        Reservas.query.filter_by(id=id).delete()
        db.session.commit()
        flash('Reserva cancelada', category='sucesso')
    return redirect(url_for('views.home'))


@views.route('/carList', methods=['GET'])
@login_required
def carlist():
    carro = Carro.query.all()
    return render_template("carList.html", utilizador=current_user, carro=carro)


@views.route('/carList/<marca>', methods=['GET'])
@login_required
def modelist(marca):
    modelo = Modelo.query.filter_by(marca_carro=marca).all()
    return render_template("carList.html", utilizador=current_user, modelo=modelo)

