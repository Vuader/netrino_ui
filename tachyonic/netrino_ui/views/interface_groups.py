from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import json

from tachyonic import app
from tachyonic.neutrino import constants as const
from tachyonic.ui import menu
from ..controllers import createIGroup, viewIGroup, editIGroup, deleteIGroup, getAPI


log = logging.getLogger(__name__)

menu.admin.add('/Infrastructure/Network/Interface Groups',
               '/infrastructure/network/igroups', 'network:admin')


@app.resources()
class InterfaceGroups(object):

    def __init__(self):
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroups',
                       self.get, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroups/create',
                       self.create, 'network:admin')
        app.router.add(const.HTTP_POST, '/infrastructure/network/igroups/create',
                       self.create, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroups/view',
                       self.getjson, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroups/view/{id}',
                       self.get, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroups/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(const.HTTP_POST, '/infrastructure/network/igroups/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroups/delete/{id}',
                       self.delete, 'network:admin')

    def create(self, req, resp):
        createIGroup(req, resp)

    def get(self, req, resp, id=None):
        return viewIGroup(req, resp, igid=id)

    def getjson(self, req, resp, id=None):
        api = getAPI(req)
        response_headers, result = api.execute(
            const.HTTP_GET, "/infrastructure/network/igroups?view=select2")
        return json.dumps(result, indent=4)

    def edit(self, req, resp, id):
        editIGroup(req, resp, igid=id)

    def delete(self, req, resp, id):
        deleteIGroup(req, resp, igid=id)
