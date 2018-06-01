#!/bin/bash

count=0

source /root/admin-openrc.sh

glance_path=$(cat /etc/glance/glance-api.conf |grep filesystem_store_datadir |grep -v "#"|cut -d "=" -f2|sed 's/ //g')
backupImages="backupImages"
backup_folder="$glance_path$backupImages"
size=$(df -h /var/lib/glance | awk 'FNR == 2{print $5}'|cut -d '%' -f1)

image_id=$(nova show "$1"|grep -i image|cut -d '(' -f2|awk '{print $1}'|cut -d ')' -f1|cut -d '|' -f1)

if [ $size -lt 91 ]
then
	echo " "
	echo "Making copy of image: $image_id"
	echo " "
	if [ -d $backup_folder ]
	then
        	cp -p  $glance_path/$image_id $backup_folder
        	if [ $? -eq 0 ]
        	then
                	echo "Back up of $image_id is made at $backup_folder"
        	else
                	echo "Back up failed: $image_id"
        	fi
	else
        	mkdir $backup_folder
        	cp -p  $glance_path/$image_id $backup_folder
        	if [ $? -eq 0 ]
        	then
                	echo "Back up of $image_id is made at $backup_folder"
       	 	else
                	echo "Back up failed: $image_id"
        	fi
	fi

else
	echo " " 
	echo "Remaining space on /var/lib/glance is lesser than 10%"
	echo " "
	df -h /var/lib/glance
	echo " "
	echo "Do you wanna continue taking a backup of image of instance ? "
	echo " " 
	echo "Press Y for Yes, N for No "
	read input
	if [ $input == "Y" ]
	then
		if [ -d $backup_folder ]
        	then
                	cp -p  $glance_path/$image_id $backup_folder
                	if [ $? -eq 0 ]
                	then
                        	echo "Back up of $image_id is made at $backup_folder"
                	else
                        	echo "Back up failed: $image_id"
                	fi
        	else
                	mkdir $backup_folder
                	cp -p  $glance_path/$image_id $backup_folder
                	if [ $? -eq 0 ]
                	then
                        	echo "Back up of $image_id is made at $backup_folder"
                	else
                        	echo "Back up failed: $image_id"
                	fi
        	fi
	else
			if [ $input == "N" ]
			then
				echo "Not taking backup of image as per user choice .... "
			else
				echo "Invalid input: $input"
				echo "Please enter only single alphabet: Y for Yes, N for No"
				echo "Exiting from script, please try again .... "
				exit 1
			fi
	fi

fi
		

openstack project list|awk -F '|' '{print $2,$3}'|grep -vi name|grep '^..'|grep -v '-' > project.list

echo " "
echo "Fetching Project lists ...... "
echo " "

echo "Please choose project for defining visiblity of image to be created .... "
echo " "
echo "Note: To choose multiple projects, use number separated by commans ... "
echo " "
echo "For example: For choosing single project like first project, enter 1 ...."
echo " "
echo "For choosing multiple projects, like first three, enter 1,2,3 ....."
echo " "

while read line
do
	count=$(($count+1))
	echo "$count: $line"
done<project.list

echo " "

echo "Enter your choice: "
read choice

test=$(echo $choice|tr -d "[:digit:]|,")

if [ -z $test ]
then
	echo " "
else
	echo "Illegal user input: $choice"
	echo "Please make sure, input is only numbers separated by commas .... "
	echo "Try again ..... "
	echo "Exiting from script ..... "
	exit 1
fi

##echo $choice|grep -v ###

