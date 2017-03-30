import re
import sys
import json
from pyipcalc import *
from collections import OrderedDict
from tachyonic import jinja
from tachyonic.neutrino import exceptions as exceptions
from tachyonic.neutrino import constants as const
from tachyonic.client import Client as RestClient
from tachyonic.ui.views import ui
from tachyonic.ui.views.datatable import datatable
from . import model


def getAPI(req):
    config = req.config.get('endpoints')
    netrino_api = config.get('netrino_api')
    api = RestClient(netrino_api)
    return api


def getFields(snippet, activate_snippet, deactivate_snippet):
    fields = re.findall('{{ ?(.*?) ?}}', snippet)
    if activate_snippet:
        afields = re.findall('{{ ?(.*?) ?}}', activate_snippet)
    else:
        afields = None
    if deactivate_snippet:
        dfields = re.findall('{{ ?(.*?) ?}}', deactivate_snippet)
    else:
        dfields = None
    if not fields:
        fields = []
    if afields:
        fields.extend(afields)
    if dfields:
        fields.extend(dfields)
    if fields:
        fields = ','.join(list(set(fields)))
    else:
        fields = None
    return fields


def viewIGroup(req, resp, id=None):
    if id:
        api = getAPI(req)
        headers, response = api.execute(
            const.HTTP_GET, "/infrastructure/network/igroup/%s" % (id,))
        form = model.IGroup(response, validate=False, readonly=True)
        ui.view(req, resp, content=form, id=id, title='View Interface Group')
    else:
        title = 'Interface Groups'
        fields = OrderedDict()
        fields['name'] = 'Interface Group Name'
        dt = datatable(
            req, 'igroups', '/infrastructure/network/igroups?view=datatable',
            fields, view_button=True, endpoint="netrino_api")
        ui.view(req, resp, content=dt, title=title)


def editIGroup(req, resp, id):
    if req.method == const.HTTP_POST:
        form = model.IGroup(req.post, validate=True, readonly=True)
        api = getAPI(req)
        headers, response = api.execute(const.HTTP_PUT, "/infrastructure/network/igroup/%s" %
                                        (id,), form)
    else:
        api = getAPI(req)
        headers, response = api.execute(
            const.HTTP_GET, "/infrastructure/network/igroup/%s" % (id,))
        form = model.IGroup(response, validate=False)
        ui.edit(req, resp, content=form, id=id, title='Edit Interface Group')


def createIGroup(req, resp):
    if req.method == const.HTTP_POST:
        try:
            form = model.IGroup(req.post, validate=True)
            api = getAPI(req)
            headers, response = api.execute(
                const.HTTP_POST, "/infrastructure/network/igroups", form)
            if 'id' in response:
                id = response['id']
                viewIGroup(req, resp, id=id)
        except exceptions.HTTPBadRequest as e:
            form = model.User(req, validate=False)
            ui.create(req, resp, content=form, title='Create User', error=[e])
    else:
        form = model.IGroup(req.post, validate=False)
        ui.create(req, resp, content=form, title='Create Interface Group')


def deleteIGroup(req, resp, id):
    try:
        api = getAPI(req)
        headers, response = api.execute(
            const.HTTP_DELETE, "/infrastructure/network/igroup/%s" % (id,))
        viewIGroup(req, resp)
    except exceptions.HTTPBadRequest as e:
        ui.edit(req, resp, content=form, id=id, title='Edit Interface Group')


