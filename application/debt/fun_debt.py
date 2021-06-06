# !D/pythor-test/files
# _*_ coding:utf-8 _*_
# author:lingyun

import cnt_mysql
import datetime


def daily_interest ():  ### 日利息

    # ### 单个最新使用总额
    # def new_total_single (name='total', column='used'):
    #     new_total = cnt_mysql.select_sql("select {} from debt WHERE name = '{}'".format(column,name))[0][0]
    #     return new_total

    ### 单个日利息
    def daily_interest_single (name, daily_ratio, column='used'):
        new_total = cnt_mysql.select_sql("select {} from debt WHERE name = '{}'".format(column, name))[0][0]
        daily_interest = new_total * daily_ratio
        return daily_interest

    ### 信用卡集合 日利率 0.000128
    card_list = ['上海', '中信', '交通', '光大', '华夏', '工商', '平安', '广发', '招商', '浦发']
    ### 日利率 0.0005 集合
    wu_list = ['新网', '浦发备用金', '招联金融', '云闪付', '金条']

    card_daily_interest = 0
    for i in card_list:
        a = daily_interest_single(i, 0.000128)
        card_daily_interest += a

    wu_daily_interest = 0
    for i in wu_list:
        a = daily_interest_single(i, 0.0005)
        wu_daily_interest += a

    a = card_daily_interest + wu_daily_interest + daily_interest_single('三六零', 0.0007) \
        + daily_interest_single('网商贷', 0.00035) + daily_interest_single('借呗', 0.00045) \
        + daily_interest_single('微粒贷', 0.00045)
    return a


def update_debt_total():  ### 更新 debt 表内 total 数据

    def gross(name):  ### 求字段总和
        row    = cnt_mysql.select_sql("select  count(*) from debt")[0][0] - 1
        totals = cnt_mysql.select_sql("select `{}` from debt limit {}".format(name, row))
        result = 0
        for a in totals:
            result += a[0]
        return result
    ### 更新debt表第三个及以后的字段名total行数据
    field_list = cnt_mysql.field_sql('debt')
    for i in field_list:
        if i[0] != "id":
            if i[0] != "name":
                cnt_mysql.commit_sql("update debt set {} = {} WHERE NAME = 'total'".format(i[0], gross(i[0])))


def insert_interest(note=''): ### 插入 interest 表 note
    # 每日利息
    daily = round(daily_interest(), 2)
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 所有项目已还利息
    gross_already_interest = cnt_mysql.select_sql("select already_interest "
                                                  "from total order by id desc limit 1")[0][0]
    # 所有项目今日总利息
    gross_today_interest = cnt_mysql.select_sql("select today_interest "
                                                "from total order by id desc limit 1")[0][0]
    cnt_mysql.commit_sql("insert into interest (datetime, daily_interest, today_interest, already_interest,  note) "
                         "values ('{}', {}, {}, {}, '{}')"
                         .format(now_time, daily, gross_today_interest, gross_already_interest, note))


def update_interest(name, interest): ### 更新利息
    interest = float(interest)
    ## 当天日期
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    # 最近利息
    already_interest = cnt_mysql.select_sql("select already_interest from debt WHERE name = '{}'"
                                            .format(name))[0][0]
    today_interest   = cnt_mysql.select_sql("select today_interest from debt WHERE name = '{}'"
                                            .format(name))[0][0]
    # 最新利息
    already_interest += interest
    today_interest   += interest
    # 所有项目已还利息
    gross_already_interest = cnt_mysql.select_sql("select already_interest "
                                                  "from total order by id desc limit 1")[0][0]
    # 所有项目今日总利息
    gross_today_interest   = cnt_mysql.select_sql("select today_interest "
                                                  "from total order by id desc limit 1")[0][0]
    # 最新总利息
    gross_today_interest   += interest
    gross_already_interest += interest

    ### 更新 debt 表
    cnt_mysql.commit_sql("update debt set today_interest = {}, already_interest = {}  WHERE name = '{}'"
                         .format(today_interest, already_interest, name))
    cnt_mysql.commit_sql("update debt set today_interest = {}, already_interest = {}  WHERE name = 'total'"
                         .format(gross_today_interest, gross_already_interest))

    ### 更新相应表
    cnt_mysql.commit_sql("update `{}` set today_interest = {}, already_interest = {} where time = '{}'"
                         .format(name, today_interest, already_interest, day))

    #### 更新 total 表
    cnt_mysql.commit_sql("update total set today_interest = {}, already_interest = {} WHERE time = '{}'"
                         .format(gross_today_interest, gross_already_interest, day))

    ### interest 表
    note = name + ' 新增利息 ' + str(interest)
    insert_interest(note)


def copy_single_debt(name='total'): ### 复制 debt 内最新数据到 相应 表
    update_debt_total()  ### 更新 debt 表内 total 数据

    ### 当天日期
    day = datetime.datetime.now().strftime("%Y-%m-%d")

    ### 定义查询 debt 内 name 表数据函数
    def field_value(field, name):
        result = cnt_mysql.select_sql("select {} from debt where name = '{}'".format(field, name))[0][0]
        return result

    for i in [name, 'total']:
        total    = field_value('total', i)
        remain   = field_value('remain', i)
        used     = field_value('used', i)
        repay    = field_value('repay', i)
        interest = field_value('interest', i)
        # today_interest   = field_value('today_interest', i)
        already_interest = field_value('already_interest', i)
        ### 建表
        cnt_mysql.create_table(i)
        # 表内数据条数
        count = cnt_mysql.select_sql("select count(*) from `{}`".format(i))[0][0]
        # 插入数据
        insert_data = "insert into `{}` (time, total, remain, used, repay, interest, already_interest) " \
                      "VALUES ('{}', {}, {}, {}, {}, {}, {})"\
                      .format(i, day, total, remain, used, repay, interest, already_interest)
        # 更新数据
        update_data = "update `{}` " \
                      "set total={}, remain={}, used={}, repay={}, interest={}, already_interest={} " \
                      "WHERE time = '{}'"\
                      .format(i, total, remain, used, repay, interest, already_interest, day)
        # 更新 debt 表 today_interest 字段为 0
        zero_today_interest = "update debt set today_interest = 0 where name = '{}'".format(i)

        if count == 0:
            cnt_mysql.commit_sql(insert_data)
        else:
            # 表最新日期
            new_day = str(cnt_mysql.select_sql("select time from `{}` order by id desc limit 1".format(i))[0][0])
            if new_day != day:
                cnt_mysql.commit_sql(zero_today_interest)
                cnt_mysql.commit_sql(insert_data)
            else:
                cnt_mysql.commit_sql(update_data)


