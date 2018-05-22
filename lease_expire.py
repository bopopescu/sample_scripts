#!/usr/bin/python
from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client
import pymysql
import json
import MySQLdb
import ipcalc
import novaclient.client
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
def notify(receiver,vmname,ipaddress,hours,whattodo):
    me = "expostack@mydomain.com"
    msg = MIMEMultipart('related')
    msgAlternative = MIMEMultipart('alternative')
    msg['From'] = me
    if receiver == "admin":
       receiver = "admin@mydomain.com"
    you = receiver
    msg['To'] = receiver
    msg.preamble = 'This is a multi-part message in MIME format.'
    ipaddress = socket.gethostbyname(socket.gethostname())
    text = "Hi!"

    if whattodo == "shutdown":
       if ipaddress  in ipcalc.Network('10.26.32.0/20'):
         msg['Subject'] = "Virtual Machine " + vmname + ".vpc.prod.scl1.us.mydomain.com" + " lease is expired and is shutdown"
         html1 = "<html><head></head><body><pre>VM Name  : " + vmname + ".vpc.prod.scl1.us.mydomain.com is expired and shutdown.<br><br>If you have any questions / issues to renew VM. Please open" +             " Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"
       else:
         msg['Subject'] = "Virtual Machine " + vmname + ".vpc.dev.scl1.us.mydomain.com" + " lease is expired and is shutdown"
         html1 = "<html><head></head><body><pre>VM Name  : " + vmname + ".vpc.dev.scl1.us.mydomain.com is expired and shutdown.<br><br>If you have any questions / issues to renew VM. Please open" +             " Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"

    if whattodo == "delete":
       if ipaddress  in ipcalc.Network('10.26.32.0/20'):
         msg['Subject'] = "Virtual Machine " + vmname + ".vpc.prod.scl1.us.mydomain.com" + " is deleted"
         html1 = "<html><head></head><body><pre>Vitual machine  : " + vmname + ".vpc.prod.scl1.us.mydomain.com is deleted. <br><br>If you have any" +         "questions / issues, Pease" +        " open Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"
       else:
         msg['Subject'] = "Virtual Machine " + vmname + ".vpc.dev.scl1.us.mydomain.com" + " is deleted"
         html1 = "<html><head></head><body><pre>Vitual machine  : " + vmname + ".vpc.dev.scl1.us.mydomain.com is deleted. <br><br>If you have any" +         "questions / issues, Pease" +        " open Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"

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

vm_archival_days = "7"
controller_ip = "10.29.16.01"
user_name = "user@mydomain.com"
passwordvpc = 'XXXXXXX'

db = MySQLdb.connect("localhost","root","XXXXXXX","expo_nova" )

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
    novac = novaclient.client.Client(2, session=sess)
    print "Checking under Domain " + domain_nameks + " " + project_name + " \n"

    def listservers():
        try:
          listofservers = novac.servers.list()
          flaglistserver=1;
        except :
             print "\tError \n"
             flaglistserver=0;
        if flaglistserver:
         cursor = db.cursor()
         for rowsa in listofservers:
             #print rowsa.name,rowsa.id,rowsa.status
             date_format='%Y-%m-%d %H:%M:%S'
             date = datetime.now(tz=pytz.utc)
             currentdate = datetime.strftime(date, date_format);
             #checkleasetime = "select created_on,leasedays,timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(created_on,INTERVAL leasedays DAY)),timestampdiff(MINUTE,'"+ currentdate +"'," +             "DATE_ADD(DATE_ADD(created_on,INTERVAL leasedays DAY), INTERVAL " + vm_archival_days + " DAY)) from lease_active_vms where hostname = '" + rowsa.name + "'"
             checkleasetime = "select created_on,leasedays, case requesttype when 'days' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(created_on,INTERVAL leasedays DAY)) " +                   "when 'hours'  then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(created_on,INTERVAL leasedays HOUR)) end as jordan," +                                                                 "case requesttype when 'days' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(DATE_ADD(created_on,INTERVAL leasedays DAY), INTERVAL " + vm_archival_days + " DAY))" +                 " when 'hours' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(DATE_ADD(created_on,INTERVAL leasedays HOUR), INTERVAL " + vm_archival_days + " DAY)) end as jordan23" +               ",requesttype,owner,ipaddress from lease_active_vms where hostname = '" + rowsa.name + "'"
             #print checkleasetime;
             cursor.execute(checkleasetime)
             resultlease = cursor.fetchall()
             for rowlease in resultlease:
                 vmcreatedon = rowlease[0]
                 vmleasetime = rowlease[1] * 24 * 60
                 vmarchivetime = rowlease[3]
	 	 ipaddress = rowlease[6]
                 print "\t" + rowsa.name + ipaddress + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(vmarchivetime)

                 if rowlease[2] <= 0:
                    if rowsa.status == "SHUTOFF":
                       a=""
                    else:
                       owner = rowlease[5]
                       print "\tShut down " + owner + " " + rowsa.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(vmarchivetime)
                       try:
                         novac.servers.stop(rowsa.id)
                       except :
                         print "\tError Shut down " + owner + " " + rowsa.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(vmarchivetime)
                                           
                       notify(owner,rowsa.name,ipaddress,rowlease[2],"shutdown")
                      #notify("suhaib.chishti@mydomain.com",rowsa.name,ipaddress,rowlease[2],"shutdown")
                       notify("cloudautomation@mydomain.com",rowsa.name,ipaddress,rowlease[2],"shutdown")
                       notify("NOC@mydomain.com",rowsa.name,ipaddress,rowlease[2],"shutdown")

                 if rowlease[3] <= 0:
                    owner = rowlease[5]
                    print "\tDelete VM " + rowsa.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(vmarchivetime)
                    novac.servers.delete(rowsa.id)
                    notify(owner,rowsa.name,ipaddress,rowlease[2],"delete")
                   #notify("suhaib.chishti@mydomain.com",rowsa.name,ipaddress,rowlease[2],"delete")
                    notify("cloudautomation@mydomain.com",rowsa.name,ipaddress,rowlease[2],"delete")
                    notify("NOC@mydomain.com",rowsa.name,ipaddress,rowlease[2],"delete")
 
    listservers()

db.close()
dbks.close()
