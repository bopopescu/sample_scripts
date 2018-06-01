
/etc/motd:
  file:
    - managed
    - user: root
    - group: root
    - mode: '0644'
    - source: salt://motd/motd.jinja
    - template: jinja

# vmsalt-head-master:/srv/salt/motd/init.sls
