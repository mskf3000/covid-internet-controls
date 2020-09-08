#!/usr/bin/expect

spawn ssh user@0.tcp.ngrok.io -p 12709
expect "password"
send "! \r"
interact
