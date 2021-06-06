FROM python

WORKDIR /

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime   \
    && pip3 install gunicorn datetime flask jinja2 pyecharts pymysql apscheduler cryptography pyecharts

COPY debt /debt

EXPOSE 13000

ENTRYPOINT ["/bin/bash","/debt/start.sh"]
