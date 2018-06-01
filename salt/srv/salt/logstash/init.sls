{% from "logstash/maps.jinja" import logstashclient %}
logstashclient:
    cmd.run:
        - name: {{ logstashclient.script }} 
        - cwd: /
