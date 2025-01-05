import os
import plyvel
import json
import sys
import time
import chimera_app.context as context


PREFIX='uc-chimera_'

class SteamCollections():

    def __init__(self, userid):
        self.collections = None
        self.db = None
        self.userid = userid
        self.url = '_https://steamloopback.host\x00\x01U{userid}-cloud-storage-namespace-1'.format(userid=self.userid).encode('utf-8')


    def open(self):
        if self.collections:
            return

        try:
            dbdir = context.DATA_HOME + '/Steam/config/htmlcache/Local Storage/leveldb'
            if not os.path.isdir(dbdir):
                self.collections = None
                return

            self.db = plyvel.DB(dbdir)

            value = self.db.get(self.url)
            if value:
                self.collections = self.__decode(value)
            else:
                self.db.close()
                self.db = None
        except Exception as e:
            print('failed to load steam collections:', e)
            self.collections = None


    def __decode(self, data):
        data = json.loads(data[1:])
        for e in data:
            if 'value' in e[1]:
                e[1]['value'] = json.loads(e[1]['value'])

        return data


    def add(self, collectionName, gameIDs):
        if not self.collections:
            return

        found = False
        for col in self.collections:
            if not col[0].startswith('user-collections.') or not 'value' in col[1]:
                continue

            if col[1]['value']['name'] == collectionName:
                found = True
                col[1]['value']['added'] = list(set(gameIDs) | set(col[1]['value']['added']))

        if found:
            return

        # collection was not found, create a new one
        new_collection = {
            'key' : 'user-collections.' + PREFIX + collectionName,
            'timestamp' : int(time.time()),
            'value' : { 'id' : PREFIX + collectionName, 'name' : collectionName, 'added' : gameIDs, 'removed' : [] },
            'conflictResolutionMethod' : 'custom',
            'strMethodId': 'union-collections'
        }

        self.collections.append(['user-collections.' + PREFIX + collectionName, new_collection])


    def remove(self, collectionName, gameIDs):
        if not self.collections:
            return

        for col in self.collections:
            if not col[0].startswith('user-collections.') or not 'value' in col[1]:
                continue

            if col[1]['value']['name'] == collectionName:
                col[1]['value']['added'] = list(set(col[1]['value']['added']) - set(gameIDs))


    def save(self):
        if not self.collections or not self.db:
            return

        out = self.__encode()
        self.db.put(self.url, out, sync=True)
        self.db.close()
        self.db = None


    def __encode(self):
        if not self.collections:
            return

        for col in self.collections:
            if 'value' in col[1]:
                col[1]['value'] = json.dumps(col[1]['value'])

        out = json.dumps(self.collections)
        out = '\x01{}'.format(out).encode('utf-8')

        self.collections = None
        return out
