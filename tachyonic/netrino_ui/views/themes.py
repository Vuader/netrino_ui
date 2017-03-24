from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from tachyonic import app


log = logging.getLogger(__name__)


@app.resources()
class Themes(object):

    def __init__(self):
        self.css = app.context['css']
        self.css['.netrino-form'] = {}
        self.css['.netrino-form']['max-width'] = '530px'
        self.css['.netrino-form']['margin'] = '0 auto'
        self.css['.netrino-form']['padding'] = '15px'
        self.css['.select2-dropdown'] = {}
        self.css['.select2-dropdown']['z-index'] = '9001'
        app.context['css'] = self.css
