from flask import Flask, redirect, render_template, request, flash, session
import pymysql.cursors
import datetime
import re
from flask_bcrypt import Bcrypt        
from mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = "ThisIsSecret!"
bcrypt = Bcrypt(app)

PASSWORD_REGEX = re.compile(r'\d.*[A-Z]|[A-Z].*\d')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

mysql = connectToMySQL("mydb")

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/success')
def success():
    if 'user_id' not in session:
        return redirect('/hacker')
    return render_template('success.html')

@app.route('/register', methods=['POST'])
def register():
    errors = False
    mysql = connectToMySQL("logindb")
    query='select email from users where email = %(email)s'
    data={
        'email': request.form['email']
    }
    check_email=mysql.query_db(query,data)
    print("Check email result", check_email)
    if check_email != ():
        flash('Email is already in use!', 'registration_error')
        errors = True
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!", 'registration_error')
        errors = True
    if len(request.form['first_name']) < 1:
        flash("First name is required!", 'registration_error')
        errors = True
    if request.form['first_name'].isalpha()==False:
        flash("First name must contain alphabetical characters only!", 'registration_error')
        errors = True
    if request.form['last_name'].isalpha()==False:
        flash("Last name must contain alphabetical characters only!", 'registration_error')
        errors = True
    if len(request.form['last_name']) < 1:
        flash("Last name is required!", 'registration_error')
        errors = True
    if len(request.form['password']) < 8:
        flash("Password must be at least 8 characters!", 'registration_error')
        errors = True
    if not PASSWORD_REGEX.match(request.form['password']):
        flash("Password must contain at least one Uppercase letter and number.", 'registration_error')
        errors = True
    if request.form['password'] != request.form['confirm_password']:
        flash("Passwords do not match!", 'registration_error')
        errors = True
    if errors == True:
        return redirect('/')
    else:
        pw_hash = bcrypt.generate_password_hash(request.form['password']) 
        mysql = connectToMySQL("logindb")
        query='INSERT INTO users(first_name,last_name,email,password,created_at,updated_at) VALUES(%(first_name)s,%(last_name)s,%(email)s,%(password)s,now(),now())'
        data={
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': pw_hash
        }
        user_info = mysql.query_db(query,data)
        print(user_info)
        return redirect('/success')

@app.route('/login', methods=['POST'])
def login():
    errors = False
    mysql = connectToMySQL("logindb")
    query='select * from users where email = %(email)s'
    data={
        'email': request.form['email']
    }
    check_user=mysql.query_db(query,data)
    if check_user == ():
        flash('Email is invalid!', 'login_error')
        errors = True
    if bcrypt.check_password_hash(check_user[0]['password'], request.form['password']) != True:
        flash('Password is invalid!', "login_error")
        errors = True
    if errors == True:
        return redirect('/')
    else:
        session['user_id'] = check_user
        print(session['user_id'])
        return redirect('/success')

@app.route('/hacker')
def hacker():
    return render_template("hacker.html")

@app.route('/logout', methods = ['POST'])
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)