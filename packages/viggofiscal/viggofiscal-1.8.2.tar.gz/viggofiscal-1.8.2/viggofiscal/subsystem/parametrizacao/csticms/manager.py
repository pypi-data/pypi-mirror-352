import flask

from viggocore.common.subsystem import operation
from viggocore.common.subsystem.pagination import Pagination
from viggocore.common import manager

from viggofiscal.subsystem.parametrizacao.csticms.resource import Csticms
from viggofiscal.subsystem.parametrizacao.regra_fiscal.resource \
    import RegraFiscalModelo


class List(operation.List):

    def get_user(self, session, **kwargs):
        user = None
        if flask.has_request_context():
            token_id = flask.request.headers.get('token')
            if token_id is not None:
                self.token = self.manager.api.tokens().get(id=token_id)
                if self.token is not None:
                    user = self.manager.api.users().get(
                        id=self.token.user_id)
        return user

    def do(self, session, **kwargs):

        self.user = self.get_user(session, **kwargs)

        empresa = None
        crt_empresa = None
        if self.user is not None:
            empresa = self.manager.api.domain_orgs().get(id=self.user.domain_id)
        if empresa is not None:
            crt_empresa = empresa.crt
        csosn_list = ["101", "102", "103", "201", "202", "203", "300",
                      "400", "500", "900"]

        query = session.query(Csticms)

        modelo = kwargs.get('modelo', None)
        if modelo and int(modelo) is RegraFiscalModelo.NFCE.value:
            nfce_cst_csosn_list = ['00', '20', '40', '41', '60',
                                   '102', '103', '300', '400', '500']
            query = query.filter(Csticms.cstcsosn.in_(nfce_cst_csosn_list))

        if crt_empresa.value in [1, 4]:
            query = query.filter(Csticms.cstcsosn.in_(csosn_list))
        elif crt_empresa.value in [2, 3]:
            query = query.filter(Csticms.cstcsosn.not_in(csosn_list))

        query = self.manager.apply_filters(query, Csticms, **kwargs)

        query = query.distinct()

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(Csticms, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(Csticms)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.list = List(self)
