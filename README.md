# HSIA-Cloud
**This project is for assignment purpose only.**

<br />

**User Data** <br />
#!/bin/bash
sudo yum update -y

sudo aws s3 cp s3://hrsystemwebapp --region us-east-1 /var/www/html/ --recursive

sudo pip3 install flask
sudo pip3 install pymysql
sudo pip3 install boto3

sudo python3 ../../var/www/html/EmpApp.py
