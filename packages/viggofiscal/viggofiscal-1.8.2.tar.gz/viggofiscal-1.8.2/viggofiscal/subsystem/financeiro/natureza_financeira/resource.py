from enum import Enum

import sqlalchemy
from sqlalchemy import orm
from viggocore.common.subsystem import entity
from viggocore.database import db


class NaturezaFinanceiraTipo(Enum):
    RECEITA = 'RECEITA'
    DESPESA = 'DESPESA'


class NATUREZA_FINANCEIRA_APROPRIACAO(Enum):
    DEBITO = 'DEBITO'
    CREDITO = 'CREDITO'


class NaturezaFinanceira(entity.Entity, db.Model):

    attributes = ['domain_id', 'natureza_financeira_id', 'descricao',
                  'tipo', 'periodicidade']
    attributes += entity.Entity.attributes

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain.id'), nullable=False)
    natureza_financeira_id = db.Column(
        db.CHAR(32), db.ForeignKey('natureza_financeira.id'), nullable=True)

    domain = orm.relationship(
        'Domain', backref=orm.backref('natureza_financeira_domain'))
    natureza_financeira = orm.relationship(
        'NaturezaFinanceira', remote_side='NaturezaFinanceira.id',
        backref=orm.backref('natureza_financeira_natureza_financeira'))

    descricao = db.Column(db.String(255), nullable=False)
    tipo = db.Column(sqlalchemy.Enum(NaturezaFinanceiraTipo), nullable=False)
    periodicidade = db.Column(db.Boolean(), nullable=False)

    def __init__(self, id, domain_id, descricao, tipo, periodicidade,
                 natureza_financeira_id=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_id = domain_id
        self.descricao = descricao
        self.tipo = tipo
        self.periodicidade = periodicidade
        self.natureza_financeira_id = natureza_financeira_id

    def is_stable(self):
        return self.natureza_financeira_id != self.id and super().is_stable()

    @classmethod
    def individual(cls):
        return 'natureza_financeira'
