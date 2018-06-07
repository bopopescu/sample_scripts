Few Commands:

salt -G 'expostack:SCL1:staging_cluster' pillar.get expostack
salt  -G 'expostack:SCL1:staging_cluster' state.sls expostack/nova test=True
salt-ssh '*' -i mount.active --output json | tee /tmp/active_mount_expostack
