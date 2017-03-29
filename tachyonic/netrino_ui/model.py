from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from tachyonic.neutrino.web.bootstrap3.forms import Form as Bootstrap
from tachyonic.netrino_common import model as common

log = logging.getLogger(__name__)


class IGroup(Bootstrap, common.IGroup):
    pass


class NetworkService(Bootstrap, common.NetworkService):
    pass
