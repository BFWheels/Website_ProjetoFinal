from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# base de dados de notas (futuramente para a bd de carros)


class Reservas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carro_marca = db.Column(db.String(150), db.ForeignKey('carro.marca'))
    carro_modelo = db.Column(db.String(150), db.ForeignKey('modelo.modelo'))
    carro_matricula = db.Column(db.String(150), db.ForeignKey('modelo.matricula'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())  # usar registo temporal as reservas dos carros
    data_inicial = db.Column(db.Date())
    data_final = db.Column(db.Date())
    preco_total = db.Column(db.Integer)
    utilizador_id = db.Column(db.Integer, db.ForeignKey('utilizador.id'))  # usar este codigo para definir reservas


class Utilizador(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    nome = db.Column(db.String(150))
    apelido = db.Column(db.String(150))
    datanascimento = db.Column(db.Date())
    password = db.Column(db.String(150))
    reservas = db.relationship('Reservas')


class Carro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(150), unique=True)
    numero_viaturas = db.Column(db.Integer)


class Modelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca_carro = db.Column(db.String(150), db.ForeignKey('carro.marca'))
    modelo = db.Column(db.String(150))
    lugares = db.Column(db.Integer, default=5)
    combustivel = db.Column(db.String(150))
    matricula = db.Column(db.String(150), unique=True)
    data_proxima_revisao = db.Column(db.Date())
    data_ultima_revisao = db.Column(db.Date())
    data_ultima_legalizacao = db.Column(db.Date())
    preco_dia = db.Column(db.Integer)
    disponivel = db.Column(db.Integer, default=1)