from pywikibot import family

class Family(family.Family):
    name = 'myacg'
    langs = {
        'myacg': 'xiplus.ddns.net',
    }

    def path(self, code):
        return '/ACG/index.php'

    def scriptpath(self, code):
        return '/ACG/w'

    def protocol(self, code):
        return 'HTTPS'