def viewService(req, resp, id=None):
    return_format = req.headers.get('X-Format')
    if id:
        api = getAPI(req)
        headers, service = api.execute(
            const.HTTP_GET, "/infrastructure/network/services/%s" % (id,))
        if return_format == "fields":
            fields = service['fields'].split(',')
            return json.dumps(fields, indent=4)
        templateFile = 'tachyonic.netrino_ui/service/createservice.html'
        t = jinja.get_template(templateFile)
        renderValues = {}
        renderValues['view'] = 'view'
        renderValues['serviceID'] = id
        renderValues['serviceName'] = service['name']
        renderValues['interfaceGroup'] = service['interface_group']
        renderValues['userRole'] = service['user_role']
        renderValues['snippet'] = service['config_snippet']
        renderValues['activate'] = service['activate_snippet']
        renderValues['deactivate'] = service['deactivate_snippet']
        renderValues['app'] = req.get_app()
        form = t.render(**renderValues)
        title = service['name']
        ui.view(req, resp, id=id, content=form, title=title)
    else:
        if return_format == "select2":
            api = getAPI(req)
            headers, response = api.execute(
                const.HTTP_GET, "/infrastructure/network/services?view=datatable")
            result = []
            for r in response:
                result.append({'id': r['id'], 'text': r['name']})
            return json.dumps(result, indent=4)
        else:
            title = 'Network Services'
            fields = OrderedDict()
            fields['name'] = 'Service Name'
            # TODO:
            fields['user_role'] = 'Roles'
            fields['interface_group'] = 'Interface Group'
            dt = datatable(
                req, 'services',
                '/infrastructure/network/services?view=datatable',
                fields, view_button=True, endpoint="netrino_api")
            ui.view(req, resp, content=dt, title=title)


def editService(req, resp, id):
    if req.method == const.HTTP_POST:
        api = getAPI(req)
        values = req.post
        snippet = values.get('config_snippet', '')
        activate_snippet = values.get('activate_snippet', None)
        deactivate_snippet = values.get('deactivate_snippet', None)
        fields = getFields(snippet, activate_snippet, deactivate_snippet)
        form = model.NetworkService(req.post, validate=True)
        form['fields'] = fields
        headers, response = api.execute(
            const.HTTP_PUT, "/infrastructure/network/services/%s" % (id,), form)
    else:
        api = getAPI(req)
        headers, service = api.execute(
            const.HTTP_GET, "/infrastructure/network/services/%s" % (id,))
        templateFile = 'tachyonic.netrino_ui/service/createservice.html'
        t = jinja.get_template(templateFile)
        renderValues = {}
        renderValues['serviceID'] = id
        renderValues['serviceName'] = service['name']
        renderValues['interfaceGroup'] = service['interface_group']
        renderValues['userRole'] = service['user_role']
        renderValues['snippet'] = service['config_snippet']
        renderValues['activate'] = service['activate_snippet']
        renderValues['deactivate'] = service['deactivate_snippet']
        renderValues['app'] = req.get_app()
        form = t.render(**renderValues)
        title = service['name']
        ui.edit(req, resp, id=id, content=form, title=title)


def createService(req, resp, **kwargs):
    if req.method == const.HTTP_POST:
        try:
            api = getAPI(req)
            values = req.post
            snippet = values.get('config_snippet', '')
            activate_snippet = values.get('activate_snippet', None)
            deactivate_snippet = values.get('deactivate_snippet', None)
            fields = getFields(snippet, activate_snippet, deactivate_snippet)
            form = model.NetworkService(req.post, validate=True)
            form['fields'] = fields
            headers, response = api.execute(
                const.HTTP_POST, "/infrastructure/network/services", form)
            if 'id' in response:
                id = response['id']
                viewService(req, resp, id=id)
        except exceptions.HTTPBadRequest as e:
            req.method = const.HTTP_GET
            createService(req, resp, error=[e])
    else:
        renderValues = {}
        if req.post.get('name'):
            renderValues['serviceName'] = req.post.get('name')
            renderValues['interfaceGroup'] = req.post.get('interface_group')
            renderValues['userRole'] = req.post.get('user_role')
            renderValues['snippet'] = req.post.get('config_snippet')
            renderValues['activate'] = req.post.get('activate_snippet')
            renderValues['deactivate'] = req.post.get('deactivate_snippet')
        renderValues['app'] = req.get_app()
        templateFile = 'tachyonic.netrino_ui/service/createservice.html'
        t = jinja.get_template(templateFile)
        form = t.render(**renderValues)
        title = 'Create a Network Service'
        ui.create(req, resp, content=form,
                  title='Create Network Service', **kwargs)


