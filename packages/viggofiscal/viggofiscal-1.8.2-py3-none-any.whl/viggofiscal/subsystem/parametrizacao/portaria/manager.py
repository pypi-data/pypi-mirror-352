from viggocore.common import exception
from viggocore.common.subsystem import manager, operation


class Update(operation.Update):

    def pre(self, session, id, **kwargs):
        super().pre(session, id, **kwargs)

        active = kwargs.get('active', True)
        visivel_nota = kwargs.get('visivel_nota', True)

        if (active is False and self.entity.active is True
           and visivel_nota is True):
            raise exception.BadRequest(
                'Não é possível inativar uma portaria padrão para a nota.')
        return True


class Manager(manager.Manager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.update = Update(self)
