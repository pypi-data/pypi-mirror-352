from viggocore.common import manager
from viggocore.common.subsystem import operation
from viggocore.common.subsystem.pagination import Pagination

from viggofiscal.subsystem.parametrizacao.uficms_sugestao.resource import \
    UficmsSugestao


class List(operation.List):

    def do(self, session, **kwargs):
        query = session.query(UficmsSugestao)
        query = self.manager.apply_filters(query, UficmsSugestao, **kwargs)

        dict_compare = {}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(UficmsSugestao, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(UficmsSugestao)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.list = List(self)