def deleteService(req, resp, id):
    try:
        api = getAPI(req)
        headers, response = api.execute(
            const.HTTP_DELETE, "/infrastructure/network/services/%s" % (id,))
        viewService(req, resp)
    except Exception, e:  # hierdie gebeur nie met api.execute nie
        editService(req, resp, id, error=[e])


def viewDevice(req, resp, id=None, **kwargs):
    renderValues = {}
    renderValues['resource'] = 'Device'
    renderValues['window'] = '#window_content'
    fields = OrderedDict()
    if id:
        fields['port'] = 'Interface'
        fields['alias'] = 'IP'
        fields['prefix_len'] = 'Prefix Length'
        fields['descr'] = 'Description'
        fields['mac'] = 'Mac'
        fields['igroupname'] = 'Interface Group'
        fields['present'] = 'Present'
        fields['customername'] = 'Customer'
        fields['service'] = 'Service'
        apiurl = "/infrastructure/network/devices/" + id + "/ports"
        dt = datatable(req, 'devices', apiurl, fields, endpoint="netrino_api")
        edit_url = "/ui/infrastructure/network/device/edit/" + id
        back_url = "/ui/infrastructure/network/device/"
        api = getAPI(req)
        response_headers, device = api.execute(
            const.HTTP_GET, "/infrastructure/network/devices/" + id)
        renderValues['title'] = device['name']
        #
        # Perhaps in the future we can have this Refresh button here
        #
        #description = '<form action="../add/'
        #description += id
        #description += '" method="post">'
        description = 'As discovered on '
        description += str(device['last_discover'])
        #description += '''. 
        #        <button name="refreshdevice">Refresh</button>
        #        </form>'''
        renderValues['device_id'] = id
        renderValues['edit_url'] = edit_url
        renderValues['back_url'] = back_url
        renderValues['window'] = '#window_content'
        renderValues['back'] = True
        renderValues['create_url'] = ''
        dt = description + dt
        dt += ('<button class="btn btn-primary" ' +
               'data-url="infrastructure/network/device/' +
               id + '/ports/igroup">' +
               'Assign Interface Groups</button><hr>')
    else:
        return_format = req.headers.get('X-Format')
        if return_format == "select2":
            api = getAPI(req)
            headers, response = api.execute(
                const.HTTP_GET, "/infrastructure/network/devices")
            result = []
            for r in response:
                result.append({'id': r['id'], 'text': r['name']})
            return json.dumps(result, indent=4)
        else:
            fields['name'] = 'Device Name'
            fields['os'] = 'OS'
            fields['os_ver'] = 'OS Version'
            fields['last_discover'] = 'Last Updated'
            dt = datatable(
                req, 'devices', '/infrastructure/network/devices?view=datatable',
                fields, view_button=True, endpoint="netrino_api")
            renderValues['title'] = 'Network Devices'

    ui.view(req, resp, content=dt, **renderValues)


def portsIGroup(req, resp, id, **kwargs):
    if req.method == const.HTTP_POST:
        igroup = req.post.get('interface_group')
        api = getAPI(req)
        api_url = '/infrastructure/network/igroup/%s/port' % (igroup,)
        data = {'device': id}
        ports = req.post.getlist('port')
        for port in ports:
            data['port'] = port
            response_headers, result = api.execute(
                const.HTTP_PUT, api_url, obj=data)
    else:
        back_url = 'infrastructure/network/devices/" + id + "/ports"'
        fields = OrderedDict()
        fields['port'] = 'Interface'
        fields['igroupname'] = 'Interface Group'
        apiurl = "infrastructure/network/devices/" + id + "/ports"
        app = req.get_app()
        dt = datatable(req, 'devices', apiurl, fields,
                       checkbox=True, endpoint="netrino_api",
                       id_field=0)
        back_url = "/ui/infrastructure/network/device/view/%s" % (id,)
        renderValues = {}
        renderValues['dt'] = dt
        renderValues['app'] = app
        renderValues['id'] = id
        templateFile = 'tachyonic.netrino_ui/device/portigroup.html'
        t = jinja.get_template(templateFile)
        content = t.render(**renderValues)
        # ui.edit(req, resp, content=content, **renderValues)
        # res = resource(req)
        kwargs['save_url'] = "%s/%s/%s" % (app, apiurl, 'igroup')
        kwargs['content'] = content
        kwargs['back_url'] = back_url
        kwargs['window'] = '#window_content'
        t = jinja.get_template('tachyonic.ui/view.html')
        resp.body = t.render(**kwargs)


