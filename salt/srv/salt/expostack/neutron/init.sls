##
# Author: Suhaib Chishti 
# Date Created: Monday, June 29, 2017
# Date Last Modified: Monday, July 13, 2017
##


{%- set baseFolder = "expostack/neutron" %}
{%- set baseURL = "salt://" ~ baseFolder %}
{%- set fileName = baseFolder ~ "/init.sls" %}
{%- set expostackRole = salt['grains.get']('expostack:ROLE', []) %}
{%- set controllerHost = salt['pillar.get']('expostack:CONTROLLER_HOST', '') %}
#{%- set domain = salt['grains.get']('domain', 'domain.com') %}
#{%- set tunnelInterface = salt['grains.get']('expostack:NETWORK_INTERFACE:TUNNEL', salt['grains.get']('expostack:NETWORK_INTERFACE:MANAGEMENT')) %}
#{%- set tunnelIP = salt['grains.get']('ip4_interfaces:'~tunnelInterface)[0] %}
#{%- set externalInterface = salt['grains.get']('expostack:NETWORK_INTERFACE:EXTERNAL', 'eth1') %}
#{%- set dbRootPass = salt['pillar.get']('expostack:DB_PASS', 'dbPass') %}
#{%- set adminToken = salt['pillar.get']('expostack:ADMIN_TOKEN', 'ADMIN') %}
#{%- set adminUser = salt['pillar.get']('expostack:ADMIN_USER', 'admin') %}
{%- set neutronDbName = salt['pillar.get']('expostack:NEUTRON_DBNAME', 'neutron') %}
{%- set neutronDbUser = salt['pillar.get']('expostack:NEUTRON_DBUSER', 'neutron') %}
{%- set neutronDbPass = salt['pillar.get']('expostack:NEUTRON_DBPASS', 'neutronDbPass') %}
{%- set neutronUser = salt['pillar.get']('expostack:NEUTRON_USER', 'neutron') %}
{%- set neutronPass = salt['pillar.get']('expostack:NEUTRON_PASS', 'neutronPass') %}
{%- set novaUser = salt['pillar.get']('expostack:NOVA_USER', 'nova') %}
{%- set novaPass = salt['pillar.get']('expostack:NOVA_PASS', 'novaPass') %}
{%- set endpointURL = "http://" ~ controllerHost ~ ":35357/v2.0" %}
{%- set endpointPublicURLV3 = "http://" ~ controllerHost ~ ":5000" %}
{%- set endpointNovaURL = "http://" ~ controllerHost ~ ":8774/v2" %}
{%- set messagingType = salt['pillar.get']('expostack:MESSAGING_TYPE', 'rabbitmq') %}
{%- set messagingUser = salt['pillar.get']('expostack:MESSAGING_USER', messagingUser) %}
{%- set messagingPass = salt['pillar.get']('expostack:MESSAGING_PASS') %}
{% from "expostack/neutron/map.jinja" import networkNameDEV with context %}
{% from "expostack/neutron/map.jinja" import networkNamePROD with context %}
{% from "expostack/neutron/map.jinja" import networkNameORACLE with context %}
{% from "expostack/neutron/map.jinja" import networkNameCORPORATE with context %}
{% from "expostack/neutron/map.jinja" import physicalDeviceDEV with context %}
{% from "expostack/neutron/map.jinja" import physicalDevicePROD with context %}
{% from "expostack/neutron/map.jinja" import physicalDeviceORACLE with context %}
{% from "expostack/neutron/map.jinja" import physicalDeviceCORPORATE with context %}
{% from "expostack/neutron/map.jinja" import ExpostackNetworks with context %}
{%- set expostackRegion = "SCL1" %}
{%- set osFamily = salt['grains.get']('os_family', '') %}

{%- if osFamily == 'Debian' %}

{% if 'compute' in expostackRole %}
{{fileName}} - Install necessary networking components:
  pkg.installed:
    - pkgs:
      - neutron-plugin-linuxbridge-agent


