from flask import Flask, render_template, request, session, flash, redirect, url_for
from pymysql import connections
import os
import boto3


#set bucket
bucket = "benedicttanzhihang-employee"
region = "us-east-1"

app = Flask(__name__)

#connect to rds
db_conn = connections.Connection(
    host="hsiadb.cfvg8qgp5zqj.us-east-1.rds.amazonaws.com",
    port=3306,
    user="itadm",
    password="main1234",
    db="hsiadb"

)
output = {}

#app.config
app.config['SECRET_KEY'] = 'benedicttanzhihang'

#### Author: Lai Liang Chun ####
#Default App Route
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('LoginEmp.html')

#process login data
@app.route("/login", methods=['GET', 'POST'])
def login():

    #get input fields
    if request.method == 'POST':
        userID = request.form['userID']
        password = request.form['password']

    #connect to db
    cur = db_conn.cursor()  
    cur.execute('SELECT * FROM users WHERE userID = %s AND password = %s AND role = %s', (userID, password, 1))
    
    result = cur.fetchone()

    #set session
    if result:
        session['loggedIn'] = True
        session['userID'] = result[0]
        
        #return page after login
        return render_template('home.html')
    else:

        #return "Invalid ID or Password or Role"      
        flash('Invalid ID or Password or Role!', category='error')
        return redirect('/')

#logout function
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    
    # Remove session data   
    session.pop('loggedIn', None)
    session.pop('userID', None)

    return redirect('/')





#### Author: Benedict Tan Zhi Hang ####
#Home page
@app.route('/home', methods=['GET', 'POST'])
def goHome():
    return render_template('home.html')

#Add employee page
@app.route('/addpemp', methods=['GET', 'POST'])
def goAddPage():
    return render_template('addEmp.html')

#Add employee process
@app.route("/addemp", methods=['POST'])
def AddEmp():

    if request.form['submit'] == "Save":
        #save profile
        name = request.form['name']
        gender = request.form['optradio']
        icNum = request.form['icNum']
        phoneNum = request.form['pn']
        email = request.form['email']
        position = request.form['position']
        address = request.form['address']
        recruitmentDate =  request.form['recruitmentDate']
        emp_image_file = request.files['emp_image_file']

        #file name to store in S3 Bucket
        emp_image_file_name_in_s3 = "name-" + str(name) + "_image_file"
        profilePic = emp_image_file_name_in_s3
        profilePic.replace(" ", "+")

        #sql statement for insert
        insert_sql = "INSERT INTO employees (name, position, address, gender, phoneNum, email, icNum, dateEntered, profilePic) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor = db_conn.cursor()

        try:
            #insert into rds
            cursor.execute(insert_sql, (name, position, address, gender, phoneNum, email, icNum, recruitmentDate, profilePic))
            db_conn.commit()

            # Uplaod image file in S3 #
            s3 = boto3.resource('s3')
            s3.Bucket(bucket).put_object(Key='profilepic/{}'.format(emp_image_file_name_in_s3), Body=emp_image_file)   

        finally:
            cursor.close()

        return render_template('addEmp.html')

    else:
        return render_template('addEmp.html')

#Go add new cert page
@app.route('/uploadcert/<string:id>', methods=['GET', 'POST'])
def goNewCert(id):

    #Retrieve details
    cur=db_conn.cursor()
    select_sql = "SELECT * FROM employees WHERE employeesID = %s"
    cur.execute(select_sql, (id))
    details = cur.fetchall()
    cur.close()

    return render_template('uploadCert.html', var = details)

@app.route("/uploadCertToS3", methods=['POST'])
def AddCert():

    #Save profile
    id =  request.form['id']
    emp_image_file = request.files['emp_image_file']

    #Retrieve to see how many cert for that user
    cur=db_conn.cursor()
    select_sql = "SELECT COUNT(certName) FROM trainingCert WHERE employeesID = %s"
    cur.execute(select_sql, (id))
    num = cur.fetchone()
    cur.close()

    #file name to store in S3 Bucket
    emp_image_file_name_in_s3 = "id-" + str(id) + "_cert_" + str(num[0])

    #sql statement for insert
    insert_sql = "INSERT INTO trainingCert (certName, employeesID) VALUES (%s,%s)"
    cursor = db_conn.cursor()

    try:
        #insert into rds
        cursor.execute(insert_sql, (emp_image_file_name_in_s3, id))
        db_conn.commit()

        # Uplaod file in S3 #
        s3 = boto3.resource('s3')
        s3.Bucket(bucket).put_object(Key='certificate/{}'.format(emp_image_file_name_in_s3), Body=emp_image_file)   

    finally:
        cursor.close()

    return redirect(url_for('viewSpecificCert', id=id))






