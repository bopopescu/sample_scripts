#!/usr/bin/python
from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client
from cinderclient import client as cclient
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
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
def notify(receiver,volname,volid,hours,whattodo):
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

  # if whattodo == "shutdown":
  #    if ipaddress  in ipcalc.Network('10.32.32.0/20'):
  #      msg['Subject'] = "Cinder Volume " + vmname + ".vpc.prod.la1.us.mydomain.com" + " lease is expired and is shutdown"
  #      html1 = "<html><head></head><body><pre>Volume Name  : " + vmname + ".vpc.prod.la1.us.mydomain.com is expired and shutdown.<br><br>If you have any questions / issues to renew Volume. Please open" +             " Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"
  #    else:
  #      msg['Subject'] = "Cinder Volume " + vmname + ".vpc.dev.la1.us.mydomain.com" + " lease is expired and is shutdown"
  #      html1 = "<html><head></head><body><pre>Volume Name  : " + vmname + ".vpc.dev.la1.us.mydomain.com is expired and shutdown.<br><br>If you have any questions / issues to renew Volume. Please open" +             " Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"

    if whattodo == "delete":
  #    if ipaddress  in ipcalc.Network('10.32.32.0/20'):
         msg['Subject'] = "Cinder Volume " + volname + "(" + volid + ")" + " in SCL region under project " + project_name + " has been deleted."
         html1 = "<html><head></head><body><pre>Volume Name  : " + volname + "(" + volid + ")" + " in SCL region under project " + project_name + " is deleted.<br><br>If you have any" +         "questions / issues, Pease" +        " open Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"
  #    else:
  #      msg['Subject'] = "Cinder Volume " + vmname + ".vpc.dev.la1.us.mydomain.com" + " is deleted"
  #      html1 = "<html><head></head><body><pre>Vitual machine  : " + vmname + ".vpc.dev.la1.us.mydomain.com is deleted. <br><br>If you have any" +         "questions / issues, Pease" +        " open Helpdesk Ticket to noc@mydomain.com.<br><br>Regards,<br>Expostack Administrator</pre>"

    htmlfinal = []
    htmlb = ''.join(htmlfinal)
    html = ''.join(str(x) for x in (html1,htmlb))
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(msgAlternative)
    msgAlternative.attach(part1)
    msgAlternative.attach(part2)
    s = smtplib.SMTP('mail.mydomain')
    s.sendmail(me, you, msg.as_string())
    s.quit()

vol_archival_days = "31"
controller_ip = "url.tf-net.mydomain"
user_name = "user@mydomain.com"
passwordvpc = 'XXXXXXX'

db = MySQLdb.connect("localhost","root","XXXXXXX","expo_cinder" )

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
    cinderc = cclient.Client(2, session=sess)
    print "Checking under Domain " + domain_nameks + " " + project_name + " \n"

    def listvolumes():
        try:
          listofvolumes = cinderc.volumes.list(search_opts={'all_tenants': 1,'project_id': project_id})
          flaglistserver=1;
        except :
             print "\tError \n"
             flaglistserver=0;
        if flaglistserver:
         cursor = db.cursor()
         for rowsa in listofvolumes:
             #print rowsa.name,rowsa.id,rowsa.status
             date_format='%Y-%m-%d %H:%M:%S'
             date = datetime.now(tz=pytz.utc)
             currentdate = datetime.strftime(date, date_format);
             #checkleasetime = "select created_on,leasedays,timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(created_on,INTERVAL leasedays DAY)),timestampdiff(MINUTE,'"+ currentdate +"'," +             "DATE_ADD(DATE_ADD(created_on,INTERVAL leasedays DAY), INTERVAL " + vol_archival_days + " DAY)) from lease_active_vms where hostname = '" + rowsa.name + "'"
             checkleasetime = "select created_on,leasedays, case requesttype when 'days' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(created_on,INTERVAL leasedays DAY)) " +                   "when 'hours'  then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(created_on,INTERVAL leasedays HOUR)) end as jordan," +                                                                 "case requesttype when 'days' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(DATE_ADD(created_on,INTERVAL leasedays DAY), INTERVAL " + vol_archival_days + " DAY))" +                 " when 'hours' then timestampdiff(MINUTE,'"+ currentdate +"',DATE_ADD(DATE_ADD(created_on,INTERVAL leasedays HOUR), INTERVAL " + vol_archival_days + " DAY)) end as jordan23" +               ",requesttype,owner from lease_active_volumes where voluuid = '" + rowsa.id + "'"
             #print checkleasetime;
             cursor.execute(checkleasetime)
             resultlease = cursor.fetchall()
             for rowlease in resultlease:
                 volcreatedon = rowlease[0]
                 volleasetime = rowlease[1] * 24 * 60
                 volarchivetime = rowlease[3]
                 print "\t" + rowsa.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(volarchivetime)

                 if rowlease[2] <= 0:
                       owner = rowlease[5]
                       print "\tAlert user " + owner + " " + rowsa.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(volarchivetime)
		       continue
            #          try:
                        #cinderc.volumes.delete(rowsa.id)
                       #notify(owner,rowsa.name,rowsa.id,rowlease[2],"Volume lease expiry Alert")
                       #notify("cloudautomation@mydomain.com",rowsa.name,rowsa.id,rowlease[2],"Volume lease expiry Alert")
                       #notify("noc@mydomain.com",rowsa.name,rowsa.id,rowlease[2],"Volume lease expiry Alert")
            #          except :
            #            print "\tError Sending message " + owner + " " + rowsa.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(volarchivetime)
                                           
                      #notify(owner,rowsa.name,rowsa.id,rowlease[2],"shutdown")
                      #notify("suhaib.chishti@mydomain.com",rowsa.name,rowsa.id,rowlease[2],"shutdown")
                      #notify("cloudautomation@mydomain.com",rowsa.name,rowsa.id,rowlease[2],"shutdown")

                 if rowlease[3] <= 0:
                    owner = rowlease[5]
                    print "\tDelete Volume " + rowsa.name + " Age Shut/Delete (minutes) : " + str(rowlease[2]) + "/" + str(volarchivetime)
                    try:
                       cinderc.volumes.delete(rowsa.id)
                       notify(owner,rowsa.name,rowsa.id,rowlease[2],"delete")
                       #notify("suhaib.chishti@mydomain.com",rowsa.name,ipaddress,rowlease[2],"delete")
                       notify("cloudautomation@mydomain.com",rowsa.name,rowsa.id,rowlease[2],"delete")
		    except:
		       print "Note: Cannot delete Volume " + rowsa.name + " as it's not in available state."
 
    listvolumes()

db.close()
dbks.close()
