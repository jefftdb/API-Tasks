from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Protocolo(db.Model):
    __tablename__ = 'protocolo'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255))
    nome = db.Column(db.String(255))
    cpf = db.Column(db.String(14))
    email = db.Column(db.String(254))
    telefone = db.Column(db.String(20))
    descricao = db.Column(db.Text)
    estado = db.Column(db.String(20), default='Analizando')
    cor = db.Column(db.String(20),default='rgb(248, 51, 84)')
    latitude = db.Column(db.Numeric(10,7))
    longitude = db.Column(db.Numeric(10,7))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    imagens = db.relationship('Imagem', backref='protocolo', cascade="all, delete-orphan")

class Imagem(db.Model):
    __tablename__ = 'imagem'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    protocolo_id = db.Column(db.Integer, db.ForeignKey('protocolo.id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
