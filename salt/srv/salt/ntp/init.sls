{% if grains['os_family'] == 'Solaris' or grains['os_family'] == 'Debian' %}
{%     set service_name = 'ntp' %}
{% elif grains['os_family'] == 'RedHat' %}
{%     set service_name = 'ntpd' %}
{% endif %}

ntp:
  service:
    - name: {{ service_name }}
    {% if grains['kernel'] == 'Linux' %}
    - running
    - watch:
      - file: /etc/ntp.conf
    {% elif grains['zonename'] == 'global' %}
    - running
    - watch:
      - file: /etc/inet/ntp.conf
    {% endif %}
  file.managed:
    {% if grains['os_family'] == 'Debian' %}
    - name: /etc/ntp.conf
    - source: salt://ntp/ntp.conf.debian.jinja
    {% elif grains['os_family'] == 'RedHat' %}
    - name: /etc/ntp.conf
    - source: salt://ntp/ntp.conf.redhat.jinja
    {% elif grains['zonename'] == 'global' %}
    - name: /etc/inet/ntp.conf
    - source: salt://ntp/ntp.conf.solaris.jinja
    {% endif %}
    - mode: 644
    - template: jinja
