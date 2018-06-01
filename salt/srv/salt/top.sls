
base:
  '*':
    - motd
    - ntp
    - resolve
    - logstash
  'os:CentOS':
    - match: grain
    - vmtools
  'os:Solaris':
    - match: grain
    - gbuilder
  'zonename:global':
    - match: grain
    - vmtools
  'openstack:CLUSTER:dev_cluster':
    - match: grain
    - openstack
  'openstack:CLUSTER:anil_cluster':
    - match: grain
    - openstack

#lab: 
#  '*':

#dev: 
#  '*': 

#prod: 
#   '*':

# vmsalt-head-master:/srv/salt/roots/little_top
