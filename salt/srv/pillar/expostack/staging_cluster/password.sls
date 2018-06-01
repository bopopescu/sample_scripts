{%- set roleOpenstack = salt['grains.get']('expostack:ROLE', []) %}
{%- set hostName = salt['grains.get']('host') %}

{%- set messagingType = 'rabbitmq' %}
{%- set messagingUser = 'expo_stack' %}
{%- set messagingPass = 'BSoniC' %}
{%- set controllerHost = 'expostack.dev.scl1.us.mydoamin.net' %}
{%- set adminEmail = 'suhaib.chishti@mydoamin.com' %}
{%- set adminPass = 'admin' %}
{%- set dbRootPass = 'admin' %}
{%- set keystoneDbPass = 'admin' %}
{%- set glanceDbPass = 'admin' %}
{%- set glancePass = 'admin' %}
{%- set novaDbPass = 'admin' %}
{%- set novaUser = 'nova' %}
{%- set novaPass = 'BSoniC' %}
{%- set neutronDbName = 'expo_neutron' %}
{%- set neutronDbUser = 'expostack' %}
{%- set neutronDbPass = 'BSoniC' %}
{%- set neutronUser = 'neutron' %}
{%- set neutronPass = 'BSoniC' %}
{%- set metadataSecret = 'admin' %}
{%- set ceilometerUser = 'ceilometer' %}
{%- set ceilometerPass = 'BSoniC' %}


expostack:
  MESSAGING_TYPE: {{messagingType}}
  MESSAGING_USER: {{messagingUser}}
  MESSAGING_PASS: {{messagingPass}}
  CONTROLLER_HOST: {{controllerHost}}

{% if 'compute' in roleOpenstack and 'network' in roleOpenstack %}
  NOVA_DBPASS: {{novaDbPass}}
  NOVA_PASS: {{novaPass}}
  NEUTRON_DBPASS: {{neutronDbPass}}
  NEUTRON_PASS: {{neutronPass}}
  METADATA_SECRET: {{metadataSecret}}
{% elif 'compute' in roleOpenstack %}
  NOVA_USER: {{novaUser}}
  NOVA_PASS: {{novaPass}}
  NEUTRON_USER: {{neutronUser}}
  NEUTRON_PASS: {{neutronPass}}
  NEUTRON_DBNAME: {{neutronDbName}}
  NEUTRON_DBUSER: {{neutronDbUser}}
  NEUTRON_DBPASS: {{neutronDbPass}}
  CEILOMETER_USER: {{ceilometerUser}}
  CEILOMETER_PASS: {{ceilometerPass}}
{% elif 'network' in roleOpenstack %}
  NEUTRON_DBPASS: {{neutronDbPass}}
  NEUTRON_PASS: {{neutronPass}}
  METADATA_SECRET: {{metadataSecret}}
{% endif %}
