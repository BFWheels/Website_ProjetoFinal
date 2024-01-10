from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# base de dados de notas (futuramente para a bd de carros)


class Reservas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())  # Usar registo temporal para as reservas dos carros
    utilizador_id = db.Column(db.Integer, db.ForeignKey('utilizador.id'))  # usar este codigo para definir reservas

    #  Base de dados do utilizador (adicionar data de nascimento)


class Utilizador(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    nome = db.Column(db.String(150))
    apelido = db.Column(db.String(150))
    dataNascimento = db.Column(db.DateTime(timezone=False))
    password = db.Column(db.String(150))
    reservas = db.relationship('Reservas')
