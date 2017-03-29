from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import json

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions


from tachyonic.ui import menu
from ..controllers import createIGroup, viewIGroup, editIGroup, deleteIGroup, getAPI


log = logging.getLogger(__name__)

menu.admin.add('/Infrastructure/Network/Interface Groups',
               '/infrastructure/network/igroup', 'network:admin')


@app.resources()
class InterfaceGroups(object):

    def __init__(self):
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroup/create',
                       self.create, 'network:admin')
        app.router.add(const.HTTP_POST, '/infrastructure/network/igroup/create',
                       self.create, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroup',
                       self.get, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroup/view',
                       self.getjson, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroup/view/{id}',
                       self.get, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroup/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(const.HTTP_POST, '/infrastructure/network/igroup/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/igroup/delete/{id}',
                       self.delete, 'network:admin')

    def create(self, req, resp):
        createIGroup(req, resp)

    def get(self, req, resp, id=None):
        viewIGroup(req, resp, id=id)

    def getjson(self, req, resp, id=None):
        api = getAPI(req)
        response_headers, result = api.execute(
            const.HTTP_GET, "/infrastructure/network/igroups?view=select2")
        return json.dumps(result, indent=4)

    def edit(self, req, resp, id):
        editIGroup(req, resp, id=id)

    def delete(self, req, resp, id):
        deleteIGroup(req, resp, id=id)
