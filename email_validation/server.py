from flask import Flask, render_template, session, flash, redirect, request
from mysqlconnection import connectToMySQL
app = Flask(__name__)
app.secret_key = 'secret'
import re
import datetime
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

mysql = connectToMySQL('mydb')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/process', methods=['post'])
def process():
    error = False
    # check to see if email address is unique
    mysql = connectToMySQL("emailsdb")
    query = "SELECT email FROM users WHERE email = %(email)s"
    data = {'email': request.form['email']}
    check_email = mysql.query_db(query, data)
    print("check email result", check_email)
    if check_email != ():
        flash("Email is already in use!")
        error = True
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
        error = True
    if error == True:
        retq    urn redirect('/')
    else:
        mysql = connectToMySQL("emailsdb")
        query = "INSERT into users (email, created_at) VALUES (%(email)s, NOW())"
        data = {
            'email': request.form['email']
        }
        new_email_id = mysql.query_db(query, data)
        return redirect('/success')


@app.route('/success')
def success():
    mysql = connectToMySQL("emailsdb")
    all_emails = mysql.query_db("SELECT * FROM users")
    print(all_emails)
    return render_template('success.html', emails=all_emails)


if __name__ == "__main__":
    app.run(debug=True)
