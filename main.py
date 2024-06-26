# index file

from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mysqldb import MySQL
import os
from passlib.hash import sha256_crypt
from FrostCryption import *
from PassMaker import get_pass, Secret_Key
import pyperclip
#from SendEmails import *


# CONFIG
app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'TonyStark@7018439751'
app.config['MYSQL_DB'] = 'PassManager'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = os.urandom(24)


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
        etext = get_pass(128)
        passcode = FrostCrypt(str(passcode), etext)
        Etext = FrostCrypt(str(etext), str(session['user']))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO main (url, username, passcode, uid, etext)VALUES ('{}','{}','{}',{},'{}')".format(
            url, username, passcode, session['user'], Etext))
        mysql.connection.commit()
        cur.close()

    cur = mysql.connection.cursor()
    cur.execute("select name from user where uid = {}".format(session['user']))
    data = cur.fetchone()
    cur.close()
    return render_template("CPasscodes.html", data=data)


@app.route('/CPasscodes1', methods=['GET', 'POST'])
def CPasscodes1():
    if 'user' not in session:
        flash("Please Login To Add Password", 'danger')
        return redirect('/login')
    if request.method == 'POST':
        url = request.form['URL']
        username = request.form['Username']
        passcode = request.form['passcode']

        if username == "":
            username = 'N/A'

        pyperclip.copy(passcode)
        flash('Password Copied', 'success')
        etext = get_pass(128)
        passcode = FrostCrypt(str(passcode), etext)
        Etext = FrostCrypt(str(etext), str(session['user']))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO main (url, username, passcode, uid, etext)VALUES ('{}','{}','{}',{},'{}')".format(
            url, username, passcode, session['user'], Etext))
        mysql.connection.commit()
        cur.close()

    cur = mysql.connection.cursor()
    cur.execute(
        "select name, username from user where uid = {}".format(session['user']))
    data = cur.fetchone()
    cur.close()
    return render_template("CPasscodes1.html", data=data)


@app.route('/mypasscodes', methods=['GET', 'POST'])
def mypasscodes():
    if 'user' not in session:
        flash("Please Login To Search Password", 'danger')
        return redirect('/login')
    if request.method == 'POST':
        url = str(request.form['URL'])
        cur = mysql.connection.cursor()
        cur.execute("select `url`, `username`, `primarykey`,`date_time` from main where `url` REGEXP '{}' and uid = {} order by `date_time` DESC".format(
            url, session['user']))
        data = cur.fetchall()
        cur.close()
        return render_template('mypasscodes.html', data=data)

    cur = mysql.connection.cursor()
    cur.execute(
        "Select * from main where uid = {} order by date_time DESC".format(session['user']))
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
        "select `passcode`,`etext` from main where `primarykey` = '{}' and `uid` = '{}' ORDER BY date_time DESC".format(primarykey,session['user']))
    data = cur.fetchone()  
    cur.close() 
    if data:
        etext = FrostDCrypt(data['etext'], str(session['user']))
        passcode = FrostDCrypt(data['passcode'], etext)
        try:
            pyperclip.copy(passcode)
        except(PermissionError):
            print("There is an error!")
        flash('Password Copied', 'success')
        return redirect('/mypasscodes')
    else: 
        return ('Ops Something Went Wrong')

    
    


@app.route('/delete/<primarykey>')
def delete(primarykey):
    if 'user' not in session:
        flash("Please Login", 'danger')
        return redirect('/login')
    cur = mysql.connection.cursor()
    cur.execute("delete from main where primarykey = {} and `uid` = {}".format(primarykey,session['user']))
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
        private_key = Secret_Key()
        SecKey = sha256_crypt.encrypt(str(private_key))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(name, email, password, username, privatekeys) VALUES(%s, %s, %s, %s, %s)",
                    (name, email, password, username, SecKey))
        mysql.connection.commit()

        cur.close()
        flash('You are successfully Registered', 'success')
        return render_template('SecretKeys.html', SecKey = private_key)

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
            if sha256_crypt.verify(passcode, password):
                session['user'] = uid
                flash('Successfully logged in', 'success')
                return redirect('/CPasscodes')
            else:
                flash('Invalid Log In', 'danger')
        else:
            flash('User not Found', 'danger')
    return render_template('Login.html')


# Forgot Password
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if 'user' in session:
        return redirect('/')
    else:
        if request.method == 'POST':
            SecKey = request.form['key']
            username = request.form['username']
            cur = mysql.connection.cursor()
            cur.execute(
                "select uid,privatekeys from user where username = %s", [username])
            data = cur.fetchone()
            cur.close()
            if data:
                privatekeys = data['privatekeys']
                uid = data["uid"]
                if sha256_crypt.verify(SecKey, privatekeys):
                    session['user'] = uid
                    flash('Successfully logged in', 'success')
                    return redirect('/ChangePassword')
                else:
                    flash('Invalid Private Key', 'danger')
            else:
                flash('User Not Found', 'danger') 
        return render_template('forgot_password.html')

@app.route('/ChangePassword', methods=['GET','POST'])
def ChangePassword():
    if "user" not in session:
        flash('Ops! something went wrong', 'danger')
        return redirect('/login')
    if request.method == 'POST':
        password = sha256_crypt.encrypt(str(request.form['password']))
        private_key = Secret_Key()
        SecKey = sha256_crypt.encrypt(str(private_key))
        cur = mysql.connection.cursor()
        cur.execute("update user set password = %s,privatekeys = %s where uid = %s",(str(password), SecKey,session['user']))
        mysql.connection.commit()
        cur.close()
        flash('Password changed','success')
        return render_template('SecretKeys.html', SecKey = private_key)
    return render_template('ChangePassword.html')


# LOGOUT ROUTE

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        flash('Logged Out', 'danger')
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
