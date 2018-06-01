{% set openstackCluster = salt['grains.get']('expostack:ENV', '') %}

base:
  '*':
    - data
  'expostack:ENV:{{openstackCluster}}':
    - match: grain
    - expostack.{{openstackCluster}}

# vmsalt-head-master:/srv/pillar/top.sls
