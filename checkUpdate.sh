#!/bin/sh

if [ -d "/home/yuchou1/workspace/MailFile/" ]; then
	cd /home/yuchou1/workspace/MailFile
else
	echo "目录不存在"
	exit 1
fi


o=`ls |wc -l`
while true
do
sleep 10
new=`ls|wc -l `
if [ $new -eq $o ];then
	continue
else
	o=$new
	echo $o
	echo "【`date`】您有新的邮件！" > /home/yuchou1/workspace/emails
	break

fi
done
