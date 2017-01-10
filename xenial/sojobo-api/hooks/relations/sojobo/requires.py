# !/usr/bin/env python3
# Copyright (C) 2016  Qrama
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# pylint: disable=c0111,c0301,c0325, r0903,w0406

from charms.reactive import hook, RelationBase, scopes


class SojoboRequires(RelationBase):
    scope = scopes.UNIT

    @hook('{requires:sojobo}-relation-{joined,changed}')
    def changed(self):
        conv = self.conversation()
        if conv.get_remote('port') and conv.get_remote('api_key'):
            conv.set_state('{relation_name}.available')

    @hook('{requires:sojobo}-relation-{departed,broken}')
    def broken(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.available')

    def services(self):
        services = {}
        for conv in self.conversations():
            service_name = conv.scope.split('/')[0]
            service = services.setdefault(service_name, {
                'service_name': service_name,
                'hosts': [],
            })
            host = conv.get_remote('hostname')
            port = conv.get_remote('port')
            api_key = conv.get_remote('api_key')
            if host and port and api_key:
                service['hosts'].append({
                    'hostname': host,
                    'port': port,
                    'api_key': api_key
                })
        return [s for s in services.values() if s['hosts']]
