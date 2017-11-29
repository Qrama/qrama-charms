# !/usr/bin/env python3
# Copyright (C) 2017  Qrama
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
from charmhelpers.core import hookenv
from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes


class ActiveMQProvides(RelationBase):
    scope = scopes.GLOBAL

    @hook('{provides:activemq-sub}-relation-{joined,changed}')
    def changed(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.removed')
        conv.set_state('{relation_name}.available')

    @hook('{provides:activemq-sub}-relation-{broken,departed}')
    def broken(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.available')
        conv.set_state('{relation_name}.removed')

    def configure(self, port, version):
        conv = self.conversation()
        relation_info = {
            'port': port,
            'version': version
        }
        conv.set_remote(**relation_info)
