from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions
from tachyonic.client import Client

from tachyonic.ui import menu
from ..controllers import viewDevice
from ..controllers import createDevice
from ..controllers import createDevicePost
from ..controllers import getPorts
from ..controllers import portsIGroup
from ..controllers import editDevice
from ..controllers import confirmRMdevice
from ..controllers import deleteDevice
from ..controllers import updateDevice

log = logging.getLogger(__name__)

menu.admin.add('/Infrastructure/Network/Devices',
               '/infrastructure/network/device', 'network:admin')


@app.resources()
class NetworkDevice(object):

    def __init__(self):
        app.router.add(const.HTTP_GET, '/infrastructure/network/device/create',
                       self.create, 'network:admin')
        app.router.add(const.HTTP_POST, '/infrastructure/network/device/create',
                       self.create, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/device',
                       self.get, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/device/{id}/ports',
                       self.getports, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/device/{id}/ports/igroup',
                       self.portsigroup, 'network:admin')
        app.router.add(const.HTTP_POST, '/infrastructure/network/devices/{id}/ports/igroup',
                       self.portsigroup, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/device/view/{id}',
                       self.get, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/device/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(const.HTTP_POST, '/infrastructure/network/device/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(const.HTTP_GET, '/infrastructure/network/device/delete/{id}',
                       self.delete)
        app.router.add(const.HTTP_POST, '/infrastructure/network/device/delete/{id}',
                       self.delete)

    def get(self, req, resp, id=None):
        return viewDevice(req, resp, id)

    def create(self, req, resp):
        if req.method == 'GET':
            createDevice(req, resp)
        elif req.method == 'POST':
            result = createDevicePost(req, resp)
            viewDevice(req, resp)

    def getports(self, req, resp, id):
        result = getPorts(req, id)
        return result

    def portsigroup(self, req, resp, id):
        portsIGroup(req, resp, id)

    def edit(self, req, resp, id):
        if req.method == 'GET':
            editDevice(req, resp, id=id)
        elif req.method == 'POST':
            result = updateDevice(req, id)
            viewDevice(req, resp, id=id, errors=result)

    def delete(self, req, resp, id):
        if req.method == 'GET':
            confirmRMdevice(req, resp, id=id)
        elif req.method == 'POST':
            result = deleteDevice(req, id)
            viewDevice(req, resp, errors=result)
