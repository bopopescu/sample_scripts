{% if grains['kernel'] == 'SunOS' %}
/etc/opt/csw/salt/minion.d/beacons.conf:
    file.managed:
        - source: salt://beacons/beacons.conf.jinja
        - user: root
        - group: root
        - mode: 644
        - template: jinja

salt-minion:
    service.running:
        - enable: True
        - reload: True
        - watch:
           - file: /etc/opt/csw/salt/minion.d/beacons.conf
{% endif %}
