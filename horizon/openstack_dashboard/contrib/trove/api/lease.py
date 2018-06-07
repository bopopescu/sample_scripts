# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 OpenStack Foundation
# Copyright 2012 Nebula, Inc.
# Copyright (c) 2012 X.commerce, a business unit of eBay Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import

import logging

from django.conf import settings
from django.utils.functional import cached_property  # noqa
from django.utils.translation import ugettext_lazy as _
import six
import pymysql
import json
from datetime import datetime
from pytz import timezone
import pytz

import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def notify(receiver, vmname, flavor, whattodo,ipaddressa,submitter):
    me = "expostack@exponential.com"
    msg = MIMEMultipart('related')
    msgAlternative = MIMEMultipart('alternative')
    receiversplit = receiver.split("@")
    if len(receiversplit)==2:
       aaaa=""
    else:
       receiver = "cloudautomation@exponential.com"
    msg['From'] = me
    you = receiver;
    msg['To'] = receiver;
    msg.preamble = 'This is a multi-part message in MIME format.'
    text = "Hi!"
    font = "<font face=verdana size=2>"
    if whattodo == "createrequeststart":
       msg['Subject'] = "Your request for virtual Machine " + vmname + "" + " is submitted"
       html1 = "<html><head></head><body>" + font + "<b>VM Name  : </b>" + vmname + "<br><b>Flavor : </b>" + flavor + "<br><br> <b>Thanks and Regards</b><br>Expostack Administrator"

    if whattodo == "deleterequeststart":
       msg['Subject'] = "Your request for virtual Machine " + vmname + "" + " destroy has been submitted"
       html1 = "<html><head></head><body>" + font + "<b>VM Name  : </b>" + vmname + "<br><b>Submitted By</b> :" + submitter + "<br><b> Thanks and Regards</b><br>Expostack Administrator"

    htmlfinal = []
    htmlb = ''.join(htmlfinal)
    html = ''.join(str(x) for x in (html1,htmlb))
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(msgAlternative)
    msgAlternative.attach(part1)
    msgAlternative.attach(part2)
    s = smtplib.SMTP('mail.tribalfusion.com')
    s.sendmail(me, you, msg.as_string())
    s.quit()

def lease_project_verify(tenant_id, controllername):

    db = pymysql.connect(host=controllername, port=3306, user='expostack', passwd='BSoniC', db='expo_keystone')
    cursor = db.cursor()
    cursor.execute("select d.local_id, e.name, f.name from assignment c, id_mapping d, project e, role f where c.actor_id=d.public_id and d.local_id='vpc.leaseadmin@exponential.com' and c.target_id=e.id and e.id='" + tenant_id + "' and c.role_id=f.id and f.name='admin'")
    if cursor.rowcount == 0:
       return False
    else:
       return True

def check_instance_owner(controllername, instancename):
    db = pymysql.connect(host=controllername, port=3306, user='expostack', passwd='BSoniC', db='expo_nova')
    cursor = db.cursor()
    sql = "select owner from lease_active_vms where hostname='" + instancename + "'"
    cursor.execute(sql)
    resultnew = cursor.fetchall()
    for rows in resultnew:
        owner = rows[0]
        return owner

def check_instance_lease(controllername, instancename , instancetenantid):
    db = pymysql.connect(host=controllername, port=3306, user='expostack', passwd='BSoniC', db='expo_nova')
    cursor = db.cursor()
    date_formatv='%Y-%m-%d %H:%M:%S'
    datev = datetime.now(tz=pytz.utc)
    currentdatev = datetime.strftime(datev, date_formatv);
    sql = "select case requesttype when 'days' then DATE_ADD(created_on,INTERVAL leasedays DAY) when 'hours' then DATE_ADD(created_on,INTERVAL leasedays HOUR) end as leasehowmuch ,case requesttype when 'days' then timestampdiff(MINUTE,'"+ currentdatev +"',DATE_ADD(created_on,INTERVAL leasedays DAY)) " +                   "when 'hours'  then timestampdiff(MINUTE,'"+ currentdatev +"',DATE_ADD(created_on,INTERVAL leasedays HOUR)) end as jordan from lease_active_vms where hostname='" + instancename + "'"
    cursor.execute(sql)
    resultnew = cursor.fetchall()
    for rows in resultnew:
        if rows[1] < 0:
           leaseexpire = "Expired";
        else:
           leaseexpire = rows[0]
        if lease_project_verify(instancetenantid, controllername) == False:
           leaseexpire = "Never"
        return leaseexpire

