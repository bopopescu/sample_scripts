{%- set baseFolder = "openstack/common" %}
{%- set fileName = baseFolder ~ "/repos.sls" %}
{%- set role = salt['grains.get']('openstack', '') %}
{%- set osFamily = salt['grains.get']('os_family', '') %}

{%- if osFamily == "RedHat" and role %}
{{fileName}} - openstack:
  pkg.installed:
    - name: centos-release-openstack-mitaka

{{fileName}} - mysql repository:
  pkg.installed:
    - sources:
        - mysql-community-release: http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
{% endif %} 
