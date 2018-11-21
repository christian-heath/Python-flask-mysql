from flask import Flask, render_template, session, flash, redirect, request
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)

mysql = connectToMySQL('mydb')

@app.route('/')
def index():
    mysql = connectToMySQL("leads_and_clients")
    all_clients = mysql.query_db("SELECT * FROM clients")
    return render_template('index.html', clients = all_clients)

if __name__ == "__main__":
    app.run(debug=True)
