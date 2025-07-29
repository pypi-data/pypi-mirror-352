from viggocore.common.subsystem import operation
from viggocore.common.subsystem.pagination import Pagination
from viggocore.common import manager, utils

from viggofiscal.subsystem.financeiro.portador.resource import Portador
from viggofiscal.subsystem.parametrizacao.terminal.resource import Terminal


class Create(operation.Create):

    def pre(self, session, **kwargs):
        saldo_inicial = kwargs.get('saldo_inicial', None)
        kwargs['saldo'] = saldo_inicial

        return super().pre(session, **kwargs)


class List(operation.List):

    def do(self, session, **kwargs):
        # flag criada para listar os portadores ligados a terminais ou não
        # True = lista todos, COM ou SEM ligação com aos Terminais
        # False = lista os que NÃO ESTÃO ligados aos Terminais
        tem_terminal = kwargs.pop('tem_terminal', False)

        query = session.query(Portador)\
            .join(Terminal, Terminal.portador_id == Portador.id,
                  isouter=True)

        query = self.manager.apply_filters(query, Portador, **kwargs)
        dict_compare = {"terminal.": Terminal}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)

        if tem_terminal is False:
            query = query.filter(Terminal.id == None)  # noqa
        query = query.distinct()

        # filtro adicionado para evitar puxar o mesmo portador tanto na
        # origem quanto no destino ao realizar tranferência financeira
        if 'portador_id' in kwargs.keys():
            portador_id = kwargs.pop('portador_id', None)
            query = query.filter(Portador.id != portador_id)

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(Portador, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(Portador)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class AjustaSaldoInicial(operation.Update):

    def do(self, session, **kwargs):
        valor = kwargs.pop('valor', None)
        valor = utils.to_decimal(valor)
        kwargs['saldo_inicial'] = self.entity.saldo_inicial + valor
        kwargs['saldo'] = self.entity.saldo + valor

        return super().do(session, **kwargs)


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.create = Create(self)
        self.list = List(self)
        self.ajusta_saldo_inicial = AjustaSaldoInicial(self)
