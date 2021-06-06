# !D/pythor-test/files
# _*_ coding:utf-8 _*_
# author:lingyun

from flask import Flask, render_template, request, url_for, redirect
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
import cnt_mysql
import fun_debt
import datetime

from random import randrange
from pyecharts import options as opts
from pyecharts.charts import Bar


CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))  ### 模板位置
app = Flask(__name__, template_folder="html")   ### flask

home_page = "index.html"
data_page = "data.html"
display_page = "display.html"
chart_page = "chart.html"


##########################################################################################################
@app.route("/", methods=['GET', 'POST'])
def index():

    return render_template(home_page)


@app.route("/display", methods=['GET', 'POST'])
def display():
    month = datetime.datetime.now().strftime("%Y-%m")
    interest = cnt_mysql.select_sql("select * from interest order by id desc limit 30")
    water_bill = cnt_mysql.select_sql("select * from water_bill order by id desc limit 30")
    total = cnt_mysql.select_sql("select value from water_bill where datetime like '{}%'".format(month))
    value = 0
    for i in total:
        value += i[0]
    value = '%.2f' % value

    return render_template(display_page, interest_table=interest, month_value=value, water_bill=water_bill)


@app.route("/data", methods=['GET', 'POST'])
def data():
    month_bill = reversed(cnt_mysql.select_sql("select * from month_bill order by id desc limit 19"))
    debt = cnt_mysql.select_sql("select * from debt")
    baitiao = debt[6]
    huabei = debt[10]

    b = 0
    for i in debt[1:21]:
        b += i[3]
    remain = b - huabei[3] - baitiao[3]

    return render_template(data_page, month_bill=month_bill, debt_table=debt, remain='%.2f' % remain)


@app.route("/update_data", methods=['GET', 'POST'])
def update_data():
    if request.method == 'GET':
        return "method == get, use POST"
    if request.method == 'POST':
        # 获取表单数据
        name = request.form.get('name')
        field = request.form.get('field')
        type = request.form.get('type')
        if request.form.get('repay_value') == "":
            repay_value = 0
        else:
            repay_value = float(request.form.get('repay_value'))
        if request.form.get('repay_interest') == "":
            repay_interest = 0
        else:
            repay_interest = float(request.form.get('repay_interest'))
        if request.form.get('add_value') == "":
            add_value = 0
        else:
            add_value = float(request.form.get('add_value'))
        if request.form.get('add_interest') == "":
            add_interest = 0
        else:
            add_interest = float(request.form.get('add_interest'))
        note = request.form.get('note')

        interest = add_interest - repay_interest
        value    = add_value - repay_value

        # 更新 数据库
        if type == "流水":
            bill_note = "{} ,{}".format(note, name)
            cnt_mysql.commit_sql("insert into water_bill (datetime, value, note) "
                                 "values (now(), {} , '{}')".format(add_value, bill_note))

        info = {'name': name, 'field': field, 'note': 0, 'repay_value': 0, 'add_value': add_value,
                'repay_interest': 0, 'add_interest': 0, 'interest': 0, 'value': 0,
                'used': 0, 'repay': 0, 'already_interest': 0}

        if name != "其它":
            fun_debt.update_web_debt(name, field, value, add_interest, repay_interest, note)
            if repay_interest > 0:
                fun_debt.update_interest(name, repay_interest)

            # 传入返回值
            used = cnt_mysql.select_sql("select used from debt WHERE name = '{}'".format(name))[0][0]
            repay = cnt_mysql.select_sql("select repay from debt WHERE name = '{}'".format(name))[0][0]
            already_interest = cnt_mysql.select_sql("select already_interest from debt "
                                                    "WHERE name = '{}'".format(name))[0][0]
            back_note = "修改 {} 成功".format(name)
            info = {'name': name, 'field': field, 'note': back_note, 'repay_value': repay_value, 'add_value': add_value,
                    'repay_interest': repay_interest, 'add_interest': add_interest, 'interest': interest, 'value': value,
                    'used': used, 'repay': repay, 'already_interest': already_interest}

        return render_template('back.html', **info)


@app.route("/update_month_bill", methods=['post', 'get'])
def update_month_bill():
    if request.method == 'GET':
        return "method == get"
    if request.method == 'POST':
        # 获取表单数据
        name = request.form.get('name')
        name_id = cnt_mysql.select_sql("select id from month_bill "
                                       "where name = '{}' order by id desc limit 1".format(name))
        cnt_mysql.commit_sql("update month_bill set whether = '是' "
                             "where id = {}".format(name_id[0][0]))

    return redirect(url_for('data'))


@app.route("/chart")
def chart():
    return render_template(chart_page)


@app.route("/barChart", methods=['GET', 'POST'])
def barChart():
    # 获取表单数据
    # name = request.args.get('input_name')
    name = request.args.get('sel_name')
    field_name = request.args.get('field_name')
    field_index = 0
    if field_name == "total":
        field_index = 2
    elif field_name == "remain":
        field_index = 3
    elif field_name == "repay":
        field_index = 5
    elif field_name == "already_interest":
        field_index = 8
    else:
        field_index = 0

    def bar_base() -> Bar:
        if name is None:
            na = '借呗'
        else:
            na = name
        y_value = []
        x_day = []
        a = cnt_mysql.select_sql("select * from {}".format(na))
        x = 0
        for i in a:
            y = i[field_index]
            today = i[1]
            if x != y:
                x = y
                y_value.append(y)
                x_day.append(datetime.datetime.strftime(today, '%m-%d'))

        c = (
            Bar()
            .add_xaxis(x_day)
            .add_yaxis(field_name, y_value)
            # .add_yaxis("已付利息", y_interest)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=na, subtitle="柱状图"),
                datazoom_opts=opts.DataZoomOpts(),
            )
        )
        return c
    s = bar_base()
    return s.dump_options_with_quotes()


##################################################################################################################


if __name__ == "__main__":
    app.run()
