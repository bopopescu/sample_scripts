##
# Author: Suhaib Chishti
# Date Created: Monday, June 22, 2017
# Date Last Modified: Monday, July 13, 2017
##
 
 
 
{%- set baseFolder = "expostack/nova" %}
{%- set baseURL = "salt://" ~ baseFolder %}
{%- set fileName = baseFolder ~ "/init.sls" %}
{%- set expostackRole = salt['grains.get']('expostack:ROLE', []) %}
{%- set controllerHost = salt['pillar.get']('expostack:CONTROLLER_HOST', '') %}
#{%- set domain = salt['grains.get']('domain', 'domain.com') %}
#{%- set dbRootPass = salt['pillar.get']('expostack:DB_PASS', 'dbPass') %}
#{%- set adminToken = salt['pillar.get']('expostack:ADMIN_TOKEN', 'ADMIN') %}
#{%- set adminUser = salt['pillar.get']('expostack:ADMIN_USER', 'admin') %}
#{%- set novaDbName = salt['pillar.get']('expostack:NOVA_DBNAME', 'nova') %}
#{%- set novaDbUser = salt['pillar.get']('expostack:NOVA_DBUSER', 'nova') %}
#{%- set novaDbPass = salt['pillar.get']('expostack:NOVA_DBPASS', 'novaDbPass') %}
{%- set novaUser = salt['pillar.get']('expostack:NOVA_USER', 'nova') %}
{%- set novaPass = salt['pillar.get']('expostack:NOVA_PASS', 'novaPass') %}
{%- set neutronUser = salt['pillar.get']('expostack:NEUTRON_USER', 'neutron') %}
{%- set neutronPass = salt['pillar.get']('expostack:NEUTRON_PASS', 'neutronPass') %}
#{%- set novaEmail = salt['pillar.get']('expostack:NOVA_EMAIL', novaUser ~ '@' ~ domain) %}
{%- set endpointURL = "http://" ~ controllerHost ~ ":35357/v2.0" %}
{%- set endpointGlanceURL = "http://" ~ controllerHost ~ ":9292" %}
{%- set endpointURLV3 = "http://" ~ controllerHost ~ ":35357" %}
{%- set endpointPublicURLV3 = "http://" ~ controllerHost ~ ":5000" %}
#{%- set messagingType = salt['pillar.get']('expostack:MESSAGING_TYPE', 'rabbitmq') %}
{%- set messagingUser = salt['pillar.get']('expostack:MESSAGING_USER', messagingUser) %}
{%- set messagingPass = salt['pillar.get']('expostack:MESSAGING_PASS', messagingPass) %}
#{%- set managementInterface = salt['grains.get']('openstack:NETWORK_INTERFACE:MANAGEMENT', 'eth0') %}
{%- set managementIP = salt['grains.get']('fqdn', '') %}
{%- set osFamily = salt['grains.get']('os_family', '') %}
{%- set openstackRegion = "SCL1" %}
{%- set instancesPath = "/var/lib/nova/instances" %}
{%- set dhcpDomain = "vpc.dev.scl1.us.tribalfusion.net" %}


{%- if osFamily == 'Debian' %}

{% if 'compute' in expostackRole %}

net.ipv4.conf.default.rp_filter:
  sysctl.present:
    - value: "0"

net.ipv4.conf.all.rp_filter:
  sysctl.present:
    - value: "0"

net.bridge.bridge-nf-call-iptables:
  sysctl.present:
    - value: "1"

net.bridge.bridge-nf-call-ip6tables:
  sysctl.present:
    - value: "1"

{% for packages in ['libvirt-bin', 'nova-novncproxy', 'nova-api-metadata', 'nova-compute'] %}
{{fileName}} - Install {{packages}} package:
  pkg.installed:
    - name: nova-compute
    - name: nova-novncproxy
    - name: nova-api-metadata
    - name: libvirt-bin
{% endfor %}

{{fileName}} - Manage nova config file /etc/nova/nova.conf:
  file.managed:
    - name: /etc/nova/nova.conf
    - source: {{baseURL}}/nova.conf
    - makedirs: True
    - user: nova
    - group: nova
    - template: jinja
    - defaults:
#        novaDbUser: {{novaDbUser}}
#        novaDbPass: {{novaDbPass}}
#        novaDbName: {{novaDbName}}
        novaUser: {{novaUser}}
        novaPass: {{novaPass}}
        neutronUser: {{neutronUser}}
        neutronPass: {{neutronPass}}
        controllerHost: {{controllerHost}}
        endpointGlanceURL: {{endpointGlanceURL}}
        endpointURLV3: {{endpointURLV3}}
        endpointPublicURLV3: {{endpointPublicURLV3}}
#        messagingType: {{messagingType}}
        messagingUser: {{messagingUser}}
        messagingPass: {{messagingPass}}
        managementIP: {{managementIP}}
        instancesPath: {{instancesPath}}
        openstackRegion: {{openstackRegion}}
        dhcpDomain: {{dhcpDomain}}
        expostackRole: 'compute'
    - require:
      - pkg: {{fileName}} - Install nova-compute package

{{fileName}} - Manage config file /etc/libvirt/libvirtd.conf:
  file.managed:
    - name: /etc/libvirt/libvirtd.conf
    - source: {{baseURL}}/libvirtd.conf
    - user: root
    - group: root
    - template: jinja

{{fileName}} - Manage config file /etc/libvirt/libvirt.conf:
  file.managed:
    - name: /etc/libvirt/libvirt.conf
    - source: {{baseURL}}/libvirt.conf
    - user: root
    - group: root
    - template: jinja

{{fileName}} - Manage config file /etc/libvirt/qemu.conf:
  file.managed:
    - name: /etc/libvirt/qemu.conf
    - user: root
    - group: root
    - source: {{baseURL}}/qemu.conf
    - template: jinja

{{fileName}} - Manage config file /etc/nova/nova-compute.conf:
  file.managed:
    - name: /etc/nova/nova-compute.conf
    - user: nova
    - group: nova
    - source: {{baseURL}}/nova-compute.conf
    - template: jinja

{{fileName}} - Manage config file /etc/default/libvirt-bin:
  file.managed:
    - name: /etc/default/libvirt-bin
    - user: root
    - group: root
    - source: {{baseURL}}/libvirt-bin-etc-default
    - template: jinja

{{fileName}} - Manage config file /etc/init/libvirt-bin.conf:
  file.managed:
    - name: /etc/init/libvirt-bin.conf
    - user: root
    - group: root
    - source: {{baseURL}}/libvirt-bin.conf-etc-init
    - template: jinja

{% for service in ['libvirt-bin', 'nova-novncproxy', 'nova-api-metadata', 'nova-compute'] %}
{{fileName}} - Start {{service}} and enable it to start at boot:
  service.running:
    - name: {{service}}
    - enable: True
    - watch:
      - file: {{fileName}} - Manage nova config file /etc/nova/nova.conf
{% endfor %}

{% endif %}

{% endif %}
