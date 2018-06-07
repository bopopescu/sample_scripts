import pymysql
import json
import datetime
db = pymysql.connect(host="controller", port=3306, user='expostack', passwd='BSoniC', db='expo_nova')
cursor = db.cursor()
generatetime1 = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
generatetime = str(generatetime1)
sql = "insert into dnsrequests values ('vi','','create','','" + generatetime + "')";
cursor.execute(sql)
db.commit()
db.close()