#### Author: Ng Soon Kit ####
#view all staff in list
@app.route('/cpdl', methods=['GET', 'POST'])
def goViewStaff():
    cur=db_conn.cursor()    
    cur.execute("SELECT * FROM employees")
    details = cur.fetchall()
    return render_template('ViewStaff.html', var = details)

#view all staff in grid
@app.route('/cpdg', methods=['GET', 'POST'])
def goViewStaffG():

    cur=db_conn.cursor()    
    cur.execute("SELECT * FROM employees")
    details = cur.fetchall()
    return render_template('viewAllEmpGrid.html', var = details)

#view specific staff - contact
@app.route('/viewSpecific/<string:id>', methods=['GET', 'POST'])
def viewSpecific(id):

    cur=db_conn.cursor()
    select_sql = "SELECT * FROM employees WHERE employeesID = %s"
    cur.execute(select_sql, (id))
    details = cur.fetchall()
    return render_template('empProfile.html', var = details)

#view specific staff - training certificate
@app.route('/viewSpecificCert/<string:id>', methods=['GET', 'POST'])
def viewSpecificCert(id):

    #Retrieve details
    cur=db_conn.cursor()
    select_sql = "SELECT * FROM employees WHERE employeesID = %s"
    cur.execute(select_sql, (id))
    details = cur.fetchall()
    cur.close()

    #Retrieve all cert
    cur=db_conn.cursor()
    select_sql = "SELECT * FROM trainingCert WHERE employeesID = %s"
    cur.execute(select_sql, (id))
    cert = cur.fetchall()
    cur.close()


    return render_template('empCert.html', var = details, certname = cert)








#### Author: Lau Haw Hang ####
#go to edit staff with form
@app.route('/gotoedit', methods=['GET', 'POST'])
def editstaff():

    id =  request.form['id']

    cur=db_conn.cursor()
    select_sql = "SELECT * FROM employees WHERE employeesID = %s"
    cur.execute(select_sql, (id))
    details = cur.fetchall()
    return render_template('editEmp.html', var = details)

#go to edit staff with anchor tag
@app.route('/goedit/<string:id>', methods=['GET', 'POST'])
def editstaffs(id):

    cur=db_conn.cursor()
    select_sql = "SELECT * FROM employees WHERE employeesID = %s"
    cur.execute(select_sql, (id))
    details = cur.fetchall()
    return render_template('editEmp.html', var = details)

#edit process
@app.route('/editemp', methods=['GET', 'POST'])
def editemp():

    if request.form['submit'] == "Save":
        #save profile
        name = request.form['name']        
        employeeID = request.form['employeeID']
        icNum = request.form['icNum']
        phoneNum = request.form['pn']
        email = request.form['email']
        position = request.form['position']
        address = request.form['address']
        emp_image_file = request.files['emp_image_file']

        #file name to store in S3 Bucket
        emp_image_file_name_in_s3 = "name-" + str(name) + "_image_file"
        profilePic = emp_image_file_name_in_s3
        profilePic.replace(" ", "+")

        #sql statement for update
        update_sql = "UPDATE employees SET name=%s, icNum=%s, position=%s, phoneNum=%s, address=%s, email=%s, profilePic=%s WHERE employeesID=%s"
        cursor = db_conn.cursor()
        

        try:
            #insert into rds
            cursor.execute(update_sql, (name, icNum, position, phoneNum, address, email, profilePic, employeeID))
            db_conn.commit()
            
            s3 = boto3.resource('s3')
            # Delete old image file in S3 #
            s3.Object(bucket, 'profilepic/{}'.format(emp_image_file_name_in_s3)).delete()
            # Uplaod new image file in S3 #
            s3.Bucket(bucket).put_object(Key='profilepic/{}'.format(emp_image_file_name_in_s3), Body=emp_image_file)   

        finally:
            cursor.close()

        return redirect(url_for('editstaffs', id=employeeID))

    else:
        return redirect(url_for('editstaffs', id=employeeID))




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
    
    
    
    
    
    
    
    