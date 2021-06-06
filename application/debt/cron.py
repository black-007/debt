# _*_ coding:utf-8 _*_
from apscheduler.schedulers.blocking import BlockingScheduler
import fun_debt


scheduler = BlockingScheduler(timezone="Asia/Shanghai")
# 在每天0点，0分 运行一次 fun_debt.copy_all_debt 方法
scheduler.add_job(fun_debt.copy_all_debt, 'cron', hour=0, minute=0)
# 每月 1号 0点 10分 运行一次 fun_debt.copy_month_bill 方法
#scheduler.add_job(fun_debt.copy_month_bill, 'cron', day=1, hour=0, minute=10)

scheduler.start()
