import datetime
import json

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from website import db
from website.models import Reservas, Carro, Modelo

dataHoje = datetime.date.today()
doisDias = datetime.date(dataHoje.year, dataHoje.month, dataHoje.day - 2)
dataLegal = datetime.date(dataHoje.year - 1, dataHoje.month, dataHoje.day)
dataAmanha = datetime.date(dataHoje.year, dataHoje.month, dataHoje.day + 1)

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

        concluida = Reservas.query.filter(Reservas.data_final <
                                          dataHoje, Reservas.carro_matricula == modelo.matricula).all()
        if reserva and reserva.pagamento == 0 and reserva.date.day < doisDias.day:
            Reservas.query.filter_by(carro_matricula=modelo.matricula).delete()
        if reserva or dataHoje > modelo.data_proxima_revisao or dataLegal > modelo.data_ultima_legalizacao:
            modelo.disponivel = 0
        elif concluida:
            modelo.disponivel = 1
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
        try:
            data_inicial = datetime.datetime.strptime(request.form.get('dataInicial'), '%Y-%m-%d').date()
            data_final = datetime.datetime.strptime(request.form.get('dataFinal'), '%Y-%m-%d').date()
            carro = request.form.get('car')
            modelostr = request.form.get('model')
            modelo = list(modelostr.split(","))
            precototal = request.form.get('preco_total')

            if data_inicial >= data_final:
                flash('a data de inicio tem que ser anterior à data final', category='erro')
                return redirect(url_for('views.get_brand'))
            elif carro == "":
                flash('Seleciona uma marca', category='erro')
                return redirect(url_for('views.get_brand'))
            elif modelo == "":
                flash('Seleciona um modelo', category='erro')
                return redirect(url_for('views.get_brand'))
            else:
                nova_reserva = Reservas(carro_marca=carro, carro_modelo=modelo[0], carro_matricula=modelo[1],
                                        preco_total=precototal, data_inicial=data_inicial, data_final=data_final,
                                        utilizador_id=current_user.id)
                db.session.add(nova_reserva)
                db.session.commit()
                flash('Reserva aceite', category='sucesso')
                return redirect(url_for('views.pagamento', id=nova_reserva.id))
        except ValueError:
            flash(f'Erro ao criar reserva: tens que ter 2 datas preenchidas', category='erro')

    return redirect(url_for('views.get_brand'))


@views.route('/eliminar/<id>', methods=['POST'])
@login_required
def eliminar(id):
    if request.method == 'POST':
        reserva = Reservas.query.filter_by(id=id).first()
        if reserva.utilizador_id == current_user.id:
            Reservas.query.filter_by(id=id).delete()
            db.session.commit()
        flash('Reserva cancelada', category='sucesso')
    return redirect(url_for('views.get_brand'))


@views.route('/alterar-datas', methods=['GET', 'POST'])
@login_required
def alterar():
    id2 = request.form.get('id2')
    return render_template("alterar-datas.html", utilizador=current_user, id=id2,
                           dataHoje=dataHoje, dataAmanha=dataAmanha)


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
    if data_inicial_alterada >= data_final_alterada:
        flash('a data de inicio não pode ser maior que a data final', category='erro')
    else:
        reserva = Reservas.query.filter_by(id=id).first()
        modelo = Modelo.query.filter_by(matricula=reserva.carro_matricula).first()
        reserva.data_inicial = data_inicial_alterada
        reserva.data_final = data_final_alterada
        precototal_novo = int(abs(data_final_alterada.day - data_inicial_alterada.day) * modelo.preco_dia)
        preco_antigostr = reserva.preco_total.split('€')
        preco_antigo = int(preco_antigostr[0])
        if reserva.pagamento == 1:
            if preco_antigo < precototal_novo:
                divida_restante = precototal_novo - preco_antigo
                reserva.preco_total = f'{divida_restante} €'
                reserva.pagamento = 0
                reserva.date = dataHoje
                db.session.commit()
                flash('Data alterada, a reserva ficou pendente para novo pagamento', category='sucesso')
            elif preco_antigo > precototal_novo:
                excesso = preco_antigo - precototal_novo
                reserva.preco_total = f'{precototal_novo} €'
                db.session.commit()
                flash(f'Data alterada,vai ser creditado {excesso} € ', category='sucesso')
        else:
            reserva.preco_total = f'{precototal_novo} €'
            db.session.commit()
            flash('Data alterada', category='sucesso')
    return redirect(url_for('views.get_brand'))


@views.route('/pagamento', methods=['GET', 'POST'])
@login_required
def pagamento():
    id = request.form.get('id')
    reserva = Reservas.query.filter_by(id=id, utilizador_id=current_user.id).first()
    print(reserva)

    carro = reserva.carro_marca
    modelo = reserva.carro_modelo
    precototal = reserva.preco_total
    data_inicial = reserva.data_inicial
    data_final = reserva.data_final
    tipo_pagamento = request.form.get('pagamento')
    if request.method == "POST":
        if tipo_pagamento == "Multibanco":
            flash("foi enviado para o seu email uma entidade e referência para completar o pagamento da reserva",
                  category='sucesso')
            reserva.pagamento = 1
            db.session.commit()
            return redirect(url_for('views.get_brand'))
        elif tipo_pagamento == "Transferência":
            flash("foi enviado para o seu email O IBAN para completar o pagamento da reserva", category='sucesso')
            reserva.pagamento = 1
            db.session.commit()
            return redirect(url_for('views.get_brand'))
        elif tipo_pagamento == "Debito_direto":
            flash("Iremos debitar o valor para a completar o pagamento da reserva", category='sucesso')
            reserva.pagamento = 1
            db.session.commit()
            return redirect(url_for('views.get_brand'))
        else:
            flash("Escolha um metodo de pagamento", category='erro')

    return render_template("pagamento.html", utilizador=current_user,
                           carro=carro, modelo=modelo, precoTotal=precototal, dataInicial=data_inicial,
                           dataFinal=data_final, id=id)
