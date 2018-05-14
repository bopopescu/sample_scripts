#########################
## Script to check compute nodes and perform auto evacutaion of instances from faulty compute node
## Author: Suhaib Chishti
## Prerequisites: Make sure physical server console IP is updated to DNS. Format: servername-console.domain  e.g: bc7-b1-console.scl1.us.tribalfusion.net
##		 Install ipmitool & VMware vCenter API for fencing compute nodes
##		 Check Keystone, MYSQL VCenter & HP console credentials
##		 Preferably keyless authentication to compute nodes
##		 Hosts file and DNS is properly configured
##		 SNMP & snmp-mibs-downloader installed on all compute nodes
##		 Make sure necessary port are open
##		 Interface Names monitored: vlan132|vlan2048|pip|em|p1p|p2p (Please append the script to monitor other interfaces)
##               To ignore specfic compute nodes, add it to IGNORE_COMPUTE paramter seperated by "|" e.g: IGNORE_COMPUTE="bc4-b4|bc4-b3" (restart requiried)
## NOTE:         In case of shared storage append #nova evacuate with "--on-shared-storage"
########################



#!/bin/bash
export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_ID=default
export OS_PROJECT_NAME=admin
export OS_TENANT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=0penst@ck
export OS_AUTH_URL=http://controller:35357/v3
export OS_IDENTITY_API_VERSION=3
mysql_user="root"
mysql_password="H&perS0nic"
mysql=$(which mysql)

#To ignore specfic compute nodes e.g: IGNORE_COMPUTE="bc4-b4|bc4-b3" (restart requiried)
IGNORE_COMPUTE="bc8-b10|bc4-b6|vmexpostack-compute-05|vmexpostack-compute-06|vmexpostack-compute-07|c12-b5|bc4-b5|c11-b1|bc7-b3"


