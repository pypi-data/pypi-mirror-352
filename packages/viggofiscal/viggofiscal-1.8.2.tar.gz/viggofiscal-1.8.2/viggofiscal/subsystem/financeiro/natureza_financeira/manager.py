from viggocore.common.subsystem import operation
from viggocore.common.subsystem.pagination import Pagination
from viggocore.common import manager
from sqlalchemy.orm import aliased

from viggofiscal.subsystem.financeiro.natureza_financeira.resource \
    import NaturezaFinanceira


class List(operation.List):

    def do(self, session, **kwargs):
        NaturezaFinanceiraPai = aliased(NaturezaFinanceira)
        not_id = kwargs.pop('not_id', None)

        query = session.query(NaturezaFinanceira)\
            .join(NaturezaFinanceiraPai,
                  NaturezaFinanceiraPai.id ==
                  NaturezaFinanceira.natureza_financeira_id,
                  isouter=True)

        query = self.manager.apply_filters(query, NaturezaFinanceira, **kwargs)
        dict_compare = {'natureza_financeira_pai.': NaturezaFinanceiraPai}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)

        # filtro usado para filtrar
        if not_id is not None:
            query = query.filter(NaturezaFinanceira.id != not_id)
        query = query.distinct()

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(NaturezaFinanceira, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(NaturezaFinanceira)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.list = List(self)
