# index file

from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mysqldb import MySQL
import os
#from passlib.hash import pbkdf2_sha256
from passlib.hash import sha256_crypt
from FrostCryption import *
from PassMaker import *
import pyperclip


# CONFIG
app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'TonyStark@7018439751'
app.config['MYSQL_DB'] = 'PassManager'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = os.urandom(24)
etext = '\xb1<\x85\x9f\x18\xe0b\xf3AJb\xce\x94\xd4f\xea\x19@\xc3G\xc6\x8a\xf0'

# intialising MySQL
mysql = MySQL()
mysql.init_app(app)


@app.route('/')
def home():
    return render_template('Home.html')


@app.route('/CPasscodes', methods=['GET', 'POST'])
def CPasscodes():
    if 'user' not in session:
        flash("Please Login To Add Password", 'danger')
        return redirect('/login')
    if request.method == 'POST':
        url = request.form['URL']
        username = request.form['Username']
        passlen = int(request.form['passlen'])

        if username == "":
            username = 'N/A'

        # creating passcode
        passcode = get_pass(passlen)
        pyperclip.copy(passcode)
        flash('Password Copied', 'success')
        passcode = FrostCrypt(str(passcode), etext)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO main (url, username, passcode, uid)VALUES ('{}','{}','{}',{})".format(
            url, username, passcode, session['user']))
        mysql.connection.commit()
        cur.close()

    cur = mysql.connection.cursor()
    cur.execute("select name from user where uid = {}".format(session['user']))
    data = cur.fetchone()
    cur.close()
    return render_template("CPasscodes.html", data=data)


@app.route('/mypasscodes', methods=['GET', 'POST'])
def mypasscodes():
    if 'user' not in session:
        flash("Please Login To Search Password", 'danger')
        return redirect('/login')
    if request.method == 'POST':
        url = str(request.form['URL'])
        cur = mysql.connection.cursor()
        cur.execute("select `url`, `username`, `primarykey` from main where `url` REGEXP '{}' and uid = {} ORDER BY date_time DESC".format(
            url, session['user']))
        data = cur.fetchall()
        cur.close()
        return render_template('mypasscodes.html', data=data)

    cur = mysql.connection.cursor()
    cur.execute("Select * from main where uid = {}".format(session['user']))
    data = cur.fetchall()

    cur.close()

    return render_template('mypasscodes.html', data=data)


@app.route('/copy/<primarykey>')
def copy(primarykey):
    if 'user' not in session:
        flash("Please Login", 'danger')
        return redirect('/login')
    cur = mysql.connection.cursor()
    cur.execute(
        "select `passcode` from main where `primarykey` = '{}' ORDER BY date_time DESC".format(primarykey))
    data = cur.fetchone()
    cur.close()
    passcode = FrostDCrypt(data['passcode'], etext)

    try:
        pyperclip.copy(passcode)
    except(PermissionError):
        print("There is an error!")
    flash('Password Copied', 'success')
    return redirect('/mypasscodes')


@app.route('/delete/<primarykey>')
def delete(primarykey):
    if 'user' not in session:
        flash("Please Login", 'danger')
        return redirect('/login')
    cur = mysql.connection.cursor()
    cur.execute("delete from main where primarykey = {}".format(primarykey))
    mysql.connection.commit()
    cur.close()
    flash('Password Deleted', 'danger')
    return redirect('/mypasscodes')

# REGISTER ROUTE


@app.route('/register/', methods=['GET', 'POST'])
def register():

    if 'user' in session:
        return redirect('/RregisterSite')

    if request.method == 'POST':
        username = request.form['uname']
        cur = mysql.connection.cursor()
        cur.execute("select * from user where username = '{}'".format(username))
        data = cur.fetchone()
        cur.close()
        if data:
            flash('This username is already taken', 'danger')
            return redirect('/register')

        password = sha256_crypt.encrypt(str(request.form['password']))
        name = request.form['name']
        email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(name, email, password, username) VALUES(%s, %s, %s, %s)",
                    (name, email, password, username))
        mysql.connection.commit()

        cur.close()
        flash('You are successfully Registered', 'success')
        return redirect('/login')

    return render_template("Register.html")

# LOGIN ROUTE


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect('/RegisterSite')
    if request.method == 'POST':
        username = request.form['uname']
        passcode = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "select uid,password from user where username = %s", [username])
        data = cur.fetchone()
        cur.close()
        if data:
            password = data['password']
            uid = data["uid"]
            if sha256_crypt.verify(passcode,password):
                session['user'] = uid
                flash('Successfully logged in', 'success')
                return redirect('CPasscodes')
            else:
                flash('Invalid Log In','danger')
        else:
            flash('User not Found', 'danger')
    return render_template('Login.html')

# LOGOUT ROUTE


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        flash('Logged Out', 'danger')
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
