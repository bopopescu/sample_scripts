{%- set roleOpenstack = salt['grains.get']('openstack:ROLE', []) %}
{%- set hostName = salt['grains.get']('host') %}

{%- set messagingType = 'rabbitmq' %}
{%- set messagingUser = 'guest' %}
{%- set messagingPass = 'guest' %}
{%- set networkingType = 'neutron' %}
{%- set tenantNetworkTypes = ['flat'] %}
{%- set controllerHost = 'vmsaltcontroller2.vpc.dev.scl1.us.mydoamin.net' %}
{%- set adminEmail = 'avnindra.singh@mydoamin.com' %}
{%- set adminPass = 'admin' %}
{%- set adminToken = '5b51862412cd005c2da9' %}
{%- set dbRootPass = 'admin' %}
{%- set keystoneDbPass = 'admin' %}
{%- set glanceDbPass = 'admin' %}
{%- set glancePass = 'admin' %}
{%- set novaDbPass = 'admin' %}
{%- set novaPass = 'admin' %}
{%- set neutronDbPass = 'admin' %}
{%- set neutronPass = 'admin' %}
{%- set metadataSecret = 'admin' %}


openstack:
  MESSAGING_TYPE: {{messagingType}}
  MESSAGING_USER: {{messagingUser}}
  MESSAGING_PASS: {{messagingPass}}
  NETWORKING_TYPE: {{networkingType}}
  CONTROLLER_HOST: {{controllerHost}}
  TENANT_NETWORK_TYPES: {{tenantNetworkTypes}}
{% if 'controller' in roleOpenstack %}
  ADMIN_EMAIL: {{adminEmail}}
  ADMIN_PASS: {{adminPass}}
  ADMIN_TOKEN: {{adminToken}}
  DB_PASS: {{dbRootPass}}
  KEYSTONE_DBPASS: {{keystoneDbPass}}
  GLANCE_DBPASS: {{glanceDbPass}}
  GLANCE_PASS: {{glancePass}}
  NOVA_DBPASS: {{novaDbPass}}
  NOVA_PASS: {{novaPass}}
  NEUTRON_DBPASS: {{neutronDbPass}}
  NEUTRON_PASS: {{neutronPass}}
  METADATA_SECRET: {{metadataSecret}}
{% endif %}

{% if 'compute' in roleOpenstack and 'network' in roleOpenstack %}
  NOVA_DBPASS: {{novaDbPass}}
  NOVA_PASS: {{novaPass}}
  NEUTRON_DBPASS: {{neutronDbPass}}
  NEUTRON_PASS: {{neutronPass}}
  METADATA_SECRET: {{metadataSecret}}
{% elif 'compute' in roleOpenstack %}
  NOVA_DBPASS: {{novaDbPass}}
  NOVA_PASS: {{novaPass}}
  NEUTRON_PASS: {{neutronPass}}
{% elif 'network' in roleOpenstack %}
  NEUTRON_DBPASS: {{neutronDbPass}}
  NEUTRON_PASS: {{neutronPass}}
  METADATA_SECRET: {{metadataSecret}}
{% endif %}
