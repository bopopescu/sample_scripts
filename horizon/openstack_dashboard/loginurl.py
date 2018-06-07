import pymysql

def get_login_url():
    db = pymysql.connect(host='controller', port=3306, user='expostack', passwd='BSoniC', db='expo_nova')
    cursor = db.cursor()
    sql = "select status from activity"
    cursor.execute(sql)
    resultnew = cursor.fetchall()
    for rows in resultnew:
        status = rows[0]
        if status == "maintenance":
           LOGIN_URL = 'maintenance/'
        else:
           LOGIN_URL = 'login/'
    return str(LOGIN_URL)
