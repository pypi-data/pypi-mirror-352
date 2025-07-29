from sqlalchemy import and_, or_
from viggocore.common import exception, manager
from viggocore.common.subsystem import operation
from viggocore.common.subsystem.pagination import Pagination

from viggofiscal.subsystem.parametrizacao.serial_fiscal.resource import \
    SerieFiscal
from viggofiscal.subsystem.parametrizacao.terminal.resource import Terminal


class Create(operation.Create):

    def pre(self, session, **kwargs):
        serie = int(kwargs.get('serie', '9999'))
        if serie < 0 or serie > 999:
            raise exception.BadRequest(
                'A serie tem que ser um valor entre 0 e 999.')
        return super().pre(session, **kwargs)


class Update(operation.Update):

    def do(self, session, **kwargs):
        kwargs.pop('ambiente', None)
        kwargs.pop('serie', None)
        kwargs.pop('modelo', None)
        return super().do(session=session, **kwargs)


class List(operation.List):

    def do(self, session, **kwargs):
        query = session.query(SerieFiscal)
        query = self.manager.apply_filters(query, SerieFiscal, **kwargs)

        dict_compare = {}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(SerieFiscal, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(SerieFiscal)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class GetNextUltimoDoc(operation.Operation):
    def pre(self, session, id, **kwargs):
        serie_fiscal = self.manager.get(id=id)
        if not serie_fiscal:
            raise exception.NotFound('ERROR! serie_fiscal not found')
        self.serie_fiscal_id = serie_fiscal.id

        return True

    def do(self, session, **kwargs):
        next_ultimo_doc = self.driver.get_next_ultimo_doc(
            session, self.serie_fiscal_id)

        if next_ultimo_doc is None:
            raise exception.ViggoCoreException(
                'Não foi possível retornar o próximo ultimo_doc ' +
                'da serie_fiscal')

        return next_ultimo_doc


class GetDisponiveis(operation.List):

    def do(self, session, **kwargs):
        serie_fiscal_id = kwargs.pop('serie_fiscal_id', None)

        query = session.query(SerieFiscal). \
            join(Terminal, Terminal.serie_fiscal_id == SerieFiscal.id,
                 isouter=True). \
            filter(and_(or_(Terminal.serie_fiscal_id == None,  # noqa: E711
                            SerieFiscal.id == serie_fiscal_id),
                        SerieFiscal.modelo == 'NFCE',
                        SerieFiscal.status == 'ATIVO'))
        query = self.manager.apply_filters(query, SerieFiscal, **kwargs)

        dict_compare = {"terminal.": Terminal}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)
        query = query.distinct()

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(SerieFiscal, **kwargs)
        if pagination.order_by is not None:
            pagination.order_by = 'serie_fiscal.serie'
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.create = Create(self)
        self.update = Update(self)
        self.list = List(self)
        self.get_next_ultimo_doc = GetNextUltimoDoc(self)
        self.get_disponiveis = GetDisponiveis(self)
