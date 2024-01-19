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
    marca = "http://127.0.0.1:5000/carList"
    return render_template("carList.html", utilizador=current_user, modelo=modelo, marca=marca)


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
        concluida = Reservas.query.filter(Reservas.data_final<dataHoje, Reservas.carro_matricula == modelo.matricula).all()

        if reserva or dataHoje > modelo.data_proxima_revisao or dataLegal > modelo.data_ultima_legalizacao:
            modelo.disponivel = 0
        else:
            modelo.disponivel = 1
        if concluida:
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
        data_inicial = ""
        data_final = ""
        try:
            data_inicial = datetime.datetime.strptime(request.form.get('dataInicial'), '%Y-%m-%d').date()

        except ValueError:
            flash('tem que haver 2 datas selecionadas', category='erro')
        else:

            try:
                data_final = datetime.datetime.strptime(request.form.get('dataFinal'), '%Y-%m-%d').date()
            except ValueError:
                flash('tem que haver 2 datas selecionadas', category='erro')

        carro = request.form.get('car')
        modelostr = request.form.get('model')
        modelo = list(modelostr.split(","))
        precototal = request.form.get('preco_total')
        if data_inicial == "" or data_final == "":
            print("")
        elif data_inicial >= data_final:
            flash('a data de inicio não pode ser maior que a data final', category='erro')
        elif carro == "":
            flash('Seleciona uma marca', category='erro')
        elif modelo == "":
            flash('Seleciona um modelo', category='erro')
        else:
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
        if Reservas.utilizador_id == current_user.id:
            Reservas.query.filter_by(id=id).delete()
            db.session.commit()
        flash('Reserva cancelada', category='sucesso')
    return redirect(url_for('views.get_brand'))


@views.route('/alterar-datas', methods=['GET', 'POST'])
@login_required
def alterar():
    id = request.form.get('id')

    return render_template("alterar-datas.html", utilizador=current_user,id=id,dataHoje=dataHoje, dataAmanha=dataAmanha)


@views.route('/alterar-datas/<id>', methods=['POST'])
@login_required
def alterar_data(id):
    data_inicial_alterada = ""
    data_final_alterada = ""
    try:
        data_inicial_alterada = datetime.datetime.strptime(request.form.get('nova_dataInicial'), '%Y-%m-%d').date()

    except ValueError:
        flash('tens que ter a data inicial adicionada', category='erro')
    else:

        try:
            data_final_alterada = datetime.datetime.strptime(request.form.get('nova_dataFinal'), '%Y-%m-%d').date()
        except ValueError:
            flash('tens que ter a data final adicionada', category='erro')
    if data_inicial_alterada == "" or data_final_alterada == "":
        print()
    elif data_inicial_alterada >= data_final_alterada:
        flash('a data de inicio não pode ser maior que a data final', category='erro')
    else:
        reserva = Reservas.query.filter_by(id=id).first()
        reserva.data_inicial = data_inicial_alterada
        reserva.data_final = data_final_alterada
        db.session.commit()
        flash('Data alterada', category='sucesso')
    return redirect(url_for('views.get_brand'))
