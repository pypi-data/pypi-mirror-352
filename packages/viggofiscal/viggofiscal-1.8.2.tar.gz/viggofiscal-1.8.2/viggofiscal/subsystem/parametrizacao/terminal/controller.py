import flask
from viggocore.common import exception, utils, controller


class Controller(controller.CommonController):

    def __init__(self, manager, resource_wrap, collection_wrap):
        super(Controller, self).__init__(
            manager, resource_wrap, collection_wrap)

    def analisar(self):
        data = flask.request.get_json()
        try:
            tuplas = self.manager.analisar(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        collection = []
        if len(tuplas) > 0:
            permissao = False
        else:
            permissao = True
        for tupla in tuplas:
            tupla_dict = {
                'user_name': tupla[0],
                'terminal_descricao': tupla[1]}
            collection.append(tupla_dict)

        response = {'permissao': permissao, 'operadores_em_uso': collection}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")
