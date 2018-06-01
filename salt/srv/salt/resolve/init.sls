
/etc/resolv.conf:
  file:
    - managed
    - user: root
    - group: root
    - mode: '0644'
    - source: salt://resolve/resolv.conf.jinja
    - template: jinja

# vmsalt-head-master:/srv/salt/resolve/init.sls
