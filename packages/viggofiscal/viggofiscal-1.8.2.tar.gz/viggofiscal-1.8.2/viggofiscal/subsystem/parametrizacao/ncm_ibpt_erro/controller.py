import flask
from viggocore.common import exception, utils
from viggocore.common.subsystem import controller


class Controller(controller.Controller):

    def get_nao_resolvidos(self):
        filters = self._filters_parse()
        filters = self._filters_cleanup(filters)

        try:
            filters = self._parse_list_options(filters)
            filters = self._clean_filters(**filters)
            count = self.manager.count(**filters)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response = {'qtd_erros_para_resolver': count}

        return flask.Response(response=utils.to_json(response),
                              status=201,
                              mimetype="application/json")
