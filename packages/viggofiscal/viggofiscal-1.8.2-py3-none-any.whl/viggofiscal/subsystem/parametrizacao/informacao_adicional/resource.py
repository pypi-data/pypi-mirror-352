from viggocore.database import db
from viggocore.common.subsystem import entity


class InformacaoAdicional(entity.Entity, db.Model):

    attributes = ['descricao']
    attributes += entity.Entity.attributes

    descricao = db.Column(db.String(100), nullable=False)

    def __init__(self, id, descricao,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.descricao = descricao

    @classmethod
    def individual(cls):
        return 'informacao_adicional'

    @classmethod
    def collection(cls):
        return 'informacao_adicionais'
