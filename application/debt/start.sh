#!/bin/bash

cd $(dirname $0)
mkdir -p logs

# 启动程序
gunicorn -c gunicorn_conf.py flask_debt:app
# 启动定时任务
nohup python3 cron.py >>cron.log 2>&1 &

# 开启前台输出，保持容器不退出
tail -f cron.log
