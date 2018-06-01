{%- set baseFolder = "expostack" %}
{%- set openstackCluster = salt['grains.get']('expostack:ENV', '') %}
{%- set baseURL = baseFolder ~ "." ~ openstackCluster %}

include:
  - {{baseURL}}.password
