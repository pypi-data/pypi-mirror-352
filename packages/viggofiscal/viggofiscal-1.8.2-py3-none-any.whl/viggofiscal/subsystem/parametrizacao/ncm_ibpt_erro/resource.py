from sqlalchemy.sql.schema import UniqueConstraint

from viggocore.database import db
from viggocore.common.subsystem import entity


class NcmIbptErro(entity.Entity, db.Model):

    attributes = ['ncm', 'uf', 'chave', 'versao', 'tipo',
                  'filename', 'msg_erro', 'erro_em', 'extipi', 'corrigido']
    attributes += entity.Entity.attributes

    ncm = db.Column(db.String(20), nullable=False)
    uf = db.Column(db.CHAR(2), nullable=False)
    chave = db.Column(db.String(100), nullable=False)
    versao = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.Numeric(3), nullable=False)
    filename = db.Column(db.String(2000), nullable=False)
    msg_erro = db.Column(db.String(2000), nullable=False)
    erro_em = db.Column(db.DateTime(), nullable=False)
    extipi = db.Column(db.Numeric(), nullable=True)
    corrigido = db.Column(db.Boolean(), nullable=False,
                          default=False, server_default='false')

    __table_args__ = (
        UniqueConstraint(
            'ncm', 'uf', 'chave', 'versao', 'extipi', 'tipo',
            name='ncm_ibpt_erro_ncm_uf_chave_versao_extipi_tipo_uk'),)

    def __init__(self, id, ncm, uf, chave, versao, tipo, filename, msg_erro,
                 erro_em, extipi=None, corrigido=False,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.ncm = ncm
        self.uf = uf
        self.chave = chave
        self.versao = versao
        self.tipo = tipo
        self.filename = filename
        self.msg_erro = msg_erro
        self.erro_em = erro_em
        self.extipi = extipi
        self.corrigido = corrigido

    @classmethod
    def individual(cls):
        return 'ncm_ibpt_erro'
