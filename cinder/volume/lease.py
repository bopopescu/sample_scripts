import pymysql
from datetime import datetime as datetimea
import pymysql
import json
import socket
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def notify(receiver, volumename, flavor, whattodo):
    me = "expostack@exponential.com"
    msg = MIMEMultipart('related')
    msgAlternative = MIMEMultipart('alternative')
    receiversplit = receiver.split("@")
    if len(receiversplit)==2:
       aaaa=""
    else:
       receiver = "esm@exponential.com"
    msg['From'] = me
    you = receiver;
    msg['To'] = receiver;
    msg.preamble = 'This is a multi-part message in MIME format.'
    text = "Hi!"

    if whattodo == "createrequestsuccess":
       msg['Subject'] = "Volume " + volumename + " is activated"
       html1 = "<html><head></head><body><b>Volume Name  : </b>" + volumename + "<br><b>Size : </b>" + flavor + "<br><br><b> Thanks and Regards</b><br>Expostack Administrator"

    if whattodo == "deleterequestsuccess":
       msg['Subject'] = "Volume " + volumename + " delete completed successfully"
       html1 = "<html><head></head><body><b>Volume Name  : </b>" + volumename + " deleted successfully.<br><br><b> Thanks and Regards</b><br>Expostack Administrator"

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


def checkowneremail(ownerid):
    dba = pymysql.connect(host="controller", port=3306, user='expostack', passwd='BSoniC', db='expo_keystone')
    cursora = dba.cursor()
    checkowner = "select local_id from id_mapping where public_id='"+ownerid+"'"
    cursora.execute(checkowner)
    resulta = cursora.fetchall()
    for rowsa in resulta:
        ownermail = rowsa[0]
    return ownermail

def create_success(ownername, voluuid, name, size):
    db = pymysql.connect(host="controller", port=3306, user='expostack', passwd='BSoniC', db='expo_cinder')
    cursor = db.cursor()
    generatetime1 = datetimea.strftime(datetimea.now(), '%Y-%m-%d %H:%M:%S')
    generatetime = str(generatetime1)
    owneremail = checkowneremail(ownername)
    sql = "insert into lease_active_volumes values ('" + name + "','" + generatetime + "','','success','days','" + owneremail + "','" + voluuid + "')";
    cursor.execute(sql)
    leasedays = "1"
    selectlease = "select leasedays from leaseinfo where volumename='" + name + "'"
    cursor.execute(selectlease)
    resultnew = cursor.fetchall()
    for rows in resultnew:
        leasedays = str(rows[0])
    updatednsrequest = "update lease_active_volumes set leasedays='"+leasedays+"' where volumename='"+name+"' and voluuid='" + voluuid + "'"
    cursor.execute(updatednsrequest)
    deleteleaseinfo = "delete from leaseinfo where volumename='" + name + "'"
    cursor.execute(deleteleaseinfo)
    db.commit()
    db.close()
    sizea = str(size)
    notify(owneremail, name, sizea, "createrequestsuccess")

def delete_success(volume_id, ownername):
    db = pymysql.connect(host="controller", port=3306, user='expostack', passwd='BSoniC', db='expo_cinder')
    cursor = db.cursor()
    sql = "select volumename from lease_active_volumes where voluuid='" + volume_id + "'"
    cursor.execute(sql)
    resultnew = cursor.fetchall()
    for rows in resultnew:
        volname = str(rows[0])

    owneremail = checkowneremail(ownername)
    deleteleaseinfo = "delete from lease_active_volumes where voluuid='" + volume_id + "'"
    cursor.execute(deleteleaseinfo)
    db.commit()
    db.close()
    notify(owneremail, volname, "delete", "deleterequestsuccess")    