def createDevice(req, resp):
    title = 'Add a Network Device (or Devices)'
    renderValues = {'title': title}
    renderValues['back_url'] = 'infrastructure/network/device'
    renderValues['window'] = '#window_content'
    renderValues['submit_url'] = 'infrastructure/network/device/create'
    renderValues['formid'] = 'device'
    renderValues['resource'] = 'Device'

    templateFile = 'tachyonic.netrino_ui/device/create.html'
    t = jinja.get_template(templateFile)
    form = t.render(**renderValues)

    ui.create(req, resp, content=form, **renderValues)


def editDevice(req, resp, id):
    title = 'Update Device'
    renderValues = {'title': title}
    renderValues['window'] = '#window_content'

    api = getAPI(req)
    response_headers, device = api.execute(
        const.HTTP_GET, "/infrastructure/network/devices/" + id)
    if device['id']:
        renderValues['device_ip'] = dec2ip(int(id), 4)
        renderValues['id'] = id
        renderValues['commstring'] = device['snmp_comm']
        renderValues['title'] = "Refresh " + device['name']
        renderValues[
            'back_url'] = 'infrastructure/network/device/view/' + id
        renderValues[
            'submit_url'] = 'infrastructure/network/device/edit/' + id
        renderValues[
            'delete_url'] = 'infrastructure/network/device/delete/' + id
        renderValues['formid'] = 'device'
        renderValues['resource'] = 'Device'
    else:
        raise exceptions.HTTPBadRequest("Device not found")  # Device not found

    templateFile = 'tachyonic.netrino_ui/device/create.html'
    t = jinja.get_template(templateFile)
    form = t.render(**renderValues)

    ui.edit(req, resp, content=form, **renderValues)


def createDevicePost(req, resp):
    api = getAPI(req)
    values = req.post
    subnet = values.get('device_ip')
    data = {'snmp_comm': values.get('snmp_community')}
    issubnet = re.search('/', subnet)
    if not issubnet:
        subnet += "/32"
        try:
            subnet = IPNetwork(subnet)
        except:
            raise exceptions.HTTPBadRequest(
                title="Failure", description="Invalid IP address")
    results = []
    for ip in subnet:
        ver = ip._version
        ip = ip.ip_network
        data['id'] = ip2dec(ip, 4)
        response_headers, result = api.execute(
            const.HTTP_POST, "/infrastructure/network/devices", obj=data)
        results.append(result)
    return results

#
# To Handle the POST of edit device:
# Nog besig met die
#


def updateDevice(req, id):
    api = getAPI(req)
    response_headers, device = api.execute(
        const.HTTP_PUT, "/infrastructure/network/devices/" + id)


def confirmRMdevice(req, resp, id):
    api = getAPI(req)
    response_headers, device = api.execute(
        const.HTTP_GET, "/infrastructure/network/devices/" + id)
    if not 'id' in device:
        raise exceptions.HTTPBadRequest(title="Not Found",
                                        description="Device not found: %s" % id)
    request_headers = {}
    request_headers['X-Search-Specific'] = 'device=' + \
        id + ',status=ACTIVE'
    response_headers, result = api.execute(
        const.HTTP_GET, "/infrastructure/network/service_requests/", headers=request_headers)
    num_serv = len(result)
    templateFile = 'tachyonic.netrino_ui/device/rmdevice.html'
    renderValues = {'title': "Remove " + device['name']}
    if num_serv > 0:
        warn = (dec2ip(int(id), 4), str(num_serv))
        renderValues['warn'] = warn
    renderValues['device_id'] = id
    t = jinja.get_template(templateFile)
    form = t.render(**renderValues)
    ui.edit(req, resp, content=form, id=id, **renderValues)


