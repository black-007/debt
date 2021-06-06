#!/bin/bash
### 遇到非零返回值，会直接退出脚本
set -e

# debt-web-image
if [ `docker images|grep debt-web|wc -l` -ne 1 ];
then
   echo "built debt-web image"
   docker build -t debt-web .
else
   echo "image:debt-web already exists, you can do 'docker rmi debt-web'"
   exit 1
fi
# init docker-compose
docker-compose up -d

num=5
while  [ `docker ps |grep debt-mysql|wc -l` -ne 1 ]
do
   let num--
   echo "waiting for mysql $num"
   sleep 2
   if [ $num -eq 0 ]; 
   then
      echo "mysql not exists , check mysql!"
      exit 1
   fi
done

# init mysql
echo "init mysql ......"
sleep 20

database_num=5
while [ $database_num -ne 0 ]
do
    if [[ `docker ps |grep debt-mysql|awk '{print $10}'` == '(healthy)' ]];
#   if [ `docker exec -i debt-mysql mysql -uroot -p456789 -e "show databases"|grep mysql|wc -l` -eq 1 ];
   then
      docker exec -i debt-mysql mysql -uroot -p456789 -e "create database if not exists debt" >> start.log 2>&1
      docker exec -i debt-mysql mysql -uroot -p456789 debt < debt-base.sql >> start.log 2>&1
      break
   else
      sleep 5
      let database_num--
      echo "waiting for init database debt ... $database_num"
      
      if [ $database_num -eq 0 ];
      then
         echo "请手动执行以下命令"
         echo "docker exec -i debt-mysql mysql -uroot -p456789 -e 'create database if not exists debt' >> start.log 2>&1"
         echo "docker exec -i debt-mysql mysql -uroot -p456789 debt < test02-base.sql >> start.log 2>&1"
         exit 1
      fi 
   fi    
done

echo "restart web"

docker-compose restart web

echo 'http://$ip:23000'
