#!/usr/bin/python
from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client
from manilaclient import client as mclient
import pymysql
import json
import MySQLdb
import ipcalc
#import novaclient.client
#import cinderclient.client 
from datetime import datetime
from pytz import timezone
import pytz
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import re
import ConfigParser
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

filepath = '/usr/local/src/lease_expire/netapp-manageability-sdk-5.3/src/sample/Data_ONTAP/Python'
netapp_user = 'cinderapi'
netapp_passwd = 'netapp123'
netapp_url = 'fcl02-mgmt.scl1.us.mydomain.com'

def notify(receiver,sharename,shareid,project_name,hours,whattodo):
    me = "expostack@mydomain.com"
    msg = MIMEMultipart('related')
    msgAlternative = MIMEMultipart('alternative')
    msg['From'] = me
    if receiver == "admin":
       receiver = "admin@mydomain.com"
    you = receiver
    msg['To'] = receiver
    msg.preamble = 'This is a multi-part message in MIME format.'
  # ipaddress = socket.gethostbyname(socket.gethostname())
    text = "Hi!"


    if whattodo == "delete":
 #     if ipaddress  in ipcalc.Network('10.32.32.0/20'):
         msg['Subject'] = "Manila Share " + sharename + "(" + shareid + ")" + " in SCL region under project " + project_name + " has been deleted."
         html1 = "<html><head></head><body><pre>Share Name  : " + sharename + "(" + shareid + ")" + " in SCL region under project " + project_name + " is deleted.<br><br>If you have any" +         "questions / issues, Pease" +        " open Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"
 #     else:
 #       msg['Subject'] = "Manila Share " + sharename + ".vpc.dev.la1.us.mydomain.com" + " is deleted"
 #       html1 = "<html><head></head><body><pre>Vitual machine  : " + sharename + ".vpc.dev.la1.us.mydomain.com is deleted. <br><br>If you have any" +         "questions / issues, Pease" +        " open Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"

    if whattodo == "offline":
 #     if ipaddress  in ipcalc.Network('10.32.32.0/20'):
         msg['Subject'] = "Manila Share " + sharename + "(" + shareid + ")" + " in SCL region under project " + project_name + " lease has expired & is offline now."
         html1 = "<html><head></head><body><pre>Share Name  : " + sharename + "(" + shareid + ")" + " in SCL region under project " + project_name + " lease  has expired hence has been made offline, please renew if required.<br><br>For any questions / issues to renew share lease. Please open" +             " Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"
 #     else:
 #       msg['Subject'] = "Alert - Manila Share " + sharename + "(" + shareid + ")" + " in SCL1 region under project" + project_name + " lease  has expired, please renew if required."
 #       html1 = "<html><head></head><body><pre>Volume Name  : " + sharename + "(" + shareid + ")" + " in SCL1 region under project" + project_name + " lease  has expired, please renew if required.<br><br>For any questions / issues to renew Volume. Please open" +             " Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"

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

share_archival_days = "31"
controller_ip = "url.tf-net.mydomain.com"
user_name = "user@mydomain.com"
passwordvpc = 'XXXXXXXX'
VERSION = "2"

db = MySQLdb.connect("localhost","root","XXXXXXX","expo_manila" )

dbks = MySQLdb.connect("localhost","root","XXXXXXX","expo_keystone")
cursorks = dbks.cursor()

sqlks = "select c.name,d.name,c.id from project c,domain d where c.domain_id=d.id and d.name != 'heat' and c.name != 'service' and c.name!='demo' and d.name!='admin'";

cursorks.execute(sqlks)
resultsks = cursorks.fetchall()

