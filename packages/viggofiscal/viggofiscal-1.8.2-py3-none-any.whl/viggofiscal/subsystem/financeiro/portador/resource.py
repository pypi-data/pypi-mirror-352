from enum import Enum

import sqlalchemy
from sqlalchemy import orm
from viggocore.common.subsystem import entity
from viggocore.database import db


class PortadorTipo(Enum):
    INTERNO = 'INTERNO'
    EXTERNO = 'EXTERNO'


class Portador(entity.Entity, db.Model):

    attributes = ['domain_id', 'tipo', 'descricao', 'padrao',
                  'codigo_banco', 'nome_banco', 'saldo',
                  'numero_conta', 'digito_conta', 'codigo_agencia',
                  'digito_agencia', 'saldo_inicial', 'ligado_a_terminal']
    attributes += entity.Entity.attributes

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain.id'), nullable=False)

    domain = orm.relationship(
        'Domain', backref=orm.backref('portador_domain'))

    tipo = db.Column(sqlalchemy.Enum(PortadorTipo), nullable=False)
    descricao = db.Column(db.String(100), nullable=False)
    padrao = db.Column(db.Boolean(), nullable=False)
    codigo_banco = db.Column(db.CHAR(3), nullable=True)
    nome_banco = db.Column(db.String(100), nullable=True)
    numero_conta = db.Column(db.String(20), nullable=True)
    digito_conta = db.Column(db.CHAR(1), nullable=True)
    codigo_agencia = db.Column(db.String(20), nullable=True)
    digito_agencia = db.Column(db.CHAR(1), nullable=True)
    saldo = db.Column(db.Numeric(15, 2), nullable=False, server_default='0.0')
    saldo_inicial = db.Column(db.Numeric(15, 2), nullable=False,
                              server_default='0.0')

    terminais = orm.relationship(
        'Terminal', backref=orm.backref('portador_terminal'),
        viewonly=True)

    def __init__(self, id, domain_id, tipo, descricao, padrao,
                 saldo_inicial=0.0, saldo=0.0, codigo_banco=None,
                 nome_banco=None, numero_conta=None, digito_conta=None,
                 codigo_agencia=None, digito_agencia=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_id = domain_id
        self.tipo = tipo
        self.descricao = descricao
        self.padrao = padrao
        self.codigo_banco = codigo_banco
        self.nome_banco = nome_banco
        self.numero_conta = numero_conta
        self.digito_conta = digito_conta
        self.codigo_agencia = codigo_agencia
        self.digito_agencia = digito_agencia
        self.saldo = saldo
        self.saldo_inicial = saldo_inicial

    @property
    def ligado_a_terminal(self):
        if self.terminais is None or len(self.terminais) == 0:
            return False
        return True

    @classmethod
    def collection(cls):
        return 'portadores'
