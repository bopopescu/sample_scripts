##
# Author: Suhaib Chishti
# Date Created: Monday, June 22, 2017
# Date Last Modified: Monday, July 13, 2017
##
 
 
 
{%- set baseFolder = "expostack/ceilometer" %}
{%- set baseURL = "salt://" ~ baseFolder %}
{%- set fileName = baseFolder ~ "/init.sls" %}
{%- set expostackRole = salt['grains.get']('expostack:ROLE', []) %}
{%- set controllerHost = salt['pillar.get']('expostack:CONTROLLER_HOST', '') %}
#{%- set domain = salt['grains.get']('domain', 'domain.com') %}
{%- set nodeName = salt['grains.get']('nodename', '') %}
#{%- set dbRootPass = salt['pillar.get']('expostack:DB_PASS', 'dbPass') %}
#{%- set adminToken = salt['pillar.get']('expostack:ADMIN_TOKEN', 'ADMIN') %}
#{%- set adminUser = salt['pillar.get']('expostack:ADMIN_USER', 'admin') %}
#{%- set novaDbName = salt['pillar.get']('expostack:NOVA_DBNAME', 'nova') %}
#{%- set novaDbUser = salt['pillar.get']('expostack:NOVA_DBUSER', 'nova') %}
#{%- set novaDbPass = salt['pillar.get']('expostack:NOVA_DBPASS', 'novaDbPass') %}
{%- set ceilometerUser = salt['pillar.get']('expostack:CEILOMETER_USER', 'ceilometer') %}
{%- set ceilometerPass = salt['pillar.get']('expostack:CEILOMETER_PASS', '') %}
{%- set endpointURL = "http://" ~ controllerHost ~ ":35357/v2.0" %}
{%- set endpointGlanceURL = "http://" ~ controllerHost ~ ":9292" %}
{%- set endpointURLV3 = "http://" ~ controllerHost ~ ":35357" %}
{%- set endpointPublicURLV3 = "http://" ~ controllerHost ~ ":5000" %}
{%- set endpointZenossURL = "rabbitmq.vmzenoss-01.vpc.dev.scl1.us.tribalfusion.net" %}
{%- set endpointZenossUSER = "openstack" %}
{%- set endpointZenossPASS = "deGxDK2s2Zdl85n1ffzX" %}
{%- set endpointZenossDEVICE = "ExpoStackSCL" %}
{%- set endpointZenossVirtualHOST = "/zenoss" %}
#{%- set messagingType = salt['pillar.get']('expostack:MESSAGING_TYPE', 'rabbitmq') %}
{%- set messagingUser = salt['pillar.get']('expostack:MESSAGING_USER', messagingUser) %}
{%- set messagingPass = salt['pillar.get']('expostack:MESSAGING_PASS', messagingPass) %}
#{%- set managementInterface = salt['grains.get']('openstack:NETWORK_INTERFACE:MANAGEMENT', 'eth0') %}
{%- set managementIP = salt['grains.get']('fqdn', '') %}
{%- set osFamily = salt['grains.get']('os_family', '') %}
{%- set openstackRegion = "SCL1" %}
{%- set dhcpDomain = "vpc.dev.scl1.us.tribalfusion.net" %}


{%- if osFamily == 'Debian' %}

{% if 'compute' in expostackRole %}
{% for packages in ['ceilometer-common', 'ceilometer-collector', 'ceilometer-agent-compute'] %}
{{fileName}} - Install {{packages}} package:
  pkg.installed:
    - name: ceilometer-agent-compute
    - name: ceilometer-collector
    - name: ceilometer-common-api-metadata
{% endfor %}

#{{fileName}} - Managea cieolometer config file /var/lib/nova/instances/ceilometer_zenoss-1.1.0dev/ceilometer.conf:
{{fileName}} - Managea ceilometer config file /etc/ceilometer/ceilometer.conf:
  file.managed:
#    - name: /var/lib/nova/instances/ceilometer_zenoss-1.1.0dev/ceilometer.conf
    - name: '/etc/ceilometer/ceilometer.conf'
    - source: {{baseURL}}/ceilometer.conf
    - makedirs: True
    - template: jinja
    - defaults:
        controllerHost: {{controllerHost}}
        endpointGlanceURL: {{endpointGlanceURL}}
        endpointURL: {{endpointURL}}
        endpointURLV3: {{endpointURLV3}}
        endpointPublicURLV3: {{endpointPublicURLV3}}
        messagingUser: {{messagingUser}}
        messagingPass: {{messagingPass}}
        managementIP: {{managementIP}}
        openstackRegion: {{openstackRegion}}
        ceilometerUser: {{ceilometerUser}}
        ceilometerPass: {{ceilometerPass}}
        endpointZenossURL: {{endpointZenossURL}}
        endpointZenossUSER: {{endpointZenossUSER}}
        endpointZenossPASS: {{endpointZenossPASS}}
        endpointZenossDEVICE: {{endpointZenossDEVICE}}
        endpointZenossVirtualHOST: {{endpointZenossVirtualHOST}}
        dhcpDomain: {{dhcpDomain}}
        expostackRole: 'compute'

#{{fileName}} - Create symlink from '/var/lib/nova/instances/ceilometer_zenoss-1.1.0dev/ceilometer.conf' to '/etc/ceilometer/ceilometer.conf':
#  file.symlink:
#    - name: '/var/lib/nova/instances/ceilometer_zenoss-1.1.0dev/ceilometer.conf'
#    - target: '/etc/ceilometer/ceilometer.conf'
#    - defaults:


{{fileName}} - Managea ceilometer pipeline config file /etc/ceilometer/pipeline.yaml:
  file.managed:
#    - name: /var/lib/nova/instances/ceilometer_zenoss-1.1.0dev/ceilometer.conf
    - name: '/etc/ceilometer/pipeline.yaml'
    - source: {{baseURL}}/pipeline.yaml
    - makedirs: True
    - template: jinja
    - defaults:
        nodeName: {{nodeName}}

{% for service in ['ceilometer-collector', 'ceilometer-agent-compute'] %}
{{fileName}} - Start {{service}} and enable it to start at boot:
  service.running:
    - name: {{service}}
    - enable: True
    - watch:
      - file: {{fileName}} - Managea ceilometer config file /etc/ceilometer/ceilometer.conf
{% endfor %}

{% endif %}

{% endif %}
