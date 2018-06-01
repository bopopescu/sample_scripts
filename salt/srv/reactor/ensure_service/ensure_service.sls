ensure service:
  cmd.state.sls:
    - tgt: {{ data['data']['id'] }}
    - arg:
          - service
    - kwarg:
        pillar:
        {% for key in data['data'].keys() %}
        {%   if 'running' in data['data'][key] %}
            service: {{ key }}
        {%   endif %}
        {%   endfor %}
