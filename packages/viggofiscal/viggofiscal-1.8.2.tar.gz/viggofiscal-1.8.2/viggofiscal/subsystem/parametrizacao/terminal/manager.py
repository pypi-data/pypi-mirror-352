from sqlalchemy import and_
from viggocore.common import manager
from viggocore.common.subsystem import operation
from viggocore.subsystem.user.resource import User
from viggofiscal.subsystem.parametrizacao.terminal.resource import (
    Terminal, TerminalOperador)
from viggocore.common.subsystem.pagination import Pagination


class Create(operation.Create):

    def pre(self, **kwargs):
        kwargs['portador_id'] = None
        return super().pre(**kwargs)

    def do(self, session, **kwargs):
        # cria um portador e vincula ao terminal
        descricao = kwargs.get('descricao', None)
        portador_data = {
            'descricao': descricao,
            'domain_id': self.entity.domain_id,
            'tipo': 'INTERNO',
            'padrao': False}
        portador = self.manager.api.portadores().create(
            **portador_data)
        self.entity.portador_id = portador.id

        super().do(session=session, **kwargs)

        self.manager.remover_users_de_outros_terminais(
            terminal=self.entity, session=session)

        return self.entity


class Update(operation.Update):

    def do(self, session, **kwargs):
        self.entity = super().do(session=session, **kwargs)

        self.manager.remover_users_de_outros_terminais(
            terminal=self.entity, session=session)

        return self.entity


class Analisar(operation.Create):

    def pre(self, session, **kwargs):
        return True

    def do(self, session, **kwargs):
        terminal_id = kwargs.get('id', '')
        operadores = kwargs.get('operadores', [])
        operadores_em_uso = []
        if len(operadores) > 0:
            operadores_em_uso = self.manager.get_operadores_em_uso(
                session, terminal_id, operadores)
        return operadores_em_uso


class List(operation.List):

    def do(self, session, **kwargs):
        query = session.query(Terminal). \
            join(TerminalOperador, Terminal.id == TerminalOperador.terminal_id,
                 isouter=True)
        query = self.manager.apply_filters(query, Terminal, **kwargs)

        dict_compare = {'terminal_operador.': TerminalOperador}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(Terminal, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(Terminal)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.create = Create(self)
        self.update = Update(self)
        self.analisar = Analisar(self)
        self.list = List(self)

    def remover_users_de_outros_terminais(self, terminal, session):
        if len(terminal.operadores) > 0:
            user_ids = terminal.get_user_id_dos_operadores()

            query = """
                DELETE FROM terminal_operador
                WHERE terminal_id <> \'{terminal_id}\' AND
                    user_id in {user_ids};
            """
            query = query.format(
                terminal_id=terminal.id,
                user_ids=str(user_ids).replace('[', '(').replace(']', ')'))
            session.execute(query)

    def get_operadores_em_uso(self, session, terminal_id, operadores):
        user_ids = [op.get('user_id', None) for op in operadores]
        query = session.query(User.name, Terminal.descricao). \
            join(TerminalOperador, TerminalOperador.user_id == User.id,
                 isouter=True). \
            join(Terminal, Terminal.id == TerminalOperador.terminal_id,
                 isouter=True). \
            filter(and_(TerminalOperador.terminal_id != terminal_id,
                        User.id.in_(user_ids)))
        query = query.distinct()
        result = query.all()

        return result
