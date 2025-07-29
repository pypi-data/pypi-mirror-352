
from viggocore.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return super().routes + [
            {
                'action': 'Ajustar saldo inicial do portador',
                'method': 'PUT',
                'url': self.resource_url + '/ajuste_saldo',
                'callback': 'ajuste_saldo'
            }
        ]
