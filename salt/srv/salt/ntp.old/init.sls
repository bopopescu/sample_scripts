
{% from "ntp/map.jinja" import ntp with context %}

ntp:
  file.managed:
    - name: {{ ntp.file }}
    - user: root
    - group: root
    - mode: '0644'
    - context:
        driftfile: {{ ntp.driftfile }}
    - source: salt://ntp/ntp.conf.jinja
    - template: jinja
  service.running:
    - name: {{ ntp.service }}
    - watch:
      - file: ntp

# vmsalt-head-master:/srv/salt/ntp/init.sls
