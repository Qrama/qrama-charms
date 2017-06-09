from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes
from charms.reactive import is_state


class InfluxdbClient(RelationBase):
    scope = scopes.GLOBAL
    auto_accessors = ['hostname', 'port', 'user', 'password']

    @hook('{requires:influxdb-api}-relation-{joined,changed}')
    def changed(self):
        #self.remove_state('{relation_name}.broken')
        self.set_state('{relation_name}.connected')
        data = {
            'hostname': self.hostname(),
            'port': self.port(),
            'user': self.user(),
            'password': self.password(),
        }
        if all(data.values()):
            self.set_state('{relation_name}.available')

    @hook('{requires:influxdb-api}-relation-{broken,departed}')
    def broken(self):
        self.remove_state('{relation_name}.available')
        #self.set_state('{relation_name}.broken')