def copy_all_debt():   ### 复制 debt 内最新数据到各表
    ### 更新 debt 表内 total 数据
    update_debt_total()
    ### 当天日期
    day = datetime.datetime.now().strftime("%Y-%m-%d")

    ### 定义查询debt内表名各表数据函数
    def field_value(field, name):
        result = cnt_mysql.select_sql("select {} from debt where name = '{}'".format(field, name))[0][0]
        return result

    ### 查询debt内所有表名
    name_list = cnt_mysql.select_sql("select name from debt ")

    for i in name_list:
        name     = i[0]
        total    = field_value('total', name)
        remain   = field_value('remain', name)
        used     = field_value('used', name)
        repay    = field_value('repay', name)
        interest = field_value('interest', name)
        # today_interest    = field_value('today_interest', name)
        already_interest = field_value('already_interest', name)
        ### 建表
        cnt_mysql.create_table(name)
        # 表内数据条数
        count = cnt_mysql.select_sql("select count(*) from `{}`".format(name))[0][0]
        # 插入数据
        insert_data = "insert into `{}` (time, total, remain, used, repay, interest, already_interest) " \
                      "VALUES ('{}', {}, {}, {}, {}, {}, {})"\
                      .format(i[0], day, total, remain, used, repay, interest, already_interest)
        # 更新数据
        update_data = "update `{}` " \
                      "set total={}, remain={}, used={}, repay={}, interest={}, already_interest={} " \
                      "WHERE time = '{}'"\
                      .format(i[0], total, remain, used, repay, interest, already_interest, day)
        # 更新 debt 表 today_interest 字段为 0
        zero_today_interest = "update debt set today_interest = 0 where name = '{}'".format(name)

        if count == 0:
            cnt_mysql.commit_sql(insert_data)
        else:
            # 表最新日期
            new_day = str(cnt_mysql.select_sql("select time from `{}` order by id desc limit 1".format(name))[0][0])
            if new_day != day:
                cnt_mysql.commit_sql(zero_today_interest)
                cnt_mysql.commit_sql(insert_data)
            else:
                cnt_mysql.commit_sql(update_data)

    ### interest 表
    note = '执行copy_all_debt'
    insert_interest(note)

### flask 更新 debt 数据
def update_web_debt(name='三六零', field='used', value='0', add_interest='0', repay_interest='0', note=""):
    total = cnt_mysql.select_sql("select total from debt WHERE name = '{}' ".format(name))[0][0]

    if field == "total":
        remain = cnt_mysql.select_sql("select remain from debt WHERE name = '{}' ".format(name))[0][0]
        total -= value
        remain -= value
        cnt_mysql.commit_sql("update debt set total = {}, remain = {} "
                             "WHERE name = '{}' ".format(total, remain, name))
    elif field == "used":
        used = cnt_mysql.select_sql("select used from debt WHERE name = '{}' ".format(name))[0][0]
        used += value
        remain = total - used
        if name == "浦发备用金":
            remain = 0
        old_interest = cnt_mysql.select_sql("select interest from debt WHERE name = '{}' ".format(name))[0][0]
        if old_interest > 0:
            new_interest = old_interest + add_interest - repay_interest
        else:
            new_interest = old_interest + add_interest
        if new_interest < 0:
            new_interest = 0
        repay = used + new_interest

        cnt_mysql.commit_sql("update debt set remain = {}, used = {}, repay = {}, interest = {} "
                             "WHERE name = '{}' ".format(remain, used, repay, new_interest, name))

    else:
        return ("field 输入 total or used ")

    copy_single_debt(name) # 复制数据到相应表
    interest_note = '修改 {}, 使用 {} {}'.format(name, value, note)
    insert_interest(interest_note)


def copy_month_bill():
    last_month_data = cnt_mysql.select_sql("select * from month_bill order by id desc limit 20")
    year = datetime.datetime.now().strftime("%Y")
    month = datetime.datetime.now().strftime("%m")
    next_month = int(month) + 1

    cnt_mysql.commit_sql("insert into month_bill(date, name, note) "
                         "value(now(), '{}', '{}')".format("新账单, 新账单", "新账单, 新账单, 新账单"))
    cnt_mysql.commit_sql("insert into month_bill(date, name, note) "
                         "value(now(), '{}', '{}')".format("新账单, 新账单", "新账单, 新账单，新账单"))
    for i in reversed(last_month_data):
        day = i[1].day
        date = year + "-" + str(next_month) + "-" + str(day)
        name = i[2]
        value = i[3]
        note = i[5]
        cnt_mysql.commit_sql("insert into month_bill(date, name, value, note) "
                             "value('{}', '{}', {}, '{}')".format(date, name, value, note))

