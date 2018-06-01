# create a user 'noc' and add sudo privileges to it
{% set domain_src = 'id' %}
{% if 'vpc' in grains[domain_src]: %}
{%   set domain = '.'.join(grains[domain_src].split('.')[2:]) %}
{% else %}
{%   set domain = '.'.join(grains[domain_src].split('.')[1:]) %}
{% endif %}
noc:
    group.present:
        - system: True

{% if 'prod' in domain %}
{%   if grains['kernel'] == 'Linux' %}
    user.present:
        - fullname: NOC user with Sudo privileges
        - shell: /bin/bash
        - password: $1$5q1DCwS/$CVP.tV0NVRHMqELonV0Iv/
        - groups:
            - noc
{%   elif grains['kernel'] == 'SunOS' %}
add user:
    cmd.run:
        - name:  '/usr/bin/id noc || /usr/sbin/useradd -G noc noc'
set password:
    module.run:
        - name: shadow.set_password
        - m_name: noc
        - password: $1$5q1DCwS/$CVP.tV0NVRHMqELonV0Iv/
{%   endif %}
{% endif %}
{% if grains['kernel'] == 'Linux' %}
{%   set sudoers_file = '/etc/sudoers' %}
{{ sudoers_file }}:
    file.append:
        - text: |
           Cmnd_Alias NOSU=!/usr/bin/su root, !/usr/bin/su -, !/usr/bin/su - root
           %noc        ALL=(ALL)       NOPASSWD: ALL, NOSU
{% endif %}
