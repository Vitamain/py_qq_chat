import pymysql
from config import *
class DB:
    @staticmethod
    def find_user(username, password):
        # 获取 mysql 数据库连接
        conn = pymysql.connect(host=HOST, port=PORT, user=USERNAME, password=PASSWD, database=DB_NAME,
                               charset=CHARSET)
        # 获取游标
        cursor = conn.cursor()

        # 执行 sql 语句
        sql = "select * from user where username = %s and password = %s"
        cursor.execute(sql, (username, password))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        return res



#res = DB.find_user('11','123')
#print(res)
#list={}
#list['name'] = {'age':23, 'score':19}
#print(list['name']['age'])