{{fileName}} - Manage neutron config file /etc/neutron/neutron.conf:
  file.managed:
    - name: /etc/neutron/neutron.conf
    - source: {{baseURL}}/neutron.conf
    - makedirs: True
    - template: jinja
    - defaults:
        neutronDbUser: {{neutronDbUser}}
        neutronDbPass: {{neutronDbPass}}
        neutronDbName: {{neutronDbName}}
        neutronUser: {{neutronUser}}
        neutronPass: {{neutronPass}}
        novaUser: {{novaUser}}
        novaPass: {{novaPass}}
        controllerHost: {{controllerHost}}
        messagingType: {{messagingType}}
        messagingUser: {{messagingUser}}
        messagingPass: {{messagingPass}}
        expostackRole: {{expostackRole}}
        endpointURL: {{endpointURL}}
        endpointPublicURLV3: {{endpointURL}}
        endpointNovaURL: {{endpointNovaURL}}
        expostackRegion: {{expostackRegion}}
        networkNameDEV: {{networkNameDEV}}
        networkNamePROD: {{networkNamePROD}}
        networkNameORACLE: {{networkNameORACLE}}
        networkNameCORPORATE: {{networkNameCORPORATE}}
        physicalDeviceDEV: {{physicalDeviceDEV}}
        physicalDevicePROD: {{physicalDevicePROD}}
        physicalDeviceORACLE: {{physicalDeviceORACLE}}
        physicalDeviceCORPORATE: {{physicalDeviceCORPORATE}}
    - require:
      - pkg: {{fileName}} - Install necessary networking components

{{fileName}} - Manage ml2 plugin config file /etc/neutron/plugins/ml2/ml2_conf.ini:
  file.managed:
    - name: /etc/neutron/plugins/ml2/ml2_conf.ini
    - source: {{baseURL}}/ml2_conf.ini
    - makedirs: True
    - template: jinja
    - defaults:
        networkNameDEV: {{networkNameDEV}}
        networkNamePROD: {{networkNamePROD}}
        networkNameORACLE: {{networkNameORACLE}}
        networkNameCORPORATE: {{networkNameCORPORATE}}
        physicalDeviceDEV: {{physicalDeviceDEV}}
        physicalDevicePROD: {{physicalDevicePROD}}
        physicalDeviceORACLE: {{physicalDeviceORACLE}}
        physicalDeviceCORPORATE: {{physicalDeviceCORPORATE}}
        ExpostackNetworks: {{ExpostackNetworks}}
    - require:
      - pkg: {{fileName}} - Install necessary networking components

{{fileName}} - Create symlink from '/etc/neutron/plugin.ini' to '/etc/neutron/plugins/ml2/ml2_conf.ini':
  file.symlink:
    - name: '/etc/neutron/plugin.ini'
    - target: '/etc/neutron/plugins/ml2/ml2_conf.ini'
    - defaults:
        networkNameDEV: {{networkNameDEV}}
        networkNamePROD: {{networkNamePROD}}
        networkNameORACLE: {{networkNameORACLE}}
        networkNameCORPORATE: {{networkNameCORPORATE}}
        physicalDeviceDEV: {{physicalDeviceDEV}}
        physicalDevicePROD: {{physicalDevicePROD}}
        physicalDeviceORACLE: {{physicalDeviceORACLE}}
        physicalDeviceCORPORATE: {{physicalDeviceCORPORATE}}
    - require:
      - pkg: {{fileName}} - Install necessary networking components

{{fileName}} - Manage ml2 plugin config file /etc/neutron/plugins/ml2/linuxbridge_agent.ini:
  file.managed:
    - name: /etc/neutron/plugins/ml2/linuxbridge_agent.ini
    - source: {{baseURL}}/linuxbridge_agent.ini
    - makedirs: True
    - template: jinja
    - defaults:
        networkNameDEV: {{networkNameDEV}}
        networkNamePROD: {{networkNamePROD}}
        networkNameORACLE: {{networkNameORACLE}}
        networkNameCORPORATE: {{networkNameCORPORATE}}
        physicalDeviceDEV: {{physicalDeviceDEV}}
        physicalDevicePROD: {{physicalDevicePROD}}
        physicalDeviceORACLE: {{physicalDeviceORACLE}}
        physicalDeviceCORPORATE: {{physicalDeviceCORPORATE}}
    - require:
      - pkg: {{fileName}} - Install necessary networking components

{% if 'compute' in expostackRole %}
{% for service in ['neutron-plugin-linuxbridge-agent'] %}
{{fileName}} - Start {{service}} service and enable it to start at boot:
  service.running:
    - name: {{service}}
    - enable: True
    - watch:
      - file: {{fileName}} - Manage ml2 plugin config file /etc/neutron/plugins/ml2/ml2_conf.ini
    - require:
      - pkg: {{fileName}} - Install necessary networking components
{% endfor %}
{% endif %}

{% endif %}

{% endif %}
