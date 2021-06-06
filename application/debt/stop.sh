#!/bin/bash

pid=$(ps -ef|grep gunicorn|grep -v grep|head -1|awk '{print $2}')
row=$(ps -ef|grep gunicorn|grep -v grep|wc -l)


if [ $row -gt 0 ]
then 

  kill -9 $pid

  a=0
  while (( $row > 0 ))
  do
    sleep 3
    a=`expr $a + 1`
    if [ $a -gt 7 ] 
    then
      echo "timeout! 重新执行"
      exit 0
    fi
    echo "停止中"
    echo $a
    row=$(ps -ef|grep gunicorn|grep -v grep|wc -l)
  done
fi 

echo "already stop"

