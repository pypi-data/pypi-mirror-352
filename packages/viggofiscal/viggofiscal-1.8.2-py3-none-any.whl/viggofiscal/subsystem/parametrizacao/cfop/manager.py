from viggocore.common.subsystem import operation
from viggocore.common.subsystem.pagination import Pagination
from viggocore.common import manager

from viggofiscal.subsystem.parametrizacao.cfop.resource import Cfop
from viggofiscal.subsystem.parametrizacao.regra_fiscal.resource \
    import RegraFiscalModelo


class List(operation.List):

    def do(self, session, **kwargs):

        query = session.query(Cfop)

        modelo = kwargs.get('modelo', None)
        if modelo and int(modelo) is RegraFiscalModelo.NFCE.value:
            nfce_cfop_list = ['5101', '5102', '5103', '5104', '5115',
                              '5405', '5656', '5667']
            query = query.filter(Cfop.cfop.in_(nfce_cfop_list))

        query = self.manager.apply_filters(query, Cfop, **kwargs)
        query = query.distinct()

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(Cfop, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(Cfop)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.list = List(self)
