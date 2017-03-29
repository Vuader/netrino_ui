from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions
from tachyonic.client import Client

from tachyonic.ui import menu
from ..controllers import viewService, createService, editService, deleteService


log = logging.getLogger(__name__)

menu.admin.add('/Infrastructure/Network/Services',
               '/infrastructure/network/service', 'network:admin')


@app.resources()
class Service(object):

    def __init__(self):
        app.router.add(const.HTTP_GET, '/infrastructure/network/service',
                       self.get, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/service/view/{id}',
                       self.get, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/service/create',
                       self.create, 'network:admin')
        app.router.add(const.HTTP_POST, '/infrastructure/network/service/create',
                       self.create, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/service/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(const.HTTP_POST, '/infrastructure/network/service/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/service/delete/{id}',
                       self.delete, 'network:admin')

    def get(self, req, resp, id=None):
        return viewService(req, resp, id)

    def create(self, req, resp):
        createService(req, resp)

    def edit(self, req, resp, id):
        editService(req, resp, id)

    def delete(self, req, resp, id):
        deleteService(req, resp, id=id)
