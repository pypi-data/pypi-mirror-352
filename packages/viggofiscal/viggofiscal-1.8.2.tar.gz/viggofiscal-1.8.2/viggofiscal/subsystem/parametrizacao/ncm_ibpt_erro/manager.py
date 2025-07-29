import flask
from viggocore.common import exception
from viggocore.common.subsystem import manager


class Manager(manager.Manager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)

    def get_erro_existe(self, **kwargs):
        try:
            erros = self.list(**kwargs)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        if len(erros) > 0:
            response = erros[0]
        else:
            response = None

        return response
