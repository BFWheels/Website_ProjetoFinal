import datetime
import json

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from website import db
from website.models import Reservas, Carro, Modelo

dataHoje = datetime.date.today()
dataLegal = datetime.date(dataHoje.year - 1, dataHoje.month, dataHoje.day)
dataAmanha = datetime.date(dataHoje.year, dataHoje.month, dataHoje.day+1)


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", utilizador=current_user)


# Routes para visualizar carros


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


# Routes para reservas


@views.route('/rent-a-car', methods=['GET', 'POST'])
@login_required
def get_brand():

    # verificar se os carros estão disponiveis
    modelos_marca = []
    carro = Carro.query.all()
    modelos_antes = Modelo.query.all()
    for modelo in modelos_antes:
        reserva = Reservas.query.filter_by(carro_matricula=modelo.matricula).first()
        if reserva or dataHoje > modelo.data_proxima_revisao or dataLegal > modelo.data_ultima_legalizacao:
            modelo.disponivel = 0
        else:
            modelo.disponivel = 1
    db.session.commit()

    if request.method == 'POST':
        carro_json = request.get_json()
        carro = carro_json['car']
        modelos = Modelo.query.filter_by(marca_carro=carro, disponivel=1).all()
        for modelo in modelos:
            json_object = {
                'model': modelo.modelo,
                'preco_dia': modelo.preco_dia,
                'matricula': modelo.matricula
            }
            modelos_marca.append(json_object)
        json_response = json.dumps(modelos_marca)
        return json_response
    return render_template("rent-a-car.html", utilizador=current_user, carro=carro,
                           dataHoje=dataHoje, dataAmanha=dataAmanha)


@views.route('/rent-a-car/reservar', methods=['POST'])
@login_required
def rent_brand():
    if request.method == 'POST':
        print(request.form.get('dataInicial'))
        data_inicial = datetime.datetime.strptime(request.form.get('dataInicial'), '%Y-%m-%d').date()
        data_final = datetime.datetime.strptime(request.form.get('dataFinal'), '%Y-%m-%d').date()

        carro = request.form.get('car')
        modelostr = request.form.get('model')
        modelo = list(modelostr.split(","))
        print(type(modelo))

        precototal = request.form.get('preco_total')
        nova_reserva = Reservas(carro_marca=carro, carro_modelo=modelo[0], carro_matricula=modelo[1],
                                preco_total=precototal, data_inicial=data_inicial, data_final=data_final,
                                utilizador_id=current_user.id)

        db.session.add(nova_reserva)
        db.session.commit()
        flash('Reserva criada', category='sucesso')

    return redirect(url_for('views.get_brand'))


@views.route('/eliminar/<id>', methods=['POST'])
@login_required
def eliminar(id):
    if request.method == 'POST':
        Reservas.query.filter_by(id=id).delete()
        db.session.commit()
        flash('Reserva cancelada', category='sucesso')
    return redirect(url_for('views.get_brand'))


@views.route('/alterarData/<id>', methods=['GET','POST'])
@login_required
def alterar(id):

    if request.method == 'POST':
        Reservas.query.filter_by(id=id).delete()
        db.session.commit()
        flash('Reserva cancelada', category='sucesso')
    return redirect(url_for('views.get_brand'))