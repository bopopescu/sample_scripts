
{% from "vmtools/map.jinja" import vmtools %}

vmtoolsd:
  cmd.run:
    - unless: {{ vmtools.script }} status
    - name: {{ vmtools.script }} start > /dev/null 2>&1
    - cwd: /

# vmsalt-head-master:/srv/salt/vmtools/init.sls
