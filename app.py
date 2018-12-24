#Include nessesary libraries
from flask import Flask, render_template, flash, redirect, url_for, session, logging, jsonify, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from ports import check
import psutil
import time
from SYSresources import ReadSYS

#App definition
app = Flask(__name__)
app.debug = True

#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'yeet'
app.config['MYSQL_DB'] = 'LHSWeb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Init MYSQL
mysql = MySQL(app)


def is_logged_in(f):
    """
    Checks to see if user is logged into current session.
    If not, deniy accsess to page that calls this before render_template.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorised, please login to continue.', 'danger')
            return redirect(url_for('logIn'))
    return wrap


#User Login/logout
@app.route('/login', methods=['GET', 'POST'])
def logIn():
    """
    Accsess the db for user data, and crosschecks the cridentials inputed into fourm.
    If data matches, set parameters and start session. Store user data into current session for easy accsess.
    """

    pagename = ': Login'
    if request.method == 'POST':
        username = request.form['username']
        passwordCandidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            name = data['name']
            email = data['email']
            userID = data['id']
            password = data['password']

            if sha256_crypt.verify(passwordCandidate, password):
                session['logged_in'] = True
                session['username'] = username
                session['name'] = name
                session['email'] = email
                session['userID'] = userID
                flash('You are now logged in!', 'success')
                return redirect(url_for('Home'))
                app.logger.info('PASSWORD MATCHED')
                app.logger.info('User logged in!')
                app.logger.info('Session Data Updated')
            else:
                error = 'Invalid login'
                return render_template('logIn.html', error=error)
                app.logger.info('PASSWORD NOT MATCHED')
                app.logger.info('User login failed!')
                app.logger.info('Session data unchanged')
            cur.close()

        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
            app.logger.info('NO USER')
            app.logger.info('User login failed!')

    return render_template('logIn.html', pagename=pagename)

@app.route('/logout')
@is_logged_in
def logout():
    """
    If user calls to logout, clear the current session and flush it of user data.
    Inform the user of the action and re-direct to login page.
    """

    pagename = ': Logout'
    session.clear()
    flash('You are now logged out.', 'success')
    app.logger.info('User logged out.')
    app.logger.info('Session data cleared')
    return redirect(url_for('logIn'))


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=5, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Request account creation fourm and make connection to db.
    Encrypt password and commit data to db and inform the user of the action.
    """

    pagename = ': Register'
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        mysql.connection.commit()
        cur.close()

        flash('You are now registered and can now login', 'success')
        app.logger.info('User has been registered and can now log in.')

    return render_template('register.html', form=form, pagename=pagename)


#Edit Account
@app.route('/My_Account')
@is_logged_in
def My_Account():
    """
    Returns render template for account information.
    Information is pulled from current session.
    """

    pagename = ': My Account'
    return render_template('My_Account.html', pagename=pagename)