NodeStatus () {
###Check Node compute node power status
if [ `echo $1|grep ^vm|wc -l` -gt 0 ];
 then

BadNodePowerStatus=$(/usr/lib/vmware-vcli/apps/vm/vminfo.pl --url https://vcenter-01.scl1.us.tribalfusion.net:443/sdk/webService --username vrealize --password password powerstatus --vmname $1 | grep "IP Address" | grep "Not Known" | wc -l)

 else

BadNodePowerStatus=$(ipmitool -I lanplus -U root -H $2 -P changeme chassis power status | grep -w off | wc -l)

fi
}


NodeOff () {
#Fence the node using IPMI for physical node & using vCenter API for VMware instance
if [ `echo $1|grep ^vm|wc -l` -gt 0 ];
 then
  /usr/lib/vmware-vcli/apps/vm/vmcontrol.pl --url https://vcenter-01.scl1.us.tribalfusion.net:443/sdk/webService --username vrealize --password password --operation poweroff --vmname $1
  echo "`date` # -> Fencing compute node $1 for evacuation"

 else
  /usr/bin/ipmitool -I lanplus -U root -H $2 -P changeme chassis power off
  echo "`date` # -> Fencing compute node $2 for evacuation"

fi
}

#Fun_NewNode () {

#PossibleNodes=$(nova service-list --binary nova-compute | grep -w enabled | grep -w up | grep "$2" | grep -v "$1" | egrep -w -v "$IGNORE_COMPUTE" | awk '{print $6}')
#flag=0
#for z in $PossibleNodes
#do 
#   inst_counter=$(mysql expo_nova -u${mysql_user} -p${mysql_password} -e "select * FROM instances WHERE host = '$z' AND vm_state = 'active'\G;"| grep -w id | wc -l)
#   if [ $flag -eq 0 ]
#   then
#        flag=$((flag+1))
#        NewNode=$z
#        NewNodeInst=$(mysql expo_nova -u${mysql_user} -p${mysql_password} -e "select * FROM instances WHERE host = '$z' AND vm_state = 'active'\G;"| grep -w id | wc -l)
#   elif [ $flag -gt 0 ] && [ $inst_counter -lt $NewNodeInst ];
#   then
#        NewNodeInst=$inst_counter
#        NewNode=$z
#        flag=$((flag+1))
#   else
#        flag=$((flag+1))
#        continue;
#   fi
#done
#}


counter=0

while true; do
     sleep 15
     RenableComp=$(nova service-list --binary nova-compute | grep -w  up | grep disabled | egrep -w -v "$IGNORE_COMPUTE" | head -1 | awk -F '|' '{print $4}' | xargs)
     if [ -z "$RenableComp" ]
     then
          #No Disabled Compute Nodes
          echo "No Disabled Compute Nodes" >/dev/null 2>&1
     else
	  #Enable Compute Node which are UP
	  echo "`date` # -> Comupte service is up on $RenableComp"
	  echo "`date` # -> Re-Enabling compute node $RenableComp"
          nova-manage service enable --host=$RenableComp --service=nova-compute
          echo "As per config, Compute Nodes excluded from compute check script: $IGNORE_COMPUTE \n\n\n $(nova service-list --binary nova-compute)"|mail -s "Recovery- nova-compute service on $RenableComp" NOC@exponential.com
     fi

     BadNode=$(nova service-list --binary nova-compute | grep -v disabled | grep -w down | egrep -w -v "$IGNORE_COMPUTE" | head -1 | awk '{print $6}' | xargs)

     if [ -z "$BadNode" ]
     then
         	#No Faulty Compute Nodes

		#Checking for data interfaces on each compute
                ComupteNodes=$(nova service-list --binary nova-compute| grep -w enabled | grep -w up | egrep -w -v "$IGNORE_COMPUTE" | awk '{print $6}')
                for r in $ComupteNodes
                do 
                        Nic_Status=$(snmptable -v 2c -c 'public' $r IF-MIB::ifTable | egrep "vlan132|vlan2048|pip|em|p1p|p2p|Broadcom" | grep -w down | wc -l)
                        if [ $Nic_Status -eq 0 ]
                        then
                                continue;
                        elif [ $Nic_Status -gt 0 ] && [ $counter -eq 0 ]
                        then
                                #An interface found down on compute node
                                ssh $r "/sbin/ifconfig -a" |mail -s "Alert- Interface Down on compute node $r" NOC@exponential.com
                                counter=1
                        elif [ $Nic_Status -gt 0 ] && [ $counter -eq 100 ]
                        then
                                counter=0
                                break;
                        else 
                                counter=$((counter+1))
                                continue;
                        fi
                done
         	
		continue;


     elif [ `ping -c 30 $BadNode|grep from|grep icmp|wc -l` -gt 27 ] 
     then
                #Disable Compute Service on controller & send Alert Email to NOC  #Service Down Issue
                echo "`date` # -> Compute Node $BadNode has not checked in"
		echo "`date` # -> Compute Node $BadNode is pinging hence will try to restart compute service"
     		nova-manage service disable --host=$BadNode --service=nova-compute
     		echo "As per config, Compute Nodes excluded from compute check script: $IGNORE_COMPUTE \n\n\n $(nova service-list --binary nova-compute)"|mail -s "Alert- Check nova-compute service on $BadNode" NOC@exponential.com
		ssh $BadNode "service nova-compute start"
		continue;

      else
		sleep 50
     	 	NodeStatus $(host $BadNode|awk '{print $1}') $(host $BadNode-console|awk '{print $1}')
		if [ $BadNodePowerStatus -eq 0 ]
		then
			#Disable Compute Service on controller & send Alert Email to NOC  #Network Issue
			echo "`date` # -> Compute Node $BadNode has not checked in and is not pinging"
			echo "`date` # -> Power status of Compute Node $BadNode is ON hence this could be problem with networking"
			echo "`date` # -> Placing list of active VMs on $BadNode in file /tmp/instance-evac-list-$BadNode-$(date +"%b-%d-%y").txt" 
			mysql expo_nova -u${mysql_user} -p${mysql_password} -e "SELECT * FROM instances WHERE host = '$BadNode' AND vm_state = 'active'\G;" > "/tmp/instance-evac-list-$BadNode-`date +"%b-%d-%y"`.txt";
			echo "`date` # -> Disabling Compute Node $BadNode"
                	nova-manage service disable --host=$BadNode --service=nova-compute
                	echo "As per config, Compute Nodes excluded from compute check script: $IGNORE_COMPUTE \n\n\n $(nova service-list --binary nova-compute)"|mail -s "Alert- Network down on compute node $BadNode [Compute Service Down]" NOC@exponential.com
                	continue;
		else
               #AvailZone=$(nova service-list --binary nova-compute|grep $BadNode | egrep -w -v "$IGNORE_COMPUTE" | awk -F '|' '{print $5}'|xargs)
                #NewNode is compute node one with least number of instances
                #NewNode=$(mysql expo_nova -B  -u${mysql_user} -p${mysql_password} -e "SELECT  node FROM instances GROUP BY node ORDER BY COUNT(*) ASC;" | grep -v  -e "$BadNode" -e "NULL" -e "node" | head -1 | cut -d"." -f1)

                #Fence faulty compute to make sure its down & list instaces on that compute
		echo "`date` # -> Compute Node $BadNode has not checked in"
		echo "`date` # -> Compute Node $BadNode is not pinging and Power Status is OFF"
		echo "`date` # -> Compute Node $BadNode will be fenced and instances will be evacuated."
                mysql expo_nova -u${mysql_user} -p${mysql_password} -e "SELECT * FROM instances WHERE host = '$BadNode' AND vm_state = 'active'\G;" > "/tmp/instance-evac-list-$BadNode-`date +"%b-%d-%y"`.txt";
	        NodeOff $(host $BadNode|awk '{print $1}') $(host $BadNode-console|awk '{print $1}')
	        sleep 30
		#Disable Compute Service on controller
		echo "`date` # -> Disabling compute service on fenced Compute Node $BadNode"
                nova-manage service disable --host=$BadNode --service=nova-compute
     		echo "\n\n\n ######## Check under /tmp/instance-evac-list-$BadNode-$(date +"%b-%d-%y").txt for list of evacuated active instances"|mail -s "Alert- Powering off $BadNode & doing instance evacuation" NOC@exponential.com

                #Issue Evacuate of instances to healthy compute
                LeftInsts=$(mysql expo_nova -u${mysql_user} -p${mysql_password} -e "select * FROM instances WHERE host = '$BadNode' AND vm_state = 'active'\G;"| grep -w id | wc -l)

                if [ "$LeftInsts" -eq 0 ]
   	        then
                	echo "`date` # -> No VMs on this compute hence no instance evacuation"
		#exit 1;
		continue;
    	        else
                   	for k in $BadNode
		   	do
		      	       echo "`date` # -> Evacuating active instances on $k ...\n"
			  
			       service openstack_lease_mgmt stop
			       for j in $(mysql expo_nova -B -N -u${mysql_user} -p${mysql_password} -e "SELECT id FROM instances WHERE host = '$k' AND vm_state = 'active'";)
			       do
             		      	     #NewNode is compute node one with least number of instances
             		             #NewNode=$(mysql expo_nova -B  -u${mysql_user} -p${mysql_password} -e "SELECT  node FROM instances WHERE availability_zone = '$AvailZone' AND vm_state = 'active' GROUP BY node ORDER BY COUNT(*) ASC;" | grep -v  -e "$BadNode" -e "NULL" -e "node" | head -1 | cut -d"." -f1)
				  #Fun_NewNode "$BadNode" "$AvailZone"
			           NAME=$(mysql expo_nova -B -N -u${mysql_user} -p${mysql_password} -e "SELECT display_name FROM instances WHERE id = '$j'")
                                  #echo "Moving $NAME to $NewNode"
                                   echo "`date` # -> Evacuating $NAME .... "
 			          #nova evacuate $j $NewNode
 			          #nova evacuate $j 
 			     	   nova evacuate $j --on-shared-storage
				   sleep 15;
 			     	   #nova evacuate $j --on-shared-storage
 			     	   #nova evacuate $j $NewNode --on-shared-storage
                            	   #mysql expo_nova -u${mysql_user} -p${mysql_password} -e "UPDATE instances SET host = '$NewNode' WHERE id = '$j'"
			    	   #UUID=`mysql expo_nova -B -N -e "select uuid from instances where id = '$j'"`
  			     	   #nova reboot $UUID
       
             		       done

			       echo "`date` # -> Done with instance evacuation on $k"

			echo "Make sure all evacuated instances instances are up before starting this service \n\n $(service openstack_lease_mgmt status)"|mail -s "Please manually start Openstack Lease service on `hostname -f`" NOC@exponential.com
		   	done
	        fi
		fi
    #exit 2;
     continue;
     fi
done
