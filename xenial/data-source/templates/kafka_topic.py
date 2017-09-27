#!/usr/bin/env python3
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
# pylint: disable=c0111,c0103,c0301,c0412
import time
from kafka import KafkaProducer
import feedparser

endpoint = "https://www.reddit.com/r/nfl/new/.rss"

def main():
    recent_id = '0'
    while True:
        d = feedparser.parse(endpoint)
        if recent_id == d.entries[0].id:
            time.sleep(600)
        else:
            recent_id = d.entries[0].id
            producer = KafkaProducer(bootstrap_servers='{{host}}:{{port}}')
            for entry in d.entries:
                producer.send('{{topic}}', str.encode(str(entry)))
            time.sleep(600)

if __name__ == '__main__':
    main()
