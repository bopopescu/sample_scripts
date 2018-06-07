#!/usr/bin/env python
import os
import sys


activate_this = '/home/horizon/horizon/.venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, '/home/horizon/horizon')
os.environ['DJANGO_SETTINGS_MODULE'] = 'openstack_dashboard.settings'

import django.core.wsgi
application = django.core.wsgi.get_wsgi_application()