def deleteDevice(req, id):
    api = getAPI(req)
    response_headers, result = api.execute(
        const.HTTP_DELETE, "/infrastructure/network/devices/" + id)
    return result


def getPorts(req, id):
    api = getAPI(req)
    response_headers, response = api.execute(
        const.HTTP_GET, "/infrastructure/network/devices/%s/ports" % (id,))
    return_format = req.headers.get('X-Format')
    if return_format == "select2":
        result = []
        for r in response:
            result.append({'id': r['port'], 'text': r['port']})
        return json.dumps(result, indent=4)
    else:
        return json.dumps(response, indent=4)


def createSR(req, resp, **kwargs):
    if req.method == const.HTTP_POST:
        api = getAPI(req)
        values = req.post
        postValues = {}
        for value in values:
            if value == 'device':
                devices = values.get(value)
                deviceIDs = devices.split(',')
            else:
                postValues[value] = values.get(value)

        for device in deviceIDs:
            postValues['device'] = int(device)
            headers, response = api.execute(
                const.HTTP_POST, "/infrastructure/network/service_requests", obj=postValues)
        viewSR(req, resp)
    else:
        tenant = req.context.get('tenant_id')
        if not tenant:
            raise exceptions.HTTPBadRequest(
                title="No Tenant selected",
                description="Please select Tenant")
        title = 'Create a service request'
        renderValues = {'title': title}
        renderValues['window'] = '#window_content'
        renderValues['back_url'] = 'infrastructure/network/sr'
        renderValues['formid'] = 'service_request'
        renderValues['app'] = req.get_app()
        tenant = req.context.get('tenant_id')
        templateFile = 'tachyonic.netrino_ui/service_requests/create.html'
        t = jinja.get_template(templateFile)
        form = t.render(**renderValues)
        renderValues['submit_url'] = 'infrastructure/network/sr/create'

        ui.create(req, resp, content=form, **renderValues)


def viewSR(req, resp, id=None, **kwargs):
    renderValues = {}
    renderValues['window'] = '#window_content'
    config = req.config.get('endpoints')
    netrino_api = config.get('netrino_api')
    if id:
        api = RestClient(netrino_api)
        headers, response = api.execute(
            const.HTTP_GET, "/infrastructure/network/service_requests/%s" % (id,))
        templateFile = 'tachyonic.netrino_ui/service_requests/view.html'
        t = jinja.get_template(templateFile)
        response = response[0]
        renderValues = response
        if response['status'] in ["SUCCESS", "INACTIVE", "UNKNOWN"] and response['service']:
            activate_url = ("infrastructure/network/sr/" +
                            "edit/" + id + "/activate")
            renderValues['activate_url'] = activate_url
        elif response['status'] == "ACTIVE":
            deactivate_url = ("infrastructure/network/sr/" +
                              "edit/" + id + "/deactivate")
            renderValues['deactivate_url'] = deactivate_url
        back_url = "infrastructure/network/service_requests/"
        renderValues['back_url'] = back_url
        renderValues['title'] = "View Service Request"
        content = t.render(**renderValues)
        ui.view(req, resp, content=content, **renderValues)
    else:
        fields = OrderedDict()
        fields['creation_date'] = 'Creation Date'
        fields['customer'] = 'Customer'
        fields['device'] = 'Device'
        fields['service'] = 'Service'
        fields['status'] = 'Status'
        content = datatable(
            req, 'service_requests', '/infrastructure/network/service_requests',
            fields, view_button=True, endpoint="netrino_api")
        renderValues['title'] = "Service Requests"

    ui.view(req, resp, content=content, **renderValues)


def activateSR(req, resp, id=id):
    api = getAPI(req)
    headers, response = api.execute(
        const.HTTP_PUT, "/infrastructure/network/service_requests/%s" % (id,))
    viewSR(req, resp, id=id)


def deactivateSR(req, resp, id=id):
    api = getAPI(req)
    headers, response = api.execute(
        const.HTTP_DELETE, "/infrastructure/network/service_requests/%s" % (id,))
    viewSR(req, resp, id=id)
