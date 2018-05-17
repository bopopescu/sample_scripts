#!/usr/bin/python
from keystoneauth1.identity import v3
from keystoneauth1 import session
from saharaclient.api import client as sahara_client
#from keystoneclient.auth.identity import v3
#from keystoneclient import session
from keystoneclient.v3 import client
import pymysql
import json
import MySQLdb
import ipcalc
from datetime import datetime
from pytz import timezone
import pytz
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os

os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
def notify(receiver,vmname,vmname_id,hours,whattodo):
    me = "expostack@mydomain.com"
    msg = MIMEMultipart('related')
    msgAlternative = MIMEMultipart('alternative')
    msg['From'] = me
    if receiver == "admin":
       receiver = "admin@mydomain.com"
    you = receiver
    msg['To'] = receiver
    msg.preamble = 'This is a multi-part message in MIME format.'
    text = "Hi!"

    if whattodo == "shutdown":
         msg['Subject'] = "Sahara Cluster: " + vmname + " lease is expired and is shutdown"
         html1 = "<html><head></head><body><pre>Sahara Cluster: " + vmname + "<br><br>If you have any questions / issues to renew cluster. Please open Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"

    if whattodo == "delete":
         msg['Subject'] = "Sahara Cluster:" + vmname + " is deleted"
         html1 = "<html><head></head><body><pre>Sahara Cluster  : " + vmname + " is deleted. <br><br>If you have any questions / issues, Please open Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"

    htmlfinal = []
    htmlb = ''.join(htmlfinal)
    html = ''.join(str(x) for x in (html1,htmlb))
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(msgAlternative)
    msgAlternative.attach(part1)
    msgAlternative.attach(part2)
    s = smtplib.SMTP('mail.mydomain.com')
    s.sendmail(me, you, msg.as_string())
    s.quit()

user_name = "newuser@mydomain.com"
passwordvpc = 'XXXXXXXX'
AUTH_URL = 'http://10.29.16.203:5000/v3'
PROJECT_ID= 'Engineering Development'
project_name = 'Engineering Development'
user_domain_name = 'exponential'
project_domain_name = 'exponential'
project_id = '5e13d215ccdc492d889e0a7ef19078c5'
cluster_archival_days = "7"
controller_ip = "10.29.16.253"

db = MySQLdb.connect("localhost","root","XXXXXXXXXX","expo_sahara" )

dbks = MySQLdb.connect("localhost","root","XXXXXXXXX","expo_keystone")
cursorks = dbks.cursor()

sqlks = "select c.name,d.name,c.id from project c,domain d where c.domain_id=d.id and d.name != 'heat' and c.name != 'service' and c.name!='demo' and d.name!='admin'";

cursorks.execute(sqlks)
resultsks = cursorks.fetchall()

for rowks in resultsks:
    project_nameks = rowks[0]
    domain_nameks = rowks[1]
    project_id = rowks[2]
    auth_url = 'http://'+controller_ip+':5000/v3'
    username = user_name
    user_domain_name = domain_nameks
    project_name = project_nameks
    project_domain_name = domain_nameks
    password = passwordvpc
    #print "++++++++++++++++++++++++++++++++++++"
    #print auth_url
    #print username
    #print password
    #print project_domain_name
    #print project_name
    #print user_domain_name 
    #print project_id


    auth = v3.Password(auth_url=auth_url,
                   username=username,
                   password=password,
                   project_domain_name=project_domain_name,
                   project_name=project_name,
                   user_domain_name=user_domain_name,project_id=project_id)

    ses = session.Session(auth=auth)
    try:
        sahara_client_obj = sahara_client.Client('1.1', session=ses,service_type="data-processing",service_name="expo_sahara",project_id=project_id)
        print "Checking under Domain " + domain_nameks + " " + project_name + " \n"
    except:
	continue

    def listclusters():
	try:
            cluster_object=sahara_client_obj.clusters.list()
	    flaglistserver=1;
	except:
	    print "\tError \n"
            flaglistserver=0;

	if flaglistserver:
	    cursor = db.cursor()
            for cluster in cluster_object:
            	#print cluster.name
            	#print cluster.id 
            	#print '\n' 
	    	#for rowsa in listofvolumes:
             	#print rowsa.name,rowsa.id,rowsa.status
            	date_format='%Y-%m-%d %H:%M:%S'
            	date = datetime.now(tz=pytz.utc)
            	currentdate = datetime.strftime(date, date_format);
            	checkleasetime = "select created_on,leasedays, case requesttype when 'days' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(created_on,INTERVAL leasedays DAY)) " +                   "when 'hours'  then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(created_on,INTERVAL leasedays HOUR)) end as jordan," +                                                                 "case requesttype when 'days' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(DATE_ADD(created_on,INTERVAL leasedays DAY), INTERVAL " + cluster_archival_days + " DAY))" +                 " when 'hours' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(DATE_ADD(created_on,INTERVAL leasedays HOUR), INTERVAL " + cluster_archival_days + " DAY)) end as jordan23" +               ",requesttype,owner from lease_active_clusters where Cluster_id = '" + cluster.id + "'"
            	#print checkleasetime;
            	cursor.execute(checkleasetime)
            	resultlease = cursor.fetchall()
	    	#print resultlease
            	for rowlease in resultlease:
                	cluster_createdon = rowlease[0]
                	cluster_leasetime = rowlease[1] * 24 * 60
                	cluster_archivetime = rowlease[3]
                	print "\t" + cluster.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(cluster_archivetime)

			if rowlease[2] <= 0:
                       		owner = rowlease[5]
                       		print "\tAlert user " + owner + " " + cluster.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(cluster_archivetime)
                       		continue

                	if rowlease[3] <= 0:
                    		owner = rowlease[5]
                    		print "\tDelete Cluster " + cluster.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(cluster_archivetime)
		    		sahara_client_obj.clusters.delete(cluster.id)
                    		notify(owner,cluster.name,cluster.id,rowlease[2],"delete")
                    		#notify("samir.chowdhary@mydomain.com",cluster.name,rowlease[2],"delete")
                    		notify("cloudautomation@mydomain.com",cluster.name,cluster.id,rowlease[2],"shutdown")

    listclusters()

db.close()
dbks.close()
