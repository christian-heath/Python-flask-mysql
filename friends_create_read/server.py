from flask import Flask, render_template, session, flash, redirect, request
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)


mysql = connectToMySQL('mydb')

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/createUser')
def create():
    pw_hash = bcrypt.generate_password_hash('password')  
    print(pw_hash)
    mysql = connectToMySQL("mydb")
    query = "INSERT INTO users (username, password) VALUES (%(username)s, %(password_hash)s);"
    data = { "username" : request.form['username'],
             "password_hash" : pw_hash }
    mysql.query_db(query, data)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
