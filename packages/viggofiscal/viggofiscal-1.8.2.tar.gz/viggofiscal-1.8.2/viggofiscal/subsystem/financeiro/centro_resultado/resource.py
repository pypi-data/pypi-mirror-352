from enum import Enum

import sqlalchemy
from sqlalchemy import orm
from viggocore.common.subsystem import entity
from viggocore.database import db


class CentroResultado(entity.Entity, db.Model):

    attributes = ['domain_id', 'centro_resultado_id', 'descricao']
    attributes += entity.Entity.attributes

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain.id'), nullable=False)

    centro_resultado_id = db.Column(
        db.CHAR(32), db.ForeignKey('centro_resultado.id'), nullable=True)

    domain = orm.relationship(
        'Domain', backref=orm.backref('centro_resultado_domain'))

    centro_resultado = orm.relationship(
        'CentroResultado', remote_side='CentroResultado.id',
        backref=orm.backref('centro_resultado_centro_resultado'))

    descricao = db.Column(db.String(255), nullable=False)

    def __init__(self, id, domain_id, descricao,
                 centro_resultado_id=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_id = domain_id
        self.descricao = descricao
        self.centro_resultado_id = centro_resultado_id

    def is_stable(self):
        return self.centro_resultado_id != self.id and super().is_stable()

    @classmethod
    def individual(cls):
        return 'centro_resultado'
