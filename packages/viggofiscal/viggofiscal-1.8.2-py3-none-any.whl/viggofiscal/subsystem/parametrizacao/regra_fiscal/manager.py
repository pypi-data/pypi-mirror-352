from viggocore.common import manager
from viggocore.common.subsystem import operation
from viggocore.common.subsystem.pagination import Pagination

from viggofiscal.subsystem.parametrizacao.regra_fiscal.resource import \
    RegraFiscal, RegraFiscalModelo


class List(operation.List):

    def do(self, session, **kwargs):
        # pega o campo status como uma lista de status separado por vírgula
        modelo = kwargs.pop('modelo', '')

        query = session.query(RegraFiscal)
        query = self.manager.apply_filters(query, RegraFiscal, **kwargs)

        # aplica a filtragem pela lista de status
        if len(modelo) > 0:
            modelo_list = str(modelo).split(',')
            modelo_list_enum = [RegraFiscalModelo[ml] for ml in modelo_list]
            query = query.filter(RegraFiscal.modelo.in_(modelo_list_enum))

        dict_compare = {}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(RegraFiscal, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(RegraFiscal)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.list = List(self)
