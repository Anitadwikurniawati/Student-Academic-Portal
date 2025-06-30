from flask import Flask, redirect, url_for, request, render_template, session
import smtplib
import sqlite3
import binascii
from Crypto.Cipher import AES

app = Flask(__name__)
sqlite_file = 'DATABASE.sqlite'
globalFID = None
app.secret_key = 'thisisdatabase'

# Fungsi enkripsi
def encrypt(s):
    obj = AES.new(b'This is a key123', AES.MODE_CBC, b'This is an IV456')
    s1 = s.rjust(16, ',')
    u = obj.encrypt(s1.encode())
    bar = binascii.b2a_hex(u)
    return bar

# Fungsi dekripsi
def decryption(s):
    obj = AES.new(b'This is a key123', AES.MODE_CBC, b'This is an IV456')
    u = binascii.a2b_hex(s)
    u1 = obj.decrypt(u)
    ux = u1.decode().strip(',')
    return ux

@app.route('/')
@app.route('/<name>')
def index(name=None):
    return render_template('HomePage.html', session=session, text=name)

@app.route('/success/<name>')
def success(name):
    return name

@app.route('/signuppage')
def signuppage():
    return render_template('SignUp.html')

@app.route('/forgotpassword')
@app.route('/forgotpassword/<name>')
def forgotpassword(name=None):
    return render_template('Forgot.html', text=name)

@app.route('/login', methods=['POST', 'GET'])
def login():
    conn = sqlite3.connect(sqlite_file)
    conn.create_function('decryption', 1, decryption)
    c = conn.cursor()
    person = request.form.get('person', '')
    user1 = request.form['UserName']
    user = encrypt(user1)
    pwd1 = request.form['Password']
    pwd = encrypt(pwd1)

    if not person or not user or not pwd:
        error = "Any of the fields cannot be left blank"
        return redirect(url_for('index', name=error))

    if person == 'Student':
        c.execute("SELECT Password FROM StudentLoginTable WHERE UserName = ?", (user,))
        f = c.fetchall()
        if not f:
            error = "UserName is incorrect!"
            return redirect(url_for('index', name=error))

        for row in f:
            if row == (pwd,):
                c.execute("SELECT SID FROM StudentLoginTable WHERE UserName = ?", (user,))
                sid = c.fetchone()
                session['id'] = sid

                con = sqlite3.connect(sqlite_file)
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                cur.execute("SELECT StudentName FROM StudentLoginTable WHERE SID=?", sid)
                sname1 = cur.fetchone()

                con1 = sqlite3.connect(sqlite_file)
                con1.create_function('decryption', 1, decryption)
                con1.row_factory = sqlite3.Row
                cur1 = con1.cursor()
                cur1.execute(
                    "SELECT c.CourseName, decryption(g.MidTerm1) as mt1, decryption(g.MidTerm2) as mt2, decryption(g.MidTerm3) as mt3, decryption(g.FinalGrade) as fg "
                    "FROM GradeTable g INNER JOIN CourseTable c ON g.CourseId = c.CourseId WHERE g.SID=?"
