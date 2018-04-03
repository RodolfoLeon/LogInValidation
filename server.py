from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
import os, binascii
password = 'password'
# salt = binascii.b2a_hex(os.urandom(15))
# hashed_password = md5(password + salt)
app = Flask(__name__)
mysql = MySQLConnector(app,'loginregistration')
app.secret_key="LoginSecurity"
EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

@app.route('/')
def index():
    if not 'user' in session:
        session['user']= "non"
    return render_template ('index.html')

@app.route('/register',methods=['post'])
def register():
    if request.form['process'] == 'register':
        valid = True
        if len(request.form['first_name']) <2 and str.isalpha(request.form['first_name'] == False):
            flash("Please enter your first name.", 'error')
            valid = False
        elif len(request.form['last_name']) <2 and str.isalpha(request.form['first_name'] == False):
            flash("Please enter your last name.", 'error')
            valid = False
        elif not EMAIL_REGEX.match(request.form['email']):
            flash('Please enter a correct email address.', 'error')
            valid=False
        elif len(request.form['password']) < 8:
            flash('Password must be at least 8 characters long.', 'error')
        elif not request.form('pwconfirm') == request.form('password'):
            flash("Incorrect confirmation for the password, please try again.", 'error')
            valid = False

        if valid == False:
            return redirect("/")
        elif valid == True:
            flash ("Thank you for registering.")
            data = {
                'firstname': request.form['first_name'],
                'lastname':  request.form['last_name'],
                'email': request.form['email'],
                'password': md5.new(request.form['password']).hexdigest()
            }
            query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:firstname, :lastname, :email, :password, NOW(), NOW())"
            mysql.query_db(query, data)
            session['user_id'] = user[0]['id']
            return redirect ('/success')

    elif request.form['process'] == 'login':
        email = request.form['logemail']
        password = request.form['logpassword']
        if not EMAIL_REGEX.match(request.form['logemail']):
            flash('Please enter a correct email address.', 'error')
            return redirect ('/')
        user_query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
        query_data = {'email': email}
        user = mysql.query_db(user_query, query_data)
        if len(user) != 0:
        encrypted_password = md5.new(password).hexdigest()
        if user[0]['password'] == encrypted_password:
            session['user_id'] = user[0]['id']
            return redirect ('/')
        else:
           flash('Incorrect username or password. Please enter correct information.')
        return redirect ('/success')

@app.route('/success')
def success():
    return render_template('success.html')

app.run(debug=True)