disable web:
  local.cmd.run:
     - tgt: {{ data['id'] }}
     - arg:
     {% if tag.split('/')[-1] == 'down' %}
          - 'relayctl host disable {{ data['address'] }}'
     {% else %}
          - 'relayctl host enable {{ data['address'] }}'
     {% endif %}
