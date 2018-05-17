## Script to clean VRRP ID of deleted k8s heat clusters
##
## Author: Suhaib Chishti
##
## Help: This script checks if k8s cluster heat stack (any of the 3 masters is running), if stack is deleted, it deletes corresponding vrrp_id from DB.
########################
import pymysql.cursors
import subprocess
from subprocess import call

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='k8s_user',
                             password='exposecret',
                             db='k8s',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
   #with connection.cursor() as cursor:
        # Create a new record
       #sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
       #cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

    # connection is not autocommit by default. So you must commit to save
    # your changes.
   #connection.commit()

    with connection.cursor() as cursor:
        # Read a single record
       #sql = "SELECT `vrrp_id`, `k8s_master_1`, `k8s_master_2`, `k8s_master_3`, FROM `vrrp` WHERE `k8s_master_1`!=%s"
        sql = "SELECT * FROM `vrrp` WHERE `k8s_master_1`!=''"
        cursor.execute(sql)
       #result = cursor.fetchone()
        result = cursor.fetchall()
       #print(result)
 	for i in range(len(result)):
	  #print result[i]
	   counter=0
	   for key, value in result[i].iteritems():
		   counter += 1
		   if (isinstance(value, int))	== True :
			id=value
			print (id)		
		   if (isinstance(value, basestring)) == True :
		    	print value
			try:
  			    subprocess.check_call(["host", value])
			    if "master-2" in value :
				print "Its VIP master"
				master2="UP"
			    if "master-1" in value :
				print "Its VIP 2nd priority"
				master1="UP"
			    if "master-3" in value :
				print "Its VIP 3rd priority"
				master3="UP"
			    if "k8s_master" not in value :
				print "Its not from k8s stack cluster"
				master1="UP"
				master2="UP"
				master3="UP"
			except subprocess.CalledProcessError:
			    if "master-2" in value :
                                print "Its VIP master"
                                master2="DOWN"
                            if "master-1" in value :
                                print "Its VIP 2nd priority"
                                master1="DOWN"
                            if "master-3" in value :
                                print "Its VIP 3rd priority"
                                master3="DOWN"
			    print "Command Failed"
		   if (len(result[i])) == counter :
			if ( master1 == "UP") or ( master2 == "UP" ) or ( master3 =="UP" ) :
		    	   print "Keep this VRRP ID"
			else:
			   print "Delete this VRRP ID"
			  #del_vrrp_id = "DELETE FROM `vrrp`  WHERE vrrp_id = '%s'" % (id,)
			   cursor.execute ("""
  			     UPDATE vrrp
   			     SET k8s_master_1=%s, k8s_master_2=%s, k8s_master_3=%s, submission_date=%s
 			      WHERE vrrp_id=%s
			    """, ('', '', '', '0000-00-00', id))
			  #cursor.execute(del_vrrp_id)
			   connection.commit()
finally:
    connection.close()
