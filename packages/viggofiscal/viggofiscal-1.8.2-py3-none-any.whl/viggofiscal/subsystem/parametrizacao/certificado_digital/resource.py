import uuid
from sqlalchemy import orm

from viggocore.database import db
from viggocore.common.subsystem import entity


class CertificadoDigital(entity.Entity, db.Model):

    attributes = ['domain_org_id']
    attributes += entity.Entity.attributes

    domain_org_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain_org.id'), nullable=False,
        unique=True)
    certificado = db.Column(db.Text, nullable=False)
    senha = db.Column(db.Text, nullable=False, default=uuid.uuid4().hex)

    domain_org = orm.relationship(
        'DomainOrg', backref=orm.backref('certificado_digital_domain_org'))

    def __init__(self, id, domain_org_id, certificado, senha,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_org_id = domain_org_id
        self.certificado = certificado
        self.senha = senha

    @classmethod
    def individual(cls):
        return 'certificado_digital'
