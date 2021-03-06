from django.utils.translation import ugettext_lazy as _

# The slug of the panel group to be added to HORIZON_CONFIG. Required.
#DISABLED = True

PANEL_GROUP = 'database'
# The display name of the PANEL_GROUP. Required.
PANEL_GROUP_NAME = _('Database')
# The slug of the dashboard the PANEL_GROUP associated with. Required.
PANEL_GROUP_DASHBOARD = 'project'
