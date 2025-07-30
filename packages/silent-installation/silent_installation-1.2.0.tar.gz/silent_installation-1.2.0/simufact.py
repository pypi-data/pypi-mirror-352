import collections

Prod = collections.namedtuple('Prod', ['name', 'alias', 'processName'])


class _Simufact:
    PROD_NAMES = ('forming', 'welding', 'additive')
    PROC_NAMES = ('sfForming.exe', 'simufact.welding.exe', 'simufact additive.exe')

    def __init__(self):
        self._prods = [Prod(prod_name, 'am' if prod_name == 'additive' else prod_name, proc_name) for
                       prod_name, proc_name in zip(self.PROD_NAMES, self.PROC_NAMES)]

    def __getitem__(self, name):
        for prod in self._prods:
            if name == prod.name:
                return prod
        raise ValueError(f'{name} is not valid, only {", ".join(self.PROD_NAMES)} are allowed.')


simufactIns = _Simufact()
