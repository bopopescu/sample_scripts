nameservers:
    - 204.11.108.93
    - 204.11.108.92
ntpservers:
    - 204.11.108.93
    - 204.11.108.92
masters:
    - 10.29.1.24
    - 10.29.1.28
esmshare:
    dev.scl1.us.tribalfusion.net: /mnt/svmdev01expoesmmonitor01
    dev.la1.us.tribalfusion.net: /mnt/svmdr01expoesmmonitor01
    prod.scl1.us.tribalfusion.net: /mnt/svmprod01expoesmmonitor01
    prod.la1.us.tribalfusion.net: /mnt/svmdr01expoesmmonitor01
domain_master:
    dev.scl1.us.tribalfusion.net:
        - 10.29.1.24
        - 10.29.1.28
    prod.scl1.us.tribalfusion.net:
        - 10.26.1.79
        - 10.26.1.80
    dev.la1.us.tribalfusion.net:
        - 10.31.0.41
        - 10.31.0.42
    prod.la1.us.tribalfusion.net:
        - 10.30.10.11
        - 10.30.10.13
root_secret: root456


# vmsalt-head-master:/srv/pillar/data.sls
