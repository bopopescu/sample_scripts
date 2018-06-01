update configuration:
  cmd.state.sls:
    - tgt: {{ data['data']['id'] }}
    - arg:
        {% if data['data']['path'] == '/etc/resolv.conf' %}
          - resolve
        {% elif data['data']['path'] == '/etc/motd' %}
          - motd
        {% elif data['data']['path'] == '/etc/inet/ntp.conf' %}
          - ntp
        {% elif data['data']['path'] == '/etc/ntp.conf' %}
          - ntp
        {% endif %}
