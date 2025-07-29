from viggocore.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return super().routes + [
            {
                'action': 'Verifica se tem erros não resolvidos',
                'method': 'GET',
                'url': self.collection_url + '/nao_resolvidos',
                'callback': 'get_nao_resolvidos'
            }
        ]
