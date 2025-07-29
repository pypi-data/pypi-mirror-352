import flask
from viggocore.common import exception, utils
from viggocore.common.subsystem import controller


class Controller(controller.Controller):

    def update(self, id):
        data = flask.request.get_json()
        data.pop('id', None)

        try:
            entity = self.manager.update(id=id, **data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response = {self.resource_wrap: entity.to_dict()}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")