user=$(whoami)

        if [ "$user" == "root" ]
        then
                if [ -r "/var/tmp/mynamerc_$3.sh" ]
                then
                        #source /root/admin-openrc.sh
			source "/var/tmp/mynamerc_$3.sh"
                        if [ $? -eq 0 ]
                        then
				rm -f "/var/tmp/mynamerc_$3.sh"
                                instancename=$(nova list --all_tenants|grep $1 | cut -d '|' -f3)
				nova list --all_tenants| grep $1 | grep -i running
				if [ $? -eq 0 ]
				then
                                	nova stop $1
					sleep 30
				else
					nova list --all_tenants | grep $1 | grep -i shutdown
					if [ $? -eq 0 ]
					then
						echo "Instance ID: $1 - Status: Shutdown"
					else
						echo "$1 status is neither shutdown nor running .... "
						echo "Please verify the status of server manually .... "
						echo "Exiting from script ..... "
						exit 1
					fi
				fi

				nova list --all_tenants| grep $1 | grep -i shutdown
                                	if [ $? -eq 0 ]
                                	then
                                        	echo "$1 has been shutdown"
						underscore=$(echo "$2"|sed -e 's/ /_/g')
						variable=".img"
                                        	nova image-create --poll $1 "$underscore$variable"
                                        	if [ $? -eq 0 ]
                                        	then
                                                	#echo "Image created: '$2.img'"
							echo "Image created: '$underscore$variable'"
                                        	else
                                                	#echo "Image creation Failed: '$2.img'"
							echo "Image creation Failed: '$underscore$variable'"
                                                	echo "Exiting from script ..... "
                                                	exit 1
                                        	fi

                                        	image_id=$(nova image-list | grep "$underscore$variable" | cut -d '|' -f2| cut -d ' ' -f2)
                                        	#glance image-download --file snapshot.raw $image_id

                                        	#if [ $? -eq 0 ]
                                        	#then
                                        	#        echo "Image downloaded: $image_id"
                                        	#else
                                        	#        echo "Image download failed: $image_id"
                                        	#        echo "Exiting from script ..... "
                                        	#        exit 1
                                        	#fi

						#echo "Command: qemu-img convert -c -p -O qcow2 /var/lib/glance/images/$image_id '$underscore$variable'"  #'$2.img'	
                                        	#qemu-img convert -c -p -O qcow2 /var/lib/glance/images/$image_id "$underscore$variable"

						echo "Command: qemu-img convert -c -p -O qcow2 $glance_path$image_id '$underscore$variable'"  #'$2.img'
						qemu-img convert -c -p -O qcow2 $glance_path$image_id "$underscore$variable"


                                        	if [ $? -eq 0 ]
                                        	then
                                                	echo "Snapshot successfully compressed"
                                        	else
                                                	echo "Failed: Snapshot compresseion failed"
							glance image-delete $image_id
                                                	echo "Exiting from script ..... "
                                                	exit 1
                                        	fi
						
						non_underscore=$(echo "$underscore"|sed -e 's/_/ /g')
						
						current_dir=$(pwd)
                                        	glance image-create --name "$non_underscore" --disk-format qcow2  --container-format bare --file "$underscore$variable" 
                                        	if [ $? -eq 0 ]
                                        	then
                                                	glance image-list|grep "$2"
                                                	if [ $? -eq 0 ]
                                                	then
                                                        	echo "Image successfully uploaded: '$2'"
								glance image-delete $image_id
                                                        	if [ $? -eq 0 ]
                                                        	then
                                                                	echo "Temporary snapshot removed: $image_id"
									echo "Restarting your server: $1"
									nova start $1
									#rm -rf $current_dir/'$2.qcow2'
									variable2=".qcow2"
									rm -rf $current_dir/$underscore$variable2
                                                        	else
                                                                	echo "Failed: Snapshot removal failed"
                                                                	echo "Please try to remove manually"
                                                        	fi
                                                	else
                                                        	echo "Failed: Image upload failed"
								glance image-delete $image_id
                                                        	echo "Exiting from script ..... "
                                                        	exit 1
                                                	fi
							#Put your new code here to update image visiblity
							p="p"

							imageID=$(glance image-list|grep "$2"|awk '{print $2}')

							echo "Changing visiblity of image to Private"

							echo " "

							echo "Further changing visiblity of image as per project specified ......"	

							len=$(cat project.list|wc -l)
							sum=$((len+1))

							for i in $(echo $choice | sed "s/,/ /g")
							do
								if [ $i -lt $sum ]
								then
									echo " " 	
									var=$i$p
                                                                	project_id=$(sed -n "$var" project.list|awk '{print $1}')
									echo "----------------------------------------------------------------------------------------------------------------"	
									echo "Changing visiblity of image: $imageID to Project: $project_id"
									echo "----------------------------------------------------------------------------------------------------------------"
                                                                	glance image-update $imageID --visibility private;
                                                                	glance member-create $imageID $project_id;
                                                                	glance member-update $imageID $project_id accepted;
									echo "  "
								else
									echo "Invalid choice: $i"
									echo "Chosen number doesn't have associated Project"
									echo "Ignoring invalid choice .... "
								fi
							done
							glance member-list --image-id $imageID;
							rm $current_dir/$2$variable
							rm $current_dir/project.list

                                        	else
                                                	echo "Failed: Image upload failed"
							glance image-delete $image_id
                                                	echo "Exiting from script ..... "
                                                	exit 1
                                        	fi
                                	else
                                        	echo "Failed: Instance shutdown failed"
                                        	echo "Exiting from script ..... "
                                        	exit 1
                                	fi
                        	else
                                	echo "Failed: Credential validation failed"
                                	echo "Exiting from script ..... "
                                	exit 1
                        	fi

                	else
                        	echo "File: /root/admin-openrc.sh is not readble"
                        	echo "Exiting from script ..... "
                        	exit 1
                	fi

        	else
                	echo "Sudo failed, Please retry ... "
                	echo "Exiting from script ..... "
                	exit 1
        	fi
