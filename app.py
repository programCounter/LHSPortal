#Include nessesary libraries
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from ports import check

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


#Check if user is logged in
def is_logged_in(f):
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
    pagename = ': Login'
    if request.method == 'POST':
        #Get Form Feilds
        username = request.form['username']
        passwordCandidate = request.form['password']

        #Create cursor
        cur = mysql.connection.cursor()

        #Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            #Get stored hash
            data = cur.fetchone()
            name = data['name']
            email = data['email']
            userID = data['id']
            password = data['password']

            #Compare Passwords
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
            #Close MySQL connection
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
    pagename = ': Logout'
    session.clear()
    flash('You are now logged out.', 'success')
    app.logger.info('User logged out.')
    app.logger.info('Session data cleared')
    return redirect(url_for('logIn'))


#User Registration
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
    pagename = ': Register'
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #Create Cursor
        cur = mysql.connection.cursor()

        #Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        #Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        #Flash message
        flash('You are now registered and can now login', 'success')
        app.logger.info('User has been registered and can now log in.')

        #return redirect(url_for('logIn'))
    return render_template('register.html', form=form, pagename=pagename)


#Edit Account
@app.route('/My_Account')
@is_logged_in
def My_Account():
    pagename = ': My Account'


    return render_template('My_Account.html', pagename=pagename)

#@app.route('/My_Account_verify', methods=['GET', 'POST'])
#@is_logged_in
#def My_Account_verify():
#    pagename = ': Edit Account'
#
#    #Confirm User
#    if request.method == 'POST':
#        #Get form Feilds
#        username = request.form['username']
#        passwordCandidate = request.form['password']
#
#        #Create cursor
#        cur = mysql.connection.cursor()
#
#        #Get user by username
#        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
#
#        if result > 0:
#            #Get stored hash
#            data = cur.fetchone()
#            password = data['password']
#
#            #Compare Passwords
#            if sha256_crypt.verify(passwordCandidate, password):
#                flash('Verified!', 'success')
#                return redirect(url_for('Edit_Account'))
#                app.logger.info('PASSWORD MATCHED')
#                app.logger.info('User verified. Redirecting...')
#            else:
#                error = 'Invalid login'
#                return render_template('My_Account.html', error=error)
#                app.logger.info('PASSWORD NOT MATCHED')
#                app.logger.info('User verify FAIL')
#            #Close MySQL connection
#            cur.close()
#
#        else:
#            error = 'Username not found'
#            return render_template('My_Account.html', error=error)
#            app.logger.info('NO USER')
#            app.logger.info('User verify FAIL')
#
#    return render_template('My_Acount_verify.html', pagename=pagename)

@app.route('/Edit_Account/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def Edit_Account(id):
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
    pagename = ': Home'

    #Create cursor
    cur = mysql.connection.cursor()

    #Get data
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
        app.logger.info('Port Check Script ran.')
        return render_template('home.html', pagename=pagename, portcheck=portcheck, state=state, Service=Service)
    else:
        msg = 'NO DATA FOUND'
        app.logger.info('No ports to check, database empty or not connected?')
        return render_template('home.html', pagename=pagename, msg=msg)

    #Close connection
    cur.close()


#Adding ports

class AddressForm(Form):
    IPAddress = StringField('IP Address', [validators.Length(min=1, max=50)])
    port = StringField('Port')
    ServiceName = StringField('ServiceName')

@app.route('/addPorts', methods=['GET', 'POST'])
@is_logged_in
def addPorts():
    pagename = ': addPorts'
    form = AddressForm(request.form)
    if request.method == 'POST' and form.validate():
        IPAddress = form.IPAddress.data
        port = form.port.data
        ServiceName = form.ServiceName.data

        #Create Cursor
        cur = mysql.connection.cursor()

        #Execute
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
    return render_template('mainPage.html')

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(host = '192.168.0.140', port = 5001)
