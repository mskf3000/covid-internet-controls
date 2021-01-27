#!/usr/bin/expect -f
set timeout 120
spawn sudo ansible-playbook deploy.yml
expect "*?assword:*"
send -- "easypass321!\r"
sleep 20
