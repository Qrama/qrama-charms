#!/usr/bin/env python3
# Copyright (C) 2017  Qrama, developed by Tengu-team
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


class SSLTerminationProvides(RelationBase):
    scope = scopes.UNIT

    @hook('{provides:ssl-termination}-relation-{joined}')
    def joined(self):
        for conv in self.conversations():
            conv.remove_state('{relation_name}.removed')
            conv.set_state('{relation_name}.connected')

    @hook('{requires:ssl-termination}-relation-{changed}')
    def changed(self):
        for conv in self.conversations():
            data = {
                'service': conv.get_remote('service'),
                'fqdns': conv.get_remote('fqdns'),
                'private_ips': conv.get_remote('private_ips'),
                'basic_auth': conv.get_remote('basic_auth'),
                'loadbalancing': conv.get_remote('loadbalancing')
            }
            if data['service']:
                conv.set_state('{relation_name}.available')

    @hook('{provides:ssl-termination}-relation-{broken,departed}')
    def broken(self):
        for conv in self.conversations():
            conv.remove_state('{relation_name}.connected')
            conv.remove_state('{relation_name}.available')
            conv.set_state('{relation_name}.removed')

    def get_data(self):
        data = []
        for conv in self.conversations():
            try:
                basic_auth = [
                    {'name': u.split(' | ', 1)[0], 'password': u.split(' | ', 1)[1]}
                    for u in conv.get_remote('basic_auth').split('  ')
                ]
            except (IndexError, AttributeError):
                basic_auth = []
            data.append({
                'service': conv.get_remote('service'),
                'fqdns': conv.get_remote('fqdns').split(' '),
                'private_ips': conv.get_remote('private_ips').split(' '),
                'basic_auth': basic_auth,
                'loadbalancing': conv.get_remote('loadbalancing')
            })
        return data

    def check_status(self):
        self.changed()

