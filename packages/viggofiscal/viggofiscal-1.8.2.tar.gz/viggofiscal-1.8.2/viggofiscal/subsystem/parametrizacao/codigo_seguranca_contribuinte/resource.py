from sqlalchemy import UniqueConstraint, orm

from viggocore.database import db
from viggocore.common.subsystem import entity


class CodigoSegurancaContribuinte(entity.Entity, db.Model):

    attributes = ['domain_org_id', 'id_csc', 'csc']
    attributes += entity.Entity.attributes

    domain_org_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain_org.id'), nullable=False)
    id_csc = db.Column(db.Numeric(10), nullable=False)
    csc = db.Column(db.String(36), nullable=False)

    domain_org = orm.relationship(
        'DomainOrg',
        backref=orm.backref('codigo_seguranca_contribuinte_domain_org'))

    __table_args__ = (
        UniqueConstraint(
            'domain_org_id', 'id_csc', 'csc',
            name='codigo_seguranca_contribuinte_domain_org_id_csc_csc_uk'),)

    def __init__(self, id, domain_org_id, id_csc, csc,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_org_id = domain_org_id
        self.id_csc = id_csc
        self.csc = csc

    @classmethod
    def individual(cls):
        return 'codigo_seguranca_contribuinte'
