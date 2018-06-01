{% set lower_os_name = grains['os'].lower() %}
{% if lower_os_name == 'ubuntu' %}
{%   set release_ver = grains['lsb_distrib_release'] %}
{% else %}
{%   set release_ver =  grains['osmajorrelease'] %}
{% endif %}
{% set domain_src = 'id' %}
{% if 'vpc' in grains[domain_src]: %}
{%   set domain = '.'.join(grains[domain_src].split('.')[2:]) %}
{% else %}
{%   set domain = '.'.join(grains[domain_src].split('.')[1:]) %}
{% endif %}
{% if grains['kernel'] == 'SunOS' %}
{%   set symlink_dest = pillar['esmshare'][domain] %}
/mnt/esmmonitor01:
  file.symlink:
    - target: {{ symlink_dest }}
/opt/csw:
  file.symlink:
    - target: /mnt/esmmonitor01/salt-minion/solaris-root/opt/csw
/etc/opt/csw/salt:
  file.directory:
    - mkdirs: True
/etc/opt/csw/salt/pki/minion:
  file.directory:
    - mkdirs: True
/etc/opt/csw/salt/minion.d:
  file.directory:
    - mkdirs: True
/etc/salt:
  file.symlink:
    - target: /etc/opt/csw/salt
filewatch-setup:
  cmd.script:
    - source: salt://saltminion/setup_service.sh
    - args: filewatch
salt-minion-setup:
  cmd.script:
    - source: salt://saltminion/setup_service.sh
    - args: salt-minion
filewatch:
  service.running:
    - enable: True
    - watch:
      - /etc/salt/minion.d/beacons.conf
{% endif %}
{% if grains['os_family'] == "RedHat" %}
salt-repo:
  pkg.removed
{% endif %}
{% if grains['os_family'] == "Debian" %}
python-pyinotify:
  pkg.installed
{% endif %}
salt-minion:
{% if grains['kernel'] == 'Linux' %}
  pkgrepo:
    - managed
    - humanname: SaltStack Repo
{%   if grains['os_family'] == "Debian" %}
    - name: deb http://repo.saltstack.com/apt/{{ lower_os_name }}/{{ release_ver }}/{{ grains['osarch'] }}/2016.11 {{ grains['lsb_distrib_codename'] }} main
    - dist: {{ grains['lsb_distrib_codename'] }}
    - key_url: https://repo.saltstack.com/apt/{{ lower_os_name }}/{{ release_ver }}/{{ grains['osarch'] }}/2016.11/SALTSTACK-GPG-KEY.pub
{%   elif grains['os_family'] == "RedHat" %}
    - name: salt-2016.11
    - baseurl: https://repo.saltstack.com/yum/redhat/{{ release_ver }}/$basearch/2016.11
    - gpgcheck: 1
    - gpgkey: http://repo.saltstack.com/yum/redhat/{{ release_ver }}/{{ grains['osarch'] }}/2016.11/SALTSTACK-GPG-KEY.pub
{%   endif %}
  pkg:
    - latest
{% endif %}
  service:
    - running
    - enable: True
    - watch:
      - file: /etc/salt/minion
      - file: /etc/salt/minion.d/beacons.conf
      - file: /etc/salt/pki/minion/master_sign.pub

/etc/salt/minion:
  file.managed:
    - source: salt://saltminion/minion.jinja
    - mode: 644
    - template: jinja

/etc/salt/minion.d/beacons.conf:
  file.managed:
    - source: salt://saltminion/beacons.conf.jinja
    - mode: 644
    - template: jinja

/etc/salt/pki/minion/master_sign.pub:
  file.managed:
    - source: salt://saltminion/{{ domain }}/master_sign.pub
    - mode: 644
