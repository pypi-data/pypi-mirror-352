from viggocore.common.subsystem import operation
from viggocore.common.subsystem.pagination import Pagination
from viggocore.common import manager

from viggofiscal.subsystem.financeiro.centro_resultado.resource \
    import CentroResultado


class List(operation.List):

    def do(self, session, **kwargs):
        centro_resultado_id = kwargs.pop('centro_resultado_id', None)

        query = session.query(CentroResultado)

        query = self.manager.apply_filters(query, CentroResultado, **kwargs)
        if centro_resultado_id is not None:
            query = query.filter(CentroResultado.id != centro_resultado_id)
        query = query.distinct()

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(CentroResultado, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(CentroResultado)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.list = List(self)
