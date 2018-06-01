#!/usr/bin/bash

# grain_builder version 2015031700
# a script that will populate the /etc/salt/grains file for Solaris minions
export PATH=/usr/sbin:$PATH

# verify Solaris 10
if [[ $(uname -rs) != "SunOS 5.10" ]]
  then
    echo "Not a Solaris 10 OS"
    exit 1
fi

# setup target file and get zonename
file="/etc/salt/grains"
name=$(zonename)

# collect zonelist, if a zone_host, if not you're a local_zone
if [ $name == "global" ]
  then
    list=$(zoneadm list -cp | grep -v ^0:global: | cut -d: -f2,3 | tr ':' '/')
    role=zone_host
  else
    role=local_zone
fi

# start building the custom grains file
echo "
roles:
  - $role
zonename: $name" > $file

# setup an exit message, make it nice for the people
msg="$(cat /etc/salt/minion_id) custom grains file built"

# if we're a local_zone, exit
if [ $name != "global" ]
  then
    echo $msg
    exit
fi

# otherwise build the zonelist section, if local zones are hosted, exit if not
if [ -z "$list" ]
  then
    echo "zonelist: none" >> $file
    echo $msg
    exit
  else
    echo "zonelist:" >> $file
fi

# add all the local_zones available
for zone in `echo $list`
  do
    echo "  - $zone" >> $file
done

echo $msg
exit
# vmsalt-head-master:/srv/salt/gbuilder/grain_builder.bash
