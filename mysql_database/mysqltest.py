import mysql.connector

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="sahilgupta221",
  password="easypass321!"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE covid_internet_controls")
