import flask
from viggocore.common import exception, utils, controller


class Controller(controller.CommonController):

    def __init__(self, manager, resource_wrap, collection_wrap):
        super(Controller, self).__init__(
            manager, resource_wrap, collection_wrap)
