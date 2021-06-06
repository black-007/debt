# !D/pythor-test/files
# _*_ coding:utf-8 _*_
# author:lingyun

import pymysql
from warnings import filterwarnings

### 忽略 warning 信息
filterwarnings('ignore', category=pymysql.Warning)

host = "mysql"
database = "debt"

db = pymysql.connect(  ### 连接数据库
    host=host,
    port=3306,
    user="root",
    password="456789",
    database=database,
    charset="utf8mb4"
)
cur = db.cursor()  ### 游标


### 查询字段名
def field_sql(table_name="debt"):
    try:
        db.ping(reconnect=True)  ### 检查链接，断开重连

        sql = "select column_name from information_schema.COLUMNS " \
              "where table_name = '{}'and table_schema = '{}'".format(table_name, database)
        cur.execute(sql)
        result = cur.fetchall()
        return result

    except pymysql.Error as n:
        print('sql-fails:' + str(n))
        db.rollback()  ### 错误回滚
    ### 关闭数据库连接 #####
    db.close()

### 插入语句

def commit_sql(sql):
    try:
        db.ping(reconnect=True) ### 检查链接，断开重连

        cur.execute(sql)
        db.commit()  ### 提交修改

    except pymysql.Error as n:
        print('sql-fails:' + str(n))
        db.rollback()  ### 错误回滚
    ### 关闭数据库连接 #####
    db.close()


### 查询语句

def select_sql(sql):
    try:
        db.ping(reconnect=True)  ### 检查链接，断开重连

        cur.execute(sql)
        return cur.fetchall()

    except pymysql.Error as n:
        print('sql-fails:' + str(n))
        db.rollback()  ### 错误回滚
    ### 关闭数据库连接 #####
    db.close()


### 历史数据表
def create_table(name):
    try:
        db.ping(reconnect=True)  ### 检查链接，断开重连

        sql = "CREATE TABLE if NOT EXISTS `{}` (" \
              "`id` int(11) NOT NULL AUTO_INCREMENT," \
              "`time` date NOT NULL," \
              "`total` DOUBLE DEFAULT 0," \
              "`remain` DOUBLE DEFAULT 0," \
              "`used` DOUBLE DEFAULT 0," \
              "`repay` DOUBLE DEFAULT 0," \
              "`interest` DOUBLE DEFAULT 0," \
              "`today_interest` DOUBLE DEFAULT 0," \
              "`already_interest` DOUBLE DEFAULT 0," \
              "`note` varchar(255) DEFAULT ''," \
              "PRIMARY KEY (`id`)" \
              ") ENGINE=innodb DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci".format(name)

        cur.execute(sql)
        db.commit()  ### 提交修改

    except pymysql.Error as n:
        print('sql-fails:' + str(n))
        db.rollback()  ### 错误回滚
    ### 关闭数据库连接 #####
    db.close()

# debt 表
def create_debt():
    try:
        db.ping(reconnect=True)  ### 检查链接，断开重连

        sql = "CREATE TABLE if NOT EXISTS `debt` (" \
              "`id` int NOT NULL AUTO_INCREMENT," \
              "`name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL," \
              "`total` DOUBLE DEFAULT 0," \
              "`remain` DOUBLE DEFAULT 0," \
              "`used` DOUBLE DEFAULT 0," \
              "`repay` DOUBLE DEFAULT 0," \
              "`interest` DOUBLE DEFAULT 0," \
              "`today_interest` DOUBLE DEFAULT 0," \
              "`already_interest` DOUBLE DEFAULT 0," \
              "PRIMARY KEY (`id`) )" \
              " ENGINE=Innodb AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

        cur.execute(sql)

        sql = "create table if NOT EXISTS interest(" \
              "`id` int not null auto_increment," \
              "`datetime` datetime not null ," \
              "`daily_interest` DOUBLE DEFAULT 0," \
              "`today_interest` DOUBLE DEFAULT 0," \
              "`already_interest` DOUBLE DEFAULT 0," \
              "`note` varchar(255) DEFAULT ''," \
              "primary key (id))" \
              "engine=Innodb DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci "

        cur.execute(sql)

        sql = "create table if NOT EXISTS `water_bill`(" \
              "`id` int not null auto_increment," \
              "`datetime` datetime not null ," \
              "`value` DOUBLE DEFAULT 0," \
              "`note` varchar(255) DEFAULT ''," \
              "primary key (id))" \
              "engine=Innodb DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci "

        cur.execute(sql)

        db.commit()  ### 提交修改

    except pymysql.Error as n:
        print('sql-fails:' + str(n))
        db.rollback()  ### 错误回滚
    ### 关闭数据库连接 #####
    db.close()

### 月账单表
def create_month_bill():
    try:
        db.ping(reconnect=True)  ### 检查链接，断开重连

        sql = "CREATE TABLE if NOT EXISTS `month_bill` (" \
              "`id` int(11) AUTO_INCREMENT," \
              "`date` date NOT NULL," \
              "`name` varchar(255) DEFAULT ''," \
              "`value` double DEFAULT 66666666," \
              "`whether` varchar(255) DEFAULT ''," \
              "`note` varchar(255) DEFAULT ''," \
              "PRIMARY KEY (`id`))" \
              "engine=Innodb DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

        cur.execute(sql)
        db.commit()  ### 提交修改

    except pymysql.Error as n:
        print('sql-fails:' + str(n))
        db.rollback()  ### 错误回滚
    ### 关闭数据库连接 #####
    db.close()