#api.lease.create_lease_record(controllername, name, lease_days_pass, request.user.username, flavor_name.name)
def create_lease_record(controllername ,instancename, lease_days, owner, flavor):
    db = pymysql.connect(host=controllername, port=3306, user='expostack', passwd='BSoniC', db='expo_nova')
    cursor = db.cursor()
    lease_days_pass = str(lease_days)
    generatetime1 = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    generatetime = str(generatetime1)
    checkexist = "select * from lease_active_vms where hostname='" + instancename + "'"
    cursor.execute(checkexist)
    if cursor.rowcount == 0:
       checkleaseinfo = "select * from leaseinfo where vmname='" + instancename + "'"
       cursor.execute(checkleaseinfo)

       if cursor.rowcount == 0:
          sql = "insert into leaseinfo values ('','" + instancename + "','" + lease_days_pass + "')";
       else:
          sql = "update leaseinfo set leasedays='" + lease_days_pass + "' where vmname='" + instancename + "'"

       cursor.execute(sql)
       db.commit()
       db.close()
       notify(owner,instancename,flavor,"createrequeststart","nil","nil")

#api.lease.delete_lease_record(controllername, instance, trueowner)
def delete_lease_record(controllername, instance, trueowner):
    db = pymysql.connect(host=controllername, port=3306, user='expostack', passwd='BSoniC', db='expo_nova')
    cursor = db.cursor()
    sql = "select d.network_info,c.hostname from instances c, instance_info_caches d where c.uuid=d.instance_uuid and c.uuid='" + instance + "'"
    cursor.execute(sql)
    resultnew = cursor.fetchall()
    generatetime1 = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    generatetime = str(generatetime1)
    for rows in resultnew:
        vmname = rows[1]
        trueownersql = "select owner from lease_active_vms where hostname='" + vmname +"'"
        cursor.execute(trueownersql)
        resulttrueowner = cursor.fetchall()
        for trueownerrows in resulttrueowner:
            trueowner = trueownerrows[0]
    db.close()
    notify(trueowner,vmname,"nil","deleterequeststart","nil",trueowner)

def trove_instance_delete(controllername, instance_id, owner):
    db = pymysql.connect(host=controllername, port=3306, user='expostack', passwd='BSoniC', db='expo_nova')
    cursor = db.cursor()
    dba = pymysql.connect(host=controllername, port=3306, user='expostack', passwd='BSoniC', db='expo_trove')
    cursora = dba.cursor()
    trovesql = "select compute_instance_id from instances where id='" + instance_id + "'"
    cursora.execute(trovesql)
    instancenovaid = "nil"
    if cursora.rowcount == 0:
       aka=""
    else:
       resulttrove = cursora.fetchall()
       for rowstrove in resulttrove:
           instancenovaid = str(rowstrove[0])
    sql = "select d.network_info,c.hostname from instances c, instance_info_caches d where c.uuid=d.instance_uuid and c.uuid='" + instancenovaid + "'"
    cursor.execute(sql)
    resultnew = cursor.fetchall()
    generatetime1 = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    generatetime = str(generatetime1)
    trueowner = owner
    vmname = "nil"
    for rows in resultnew:
        vmname = rows[1]
        trueownersql = "select owner from lease_active_vms where hostname='" + vmname +"'"
        cursor.execute(trueownersql)
        resulttrueowner = cursor.fetchall()
        for trueownerrows in resulttrueowner:
            trueowner = trueownerrows[0]
    dba.close()
    db.close()
    if vmname == "nil":
       asdas=""
    else:
       notify(trueowner,vmname,"nil","deleterequeststart","nil",owner)
