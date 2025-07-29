
import flask

from viggocore.common import controller, exception, utils


class Controller(controller.CommonController):

    def __init__(self, manager, resource_wrap, collection_wrap):
        super(Controller, self).__init__(
            manager, resource_wrap, collection_wrap)

    def ajuste_saldo(self, id):
        data = flask.request.get_json()

        try:
            if data:
                id = data.pop('id', id)
                entity = self.manager.ajusta_saldo_inicial(id=id, **data)
            else:
                entity = self.manager.ajusta_saldo_inicial(id=id)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response = {self.resource_wrap: entity.to_dict()}

        return flask.Response(response=utils.to_json(response),
                              status=201,
                              mimetype="application/json")