for rowks in resultsks:
    project_nameks = rowks[0]
    domain_nameks = rowks[1]
    project_id = rowks[2]
    auth_url = 'http://'+controller_ip+':5000/v3/'
    username = user_name
    user_domain_name = domain_nameks
    project_name = project_nameks
    project_domain_name = domain_nameks
    password = passwordvpc
    auth = v3.Password(auth_url=auth_url,
                   username=username,
                   password=password,
                   project_domain_name=project_domain_name,
                   project_name=project_name,
                   user_domain_name=user_domain_name)
    sess = session.Session(auth=auth)
    keystone = client.Client(session=sess)
    sess = session.Session(auth=auth)
    try:
         manilac = mclient.Client(VERSION, session=sess)
         print "Checking under Domain " + domain_nameks + " " + project_name + " \n"
    except:
	 print "\n Note: Domain " + domain_nameks + " " + project_name + " is non expiry! \n "
	 continue

    def offline_share(netapp_name,manilaid,svmname):
	 umount_cmd = "python " + filepath + "/apitest.py -v "+svmname+ " " + netapp_url + " " + netapp_user + " " + netapp_passwd + " volume-unmount force true  volume-name " + netapp_name
	 offline_cmd = "python " + filepath + "/apitest.py -v "+svmname+ " " + netapp_url + " " + netapp_user + " " + netapp_passwd + " volume-offline name " + netapp_name
	 try:
	    os.system(umount_cmd)
	    os.system(offline_cmd)
	    return "success"
	 except:
            print "\tError trying to offline Share " + netapp_name + " " + manilaid 
	    return "failed"

    def listshares():
        try:
          listofshares = manilac.shares.list(search_opts={'all_tenants': 1,'project_id': project_id})
          flaglistserver=1;
        except :
             print "\tError \n"
             flaglistserver=0;
        if flaglistserver:
         cursor = db.cursor()
         for rowsa in listofshares:
             #print rowsa.name,rowsa.id,rowsa.status
             date_format='%Y-%m-%d %H:%M:%S'
             date = datetime.now(tz=pytz.utc)
             currentdate = datetime.strftime(date, date_format);
             #checkleasetime = "select created_on,leasedays,timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(created_on,INTERVAL leasedays DAY)),timestampdiff(MINUTE,'"+ currentdate +"'," +             "DATE_ADD(DATE_ADD(created_on,INTERVAL leasedays DAY), INTERVAL " + share_archival_days + " DAY)) from lease_active_vms where hostname = '" + rowsa.name + "'"
             checkleasetime = "select created_on,leasedays, case requesttype when 'days' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(created_on,INTERVAL leasedays DAY)) " +                   "when 'hours'  then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(created_on,INTERVAL leasedays HOUR)) end as jordan," +                                                                 "case requesttype when 'days' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(DATE_ADD(created_on,INTERVAL leasedays DAY), INTERVAL " + share_archival_days + " DAY))" +                 " when 'hours' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(DATE_ADD(created_on,INTERVAL leasedays HOUR), INTERVAL " + share_archival_days + " DAY)) end as jordan23" +               ",requesttype,owner,share_status from lease_active_shares where shareuuid = '" + rowsa.id + "'"
             #print checkleasetime;
             cursor.execute(checkleasetime)
             resultlease = cursor.fetchall()
             for rowlease in resultlease:
                 sharecreatedon = rowlease[0]
                 shareleasetime = rowlease[1] * 24 * 60
                 sharearchivetime = rowlease[3]
		 share_status = rowlease[6]
		 if "NFS" in str(rowsa.share_proto):
	         	netapp_name = str(rowsa.export_location.split("/")[1])
		 else:
	         	netapp_name = str(rowsa.export_location.split("\\")[3])
		
                 print "\t" + rowsa.name + " Age Alert/Delete (minutes) : " + str(rowlease[2]) + "/" + str(sharearchivetime)

                 if rowlease[2] <= 0:
		    if "online" not in share_status :  
                       continue
                    else:
                       owner = rowlease[5]
                       print "\tOffline " + owner + " " + rowsa.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(sharearchivetime)
		       getshare_type_id_cmd = "Select id from share_types where name='"+rowsa.share_type+"'"
                       cursortype = db.cursor()
                       cursortype.execute(getshare_type_id_cmd)
                       sharetypeid = cursortype.fetchall()
		       getsvm_name = "select spec_value from share_type_extra_specs where share_type_id='"+str(sharetypeid[0]).split("'")[1]+"' and spec_key='share_backend_name'"
		       cursortype.execute(getsvm_name)
		       configname = cursortype.fetchall()
		       config_name = str(configname[0]).split("'")[1]
		       configParser = ConfigParser.RawConfigParser()
		       configFilePath = r'/etc/manila/manila.conf'
		       configParser.read(configFilePath)
		       svm_name = configParser.get(config_name, 'netapp_vserver')
		       netapp_result = offline_share(netapp_name,rowsa.id,svm_name)
		       if "success" in netapp_result:
			   update_share_stat_cmd = "update lease_active_shares set share_status='offline', storage_name='"+netapp_name+"'  where shareuuid='"+rowsa.id+"'"	
			   cursortype.execute(update_share_stat_cmd)
			   db.commit()
			
                                           
                       notify(owner,rowsa.name,rowsa.id,project_name,rowlease[2],"offline")
                      #notify("suhaib.chishti@mydomain.com",rowsa.name,ipaddress,rowlease[2],"shutdown")
                       notify("cloudautomation@mydomain.com",rowsa.name,rowsa.id,project_name,rowlease[2],"offline")
			

                   #   try:
                        #manilac.shares.delete(rowsa.id)
                    #   notify(owner,rowsa.name,rowsa.id,project_name,rowlease[2],"alert")
                    #   notify("cloudautomation@mydomain.com",rowsa.name,rowsa.id,project_name,rowlease[2],"alert")
                    #   notify("noc@mydomain.com",rowsa.name,rowsa.id,rowlease[2],"alert")
                    #  except :
                    #    print "\tError Sending message " + owner + " " + rowsa.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(sharearchivetime)
                                           
                    #  notify(owner,rowsa.name,rowsa.id,project_name,rowlease[2],"alert")
                    #  notify("suhaib.chishti@mydomain.com",rowsa.name,rowsa.id,project_name,rowlease[2],"alert")
                    #  notify("cloudautomation@mydomain.com",rowsa.name,rowsa.id,project_name,rowlease[2],"alert")

                 if rowlease[3] <= 0:
                    owner = rowlease[5]
                    print "\tDelete Volume " + rowsa.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(sharearchivetime)
                    manilac.shares.delete(rowsa.id)
                    notify(owner,rowsa.name,rowsa.id,project_name,rowlease[2],"delete")
                   #notify("suhaib.chishti@mydomain.com",rowsa.name,ipaddress,rowlease[2],"delete")
                    notify("cloudautomation@mydomain.com",rowsa.name,rowsa.id,project_name,rowlease[2],"delete")
 
    listshares()

db.close()
dbks.close()
