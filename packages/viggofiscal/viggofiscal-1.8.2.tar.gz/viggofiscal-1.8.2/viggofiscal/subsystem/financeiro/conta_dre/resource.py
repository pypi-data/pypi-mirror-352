from enum import Enum

import sqlalchemy
from sqlalchemy import orm
from viggocore.common.subsystem import entity
from viggocore.database import db


class CONTA_DRE_CLASSIFICACAO(Enum):
    ATIVO = 'ATIVO'
    PASSIVO = 'PASSIVO'
    RECEITA = 'RECEITA'
    DESPESA = 'DESPESA'
    RESULTADO = 'RESULTADO'
    CUSTO = 'CUSTO'


class ContaDre(entity.Entity, db.Model):

    attributes = ['domain_id', 'descricao', 'classificacao', 'codigo_reduzido']
    attributes += entity.Entity.attributes

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain.id'), nullable=False)

    domain = orm.relationship(
        'Domain', backref=orm.backref('conta_dre_domain'))

    descricao = db.Column(db.String(255), nullable=False)
    classificacao = db.Column(sqlalchemy.Enum(CONTA_DRE_CLASSIFICACAO),
                              nullable=False)
    codigo_reduzido = db.Column(db.String(50), nullable=True)

    def __init__(self, id, domain_id, descricao, classificacao,
                 codigo_reduzido=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_id = domain_id
        self.descricao = descricao
        self.classificacao = classificacao
        self.codigo_reduzido = codigo_reduzido

    @classmethod
    def individual(cls):
        return 'conta_dre'
