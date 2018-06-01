##
# Author: Nitin Madhok
# Date Created: Sunday, June 21, 2015
# Date Last Modified: Thursday, June 25, 2015
##


{%- set baseFolder = "expostack" %}
{%- set baseURL = "salt://" ~ baseFolder %}
{%- set fileName = baseFolder ~ "/init.sls" %}
{%- set role = salt['grains.get']('expostack', '') %}

{%- if role %}

include:
  - .nova
  - .neutron
  - .ceilometer

{% endif %}
