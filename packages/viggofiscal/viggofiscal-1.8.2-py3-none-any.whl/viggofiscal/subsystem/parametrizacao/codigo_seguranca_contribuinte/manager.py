from viggocore.common.subsystem import operation, manager
from viggocore.common import exception


class Create(operation.Create):

    def pre(self, session, **kwargs):
        csc = kwargs.get('csc', None)
        if csc is None:
            raise exception.BadRequest('csc é obrigatório')
        elif len(csc) < 16 or len(csc) > 36:
            raise exception.BadRequest(
                'csc deve conter entre 16 e 36 caracteres')

        return super().pre(session, **kwargs)


class Update(operation.Update):

    def pre(self, session, **kwargs):
        csc = kwargs.get('csc', None)
        if csc is not None and (len(csc) < 16 or len(csc) > 36):
            raise exception.BadRequest(
                'csc deve conter entre 16 e 36 caracteres')

        return super().pre(session, **kwargs)


class Manager(manager.Manager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.create = Create(self)
        self.update = Update(self)
