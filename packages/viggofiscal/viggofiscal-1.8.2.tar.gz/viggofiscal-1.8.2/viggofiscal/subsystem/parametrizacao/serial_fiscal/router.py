from viggocore.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return super().routes + [
            {
                'action': 'Get séries fiscais disponíveis',
                'method': 'GET',
                'url': self.collection_url + '/disponiveis',
                'callback': 'get_disponiveis'
            },
        ]
