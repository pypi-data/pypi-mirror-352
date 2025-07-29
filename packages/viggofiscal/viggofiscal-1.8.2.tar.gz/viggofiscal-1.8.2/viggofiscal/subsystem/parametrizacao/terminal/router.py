from viggocore.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return super().routes + [
            {
                'action': 'Analisar a criação ou atualiza',
                'method': 'POST',
                'url': self.collection_url + '/analisar',
                'callback': 'analisar'
            },
        ]
