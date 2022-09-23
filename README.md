# HSIA-Cloud
**This project is for assignment purpose only.**

<br />

**User Data** <br />
#!/bin/bash <br />
sudo yum update -y <br /> <br />

sudo aws s3 cp s3://hrsystemwebapp --region us-east-1 /var/www/html/ --recursive <br /> <br />

sudo pip3 install flask <br /> 
sudo pip3 install pymysql <br />
sudo pip3 install boto3 <br /> <br />

sudo python3 ../../var/www/html/EmpApp.py <br />
