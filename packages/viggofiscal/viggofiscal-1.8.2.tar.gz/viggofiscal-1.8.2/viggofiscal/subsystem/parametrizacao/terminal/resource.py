from sqlalchemy import UniqueConstraint, orm

from viggocore.database import db
from viggocore.common.subsystem import entity


class Terminal(entity.Entity, db.Model):

    attributes = ['domain_id', 'serie_fiscal_id', 'portador_id',
                  'descricao']
    attributes += entity.Entity.attributes

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain.id'), nullable=False)
    serie_fiscal_id = db.Column(
        db.CHAR(32), db.ForeignKey('serie_fiscal.id'), nullable=True)
    portador_id = db.Column(
        db.CHAR(32), db.ForeignKey('portador.id'), nullable=False)
    descricao = db.Column(db.String(80), nullable=False)

    domain = orm.relationship(
        'Domain', backref=orm.backref('terminal_domain'))
    serie_fiscal = orm.relationship(
        'SerieFiscal', backref=orm.backref('terminal_serie_fiscal'))
    portador = orm.relationship(
        'Portador', backref=orm.backref('terminal_portador'),
        viewonly=True)

    operadores = orm.relationship(
        "TerminalOperador",
        backref=orm.backref('terminal_terminal_operaador'),
        cascade='delete,delete-orphan,save-update')

    __table_args__ = (
        UniqueConstraint(
            'domain_id', 'serie_fiscal_id',
            name='terminal_domain_id_serie_fiscal_id_uk'),
        UniqueConstraint(
            'domain_id', 'descricao',
            name='terminal_domain_id_descricao_uk'),)

    def __init__(self, id, domain_id, portador_id,
                 descricao, serie_fiscal_id=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_id = domain_id
        self.serie_fiscal_id = serie_fiscal_id
        self.portador_id = portador_id
        self.descricao = descricao

    def get_user_id_dos_operadores(self):
        user_ids = []
        for operador in self.operadores:
            user_ids.append(operador.user_id)
        return user_ids

    @classmethod
    def individual(cls):
        return 'terminal'

    @classmethod
    def collection(cls):
        return 'terminais'

    @classmethod
    def embedded(cls):
        return ['operadores']


class TerminalOperador(entity.Entity, db.Model):

    attributes = ['id', 'user_id']
    attributes += entity.Entity.attributes

    terminal_id = db.Column(
        db.CHAR(32), db.ForeignKey('terminal.id'), nullable=False)
    user_id = db.Column(
        db.CHAR(32), db.ForeignKey('user.id'), nullable=False)

    user = orm.relationship(
        'User', backref=orm.backref('terminal_operador_user'))

    def __init__(self, id, terminal_id, user_id,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.terminal_id = terminal_id
        self.user_id = user_id
