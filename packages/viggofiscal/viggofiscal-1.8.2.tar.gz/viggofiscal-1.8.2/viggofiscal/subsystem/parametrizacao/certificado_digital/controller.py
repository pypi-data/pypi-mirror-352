import flask
import json

from viggocore.common import exception, utils
from viggocore.common.subsystem import controller


class Controller(controller.Controller):

    MIMETYPE_JSON = 'application/json'

    def __init__(self, manager, resource_wrap, collection_wrap):
        super().__init__(manager, resource_wrap, collection_wrap)

    def create(self):
        try:
            values = flask.request.values.get('body', None)
            file = flask.request.files.get('file', None)

            file_types = ['pfx', 'p12']
            if not file:
                raise exception.BadRequest(
                    'ERRO! Arquivo não enviado na requisição')

            if file.filename.split('.')[-1] not in file_types:
                raise exception.BadRequest(
                    'O file não é de um tipo suportado (pfx ou p12).')

            data = json.loads(values)
            result = self.manager.create(file=file, **data)
            response = {self.resource_wrap: result.to_dict()}
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=utils.to_json(response),
                              status=201,
                              mimetype=self.MIMETYPE_JSON)

    def update(self, id):
        try:
            values = flask.request.values.get('body', None)
            file = flask.request.files.get('file', None)

            file_types = ['pfx', 'p12']
            if not file:
                raise exception.BadRequest(
                    'ERRO! Arquivo não enviado na requisição')

            if file.filename.split('.')[-1] not in file_types:
                raise exception.BadRequest(
                    'O file não é de um tipo suportado (pfx ou p12).')

            data = json.loads(values)
            id = data.pop('id', None)
            if id is None:
                raise exception.BadRequest(
                    'É obrigatório passar o id no campo body do form-data.')
            result = self.manager.update(id=id, file=file, **data)
            response = {self.resource_wrap: result.to_dict()}
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=utils.to_json(response),
                              status=201,
                              mimetype=self.MIMETYPE_JSON)
