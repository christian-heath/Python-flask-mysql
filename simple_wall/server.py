from flask import Flask, redirect, render_template, request, flash, session
import datetime
import re
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = "secret"
bcrypt = Bcrypt(app)

PASSWORD_REGEX = re.compile(r'\d.*[A-Z]|[A-Z].*\d')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

mysql = connectToMySQL("mydb")


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/wall')
    return render_template('home.html')


@app.route('/wall')
def wall():
    if 'user_id' not in session:
        return redirect('/hacker')
    else:
        mysql = connectToMySQL("logindb")
        query = 'select * from users where id !=%(checkuser)s'
        data = {
            'checkuser': session['user_id'][0]['id']
        }
        allusers = mysql.query_db(query, data)
        mysql = connectToMySQL("logindb")
        query = 'SELECT id, user_id, content, sender FROM messages WHERE user_id = %(checkuser)s'
        data = {
            'checkuser': session['user_id'][0]['id']
        }
        mymessages = mysql.query_db(query, data)
        return render_template('wall.html', allusers=allusers, mymessages=mymessages)


@app.route('/register', methods=['POST'])
def register():
    errors = False
    mysql = connectToMySQL("logindb")
    query = 'select email from users where email = %(email)s'
    data = {
        'email': request.form['email']
    }
    check_email = mysql.query_db(query, data)
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
    if request.form['first_name'].isalpha() == False:
        flash("First name must contain alphabetical characters only!",
              'registration_error')
        errors = True
    if request.form['last_name'].isalpha() == False:
        flash("Last name must contain alphabetical characters only!",
              'registration_error')
        errors = True
    if len(request.form['last_name']) < 1:
        flash("Last name is required!", 'registration_error')
        errors = True
    if len(request.form['password']) < 8:
        flash("Password must be at least 8 characters!", 'registration_error')
        errors = True
    if not PASSWORD_REGEX.match(request.form['password']):
        flash("Password must contain at least one Uppercase letter and number.",
              'registration_error')
        errors = True
    if request.form['password'] != request.form['confirm_password']:
        flash("Passwords do not match!", 'registration_error')
        errors = True
    if errors == True:
        return redirect('/')
    else:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        mysql = connectToMySQL("logindb")
        query = 'INSERT INTO users(first_name,last_name,email,password,created_at,updated_at) VALUES(%(first_name)s,%(last_name)s,%(email)s,%(password)s,now(),now())'
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': pw_hash
        }
        new_user = mysql.query_db(query, data)
        mysql = connectToMySQL("logindb")
        query = 'select * from users where email = %(email)s'
        data = {
            'email': request.form['email']
        }
        check_user = mysql.query_db(query, data)
        session['user_id'] = check_user
        return redirect('/wall')


@app.route('/login', methods=['POST'])
def login():
    errors = False
    mysql = connectToMySQL("logindb")
    query = 'select * from users where email = %(email)s'
    data = {
        'email': request.form['email']
    }
    check_user = mysql.query_db(query, data)
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
        return redirect('/wall')


@app.route('/send', methods=['post'])
def send():
    mysql = connectToMySQL("logindb")
    query = 'INSERT INTO messages(content,user_id,created_at,updated_at,sender) VALUES (%(content)s,%(recipient_id)s,NOW(),NOW(),%(sender)s)'
    data = {
        'content': request.form['message'],
        'recipient_id': request.form['hidden'],
        'sender': session['user_id'][0]['first_name']
    }
    message_id = mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/delete/<id>', methods = ['post'])
def delete(id):
    mysql = connectToMySQL("logindb")
    query = 'DELETE FROM messages WHERE id = %(id)s AND user_id = %(user_id)s'
    data = {
        'id' : id,
        'user_id' : session['user_id'][0]['id']
    }
    deleter = mysql.query_db(query, data)
    print(deleter)
    return redirect('/wall')

@app.route('/hacker')
def hacker():
    return render_template("hacker.html")


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
