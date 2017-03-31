from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions
from tachyonic.client import Client

from tachyonic.ui import menu
from ..controllers import createSR, viewSR, activateSR, deactivateSR


log = logging.getLogger(__name__)

menu.admin.add('/Infrastructure/Network/Service Requests',
               '/infrastructure/network/sr', 'network:admin')


@app.resources()
class ServiceRequest(object):

    def __init__(self):
        router.add(const.HTTP_GET, '/infrastructure/network/sr/create',
                   self.create, 'network:admin')
        router.add(const.HTTP_POST, '/infrastructure/network/sr/create',
                   self.create, 'network:admin')
        router.add(const.HTTP_GET, '/infrastructure/network/sr',
                   self.get, 'network:admin')
        # router.add(const.HTTP_GET, '/infrastructure/network/sr/view',
        #            self.getjson, 'network:admin')
        router.add(const.HTTP_GET, '/infrastructure/network/sr/view/{id}',
                   self.get, 'network:admin')
        router.add(const.HTTP_GET, '/infrastructure/network/sr/edit/{id}/activate',
                   self.activate, 'network:admin')
        router.add(const.HTTP_GET, '/infrastructure/network/sr/edit/{id}/deactivate',
                   self.deactivate, 'network:admin')

    def create(self, req, resp):
        createSR(req, resp)

    def get(self, req, resp, id=None):
        viewSR(req, resp, id=id)

    # def getjson(self, req, resp):
    #     getSelect2(req, resp, service_requests)

    def activate(self, req, resp, id):
        activateSR(req, resp, id=id)

    def deactivate(self, req, resp, id):
        deactivateSR(req, resp, id=id)