@app.route('/Edit_Account/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def Edit_Account(id):
    """
    Create DOCSTRING HERE!
    """

    pagename = ': Edit Account'

    #Create cursor
    cur = mysql.connection.cursor()

    #Get all data matching user id
    result = cur.execute("SELECT * from users WHERE id= %s", [id])
    Edit = cur.fetchone()

    #Close Cursor
    cur.close()

    #Get form
    form = RegisterForm(request.form)

    #Populate feilds
    #Password can not be shown. sha256_crypt is a one way cryptography.
    form.name.data = Edit['name']
    form.username.data = Edit['username']
    form.email.data = Edit['email']


    #If changes are made update the database
    if request.method == 'POST' and form.validate():
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = sha256_crypt.encrypt(str(request.form['password']))

        app.logger.info(name)
        app.logger.info(username)
        app.logger.info(email)
        app.logger.info(password)

        #Create cursor
        cur = mysql.connection.cursor()

        #Execute changes
        cur.execute("UPDATE users SET name=%s, username=%s, email=%s, password=%s WHERE id=%s", (name, username, email, password, [id]))

        #Commit changes
        mysql.connection.commit()
        app.logger.info('User changes commited to database.')

        #Close Cursor
        cur.close()

        return redirect(url_for('My_Account'))

    return render_template('Edit_Account.html', pagename=pagename, form=form)


#Dashbord
@app.route('/Home')
@is_logged_in
def Home():
    """
    Create DOCSTRING HERE!
    """

    pagename = ': Home'

    cur = mysql.connection.cursor()
    results = cur.execute("SELECT * FROM portcheck")
    portcheck = cur.fetchall()

    if results > 0:
        cur.execute("SELECT IPAddress FROM portcheck")
        IPs = []

        for row in cur:
            IPs.append(row)

        cur.execute("SELECT Port FROM portcheck")
        Ports = []

        for row in cur:
            Ports.append(row)

        cur.execute("SELECT ServiceName FROM portcheck")
        Service = []

        for row in cur:
            Service.append(row)

        i = 0
        state = []
        for row in cur:
            stat = check((IPs[i]["IPAddress"]), (Ports[i]["Port"]))
            state.append(stat)
            i = i + 1
        app.logger.info('EXTERNAL SCRIPT RAN: check')

        CPUcount, ThreadCount, CPUTotalUse, CPUTotalFrequency, CPUusePerCore, RAMuse, MountedPartitions, RootDisk = ReadSYS()

        return render_template('home.html', pagename=pagename, portcheck=portcheck, state=state, Service=Service, CPUcount=CPUcount, ThreadCount=ThreadCount, CPUTotalUse=CPUTotalUse, CPUTotalFrequency=CPUTotalFrequency, CPUusePerCore=CPUusePerCore, RAMuse=RAMuse, MountedPartitions=MountedPartitions, RootDisk=RootDisk)
    else:
        msg = 'NO DATA FOUND'
        app.logger.info('No ports to check, database empty or not connected?')
        return render_template('home.html', pagename=pagename, msg=msg, CPUcount=CPUcount, ThreadCount=ThreadCount, CPUTotalUse=CPUTotalUse, CPUTotalFrequency=CPUTotalFrequency, CPUusePerCore=CPUusePerCore, RAMuse=RAMuse, MountedPartitions=MountedPartitions, RootDisk=RootDisk)

    cur.close()


class AddressForm(Form):
    IPAddress = StringField('IP Address', [validators.Length(min=1, max=50)])
    port = StringField('Port')
    ServiceName = StringField('ServiceName')


@app.route('/addPorts', methods=['GET', 'POST'])
@is_logged_in
def addPorts():
    """
    Create DOCSTRING HERE!
    """

    pagename = ': addPorts'
    form = AddressForm(request.form)
    if request.method == 'POST' and form.validate():
        IPAddress = form.IPAddress.data
        port = form.port.data
        ServiceName = form.ServiceName.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO portcheck(IPAddress, Port, ServiceName) VALUES(%s, %s, %s)", (IPAddress, port, ServiceName))

        #Commit to DB
        mysql.connection.commit()
        app.logger.info('New port commited to database.')

        #Close connection
        cur.close()

        flash('IP and Port Added to check list!')
        return redirect(url_for('Home'))
    return render_template('addPorts.html', pagename=pagename, form=form)


@app.route('/editPort/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def editPort(id):
    """
    Create DOCSTRING HERE!
    """

    #Create cursor
    cur = mysql.connection.cursor()

    #Get IP by ID
    result = cur.execute("SELECT * from portcheck WHERE id= %s", [id])
    Edit = cur.fetchone()

    app.logger.info(Edit)

    #Get form
    form = AddressForm(request.form)

    #Populate feilds
    form.ServiceName.data = Edit["ServiceName"]
    form.IPAddress.data = Edit["IPAddress"]
    form.port.data = Edit["Port"]

    if request.method == 'POST' and form.validate():
        ServiceName = request.form['ServiceName']
        IPAddress = request.form['IPAddress']
        port = request.form['port']

        #Create cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute("UPDATE portcheck SET ServiceName=%s, IPAddress=%s, Port=%s WHERE id=%s", (ServiceName, IPAddress, port, [id]))

        #Commit changes
        mysql.connection.commit()
        app.logger.info('Port changes commited to database.')

        #Close connection
        cur.close()

        flash('Service Updated!', 'success')
        return redirect(url_for('Home'))
    return render_template('editPort.html', form=form)


@app.route('/deleteIP/<string:id>', methods=['POST'])
@is_logged_in
def deleteIP(id):
    """
    Create DOCSTRING HERE!
    """

    #Create cursor
    cur = mysql.connection.cursor()

    #Execute
    cur.execute("DELETE FROM portcheck WHERE id=%s", [id])

    #Commit changes
    mysql.connection.commit()
    app.logger.info('Delete entry from database commited.')

    #Close connection
    cur.close()

    flash('IP and Port Deleted!', 'success')
    return redirect(url_for('Home'))


#Main site page

@app.route('/')
def mainPage():
    """
    Create DOCSTRING HERE!
    """

    #Create cursor
    cur = mysql.connection.cursor()

    #Get data
    #Service name data is not needed here. It is gathered during for loop in HTML file.
    results = cur.execute("SELECT * FROM portcheck")
    portcheck = cur.fetchall()

    if results > 0:
        cur.execute("SELECT IPAddress FROM portcheck")
        IPs = []

        for row in cur:
            IPs.append(row)

        cur.execute("SELECT Port FROM portcheck")
        Ports = []

        for row in cur:
            Ports.append(row)

        i = 0
        state = []
        for row in cur:
            stat = check((IPs[i]["IPAddress"]), (Ports[i]["Port"]))
            state.append(stat)
            i = i + 1
        app.logger.info("Port check script ran. PUBLIC")
        return render_template('mainPage.html', portcheck=portcheck, state=state)
    else:
        msg = "NO DATA FOUND"
        app.logger.info("No ports to check, database empty or not connected?")
        return render_template('mainPage.html', msg=msg)

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(host = '192.168.0.130', port = 5001)
