from viggocore.database import db
from viggocore.common.subsystem import entity


class UficmsSugestao(entity.Entity, db.Model):

    attributes = ['uf_origem', 'uf_destino', 'aliquota']
    attributes += entity.Entity.attributes

    uf_origem = db.Column(db.CHAR(2), nullable=False)
    uf_destino = db.Column(db.CHAR(2), nullable=False)
    aliquota = db.Column(db.Numeric(10), nullable=False)

    def __init__(self, id, uf_origem, uf_destino, aliquota,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.uf_origem = uf_origem
        self.uf_destino = uf_destino
        self.aliquota = aliquota

    @classmethod
    def individual(cls):
        return 'uficms_sugestao'

    @classmethod
    def collection(cls):
        return 'uficms_sugestoes'
