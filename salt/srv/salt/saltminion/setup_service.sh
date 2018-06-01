#!/bin/bash
set -x
PATH=$PATH:/usr/sbin:/usr/bin:/bin:/sbin:/usr/local/bin
export PATH
SERVICE=$1
SPECDIR=/mnt/esmmonitor01/salt-minion/solaris-root/opt/lib/svc/manifest
STATUS=$(svcs -H ${SERVICE}| cut -d" " -f 1)
if [ "${STATUS}" != "online" ]; then
    if [ -n "${STATUS}" ]; then
        svcadm disable ${SERVICE} && svccfg delete ${SERVICE}
        if [ $? -ne 0 ]; then
            exit 1
        fi
    fi
    svccfg import ${SPECDIR}/${SERVICE}.xml
fi
