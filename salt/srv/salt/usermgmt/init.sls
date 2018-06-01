#disable root login
{% from "usermgmt/map.jinja" import sshcfg with context %}
change sshd config:
    file.replace:
        - name: {{ sshcfg.config }}
        - pattern: ^PermitRootLogin yes
        - repl: PermitRootLogin no
        - backup: bak
        - append_if_not_found: True

{{ sshcfg.service }}:
    service.running:
        - enable: True
        - reload: True
        - watch:
            - file: {{ sshcfg.config }}

change root password:
    module.run:
        - name: shadow.set_password
        - m_name: root
        - password: {{ salt['shadow.gen_password'](salt['pillar.get']('root_secret')) }}
