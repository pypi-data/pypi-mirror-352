from viggocore.common import exception
from viggocore.common.subsystem import manager, operation


class LimparPorSigla(operation.Delete):

    def pre(self, session, **kwargs):
        self.sigla = kwargs.pop('sigla', None)
        if self.sigla is None:
            raise exception.BadRequest('A sigla é obrigatória.')
        return True

    def do(self, session, **kwargs):
        query = """
            DELETE FROM ncm_ibpt AS ni
            WHERE ni.uf = \'{sigla}\';

            DELETE FROM ncm_ibpt_erro AS nie
            WHERE nie.uf = \'{sigla}\';
        """
        query = query.format(sigla=self.sigla)
        session.execute(query)
        return True


class Manager(manager.Manager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.limpar_por_sigla = LimparPorSigla(self)
