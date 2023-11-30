
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import create_engine, text 
from sqlalchemy.pool import NullPool
from flask import Flask, jsonify, request, render_template, g, redirect, Response, flash, session, url_for
import psycopg2, psycopg2.extras
from urllib.parse import urlparse

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'bankprogram-milly'
#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://mki2104:908176@34.74.171.121/proj1part2"


result = urlparse(DATABASEURI)
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port
conn = psycopg2.connect( database = database, user = username, password = password, host = hostname, port = port )

engine = create_engine(DATABASEURI, pool_pre_ping=True)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#Endpoint for budgetTracker
@app.route('/', methods=['GET','POST'])
def index():
  return render_template("index.html")


# Endpoint for Login 
@app.route('/login.html', methods=['POST', 'GET'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'uni' in request.form:
        uni = request.form['uni']
        username = request.form['username']
        name = request.form.get("name", "")  # Use get() to handle the case where 'name' is not present
        password = request.form['password']
        
        cursor.execute('SELECT username, password, uni, name FROM user_attends WHERE username = %s', (username,))
        profile = cursor.fetchone()

        if profile:
            uni_rs = profile['uni']
            # If account exists in users table in our database
            if uni_rs == uni:
                # Create session data, we can access this data in other routes
                session['uni'] = profile['uni']
                session['username'] = profile['username']
                
                # Check if 'name' key exists in the profile dictionary
                if 'name' in profile:
                    session['name'] = profile['name']
                else:
                    session['name'] = ""  # Provide a default value or handle it based on your application logic
                
                session['password'] = profile['password']

                # Flash the 'info' dictionary and redirect
                #flash({'uni': profile['uni'], 'name': session['name'], 'username': profile['username'], 'password': profile['password']})
                
                # Redirect to home page
                return redirect(url_for('user_profile', name=session['name']))

            else:
                # Account doesn't exist or uni/password incorrect
                flash('Incorrect uni or unknown account')
        else:
            # Account doesn't exist or uni/password incorrect
            flash('Incorrect uni or unknown account')

    # Add this return statement to handle the case where the conditions are not met
    return render_template('login.html')


# Endpoint for User Profile
@app.route('/user_profile.html', methods=['POST', 'GET'])
def user_profile():
    # Retrieve the data from the session
    uni = session.get('uni', "")
    name = session.get('name', "")
    username = session.get('username', "")
    password = session.get('password', "")

    #cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = text('SELECT u.schoolcode, i.school FROM user_attends u JOIN institutions i ON u.schoolcode = i.schoolcode WHERE u.uni = :uni ')
    params = {'uni': uni}
    result = g.conn.execute(query, params)
    g.conn.commit()
    #print(result)
    for i in result:
       schoolcode = i[0]
       schoolname = i[1]
   
    # Render the template with the retrieved data
    return render_template("user_profile.html", info={'uni': uni, 'name': name, 'username': username, 'password': password, 'schoolcode': schoolcode, 'schoolname': schoolname })




# Endpoint for Savings
@app.route('/savings', methods=['GET'])
def savings():
    uni = session.get('uni', "")
    #cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = text('SELECT ab.accountid, s.balance FROM savings_account s JOIN account_belongsto ab ON s.accountid = ab.accountid WHERE ab.uni = :uni')
    params = {'uni': uni}
    result = g.conn.execute(query, params)
    g.conn.commit()

    for i in result:
       accountid = i[0]
       balance = i[1]
       
    return render_template("user_profile.html", info = {'accountid': accountid, 'balance': balance})

#Endpoint for Checkings      
@app.route('/checkings', methods=['GET', 'POST'])
def checkings():
    uni = session.get('uni', "")
    #cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = text('SELECT ab.accountid, c.balance FROM checkings_account c JOIN account_belongsto ab ON c.accountid = ab.accountid WHERE ab.uni = :uni')
    params = {'uni': uni}
    result = g.conn.execute(query, params)
    g.conn.commit()

    for i in result:
       accountid = i[0]
       balance = i[1]
       
    return render_template("user_profile.html", info = {'accountid': accountid, 'balance': balance})


@app.route('/meal_plan', methods=['GET', 'POST'])
def mealPlan():

    uni = session.get('uni', "")
    query = text('SELECT swipes, dining_dollars, points, flex FROM dining_attachedto dat JOIN has_plan hp ON dat.accountid = hp.accountid JOIN account_belongsto ab ON hp.accountid = ab.accountid AND ab.uni = :uni')
    params = {'uni': uni}
    result = g.conn.execute(query, params)
    g.conn.commit()
    
    for i in result:
       swipes = i[0]
       dinning_dollars = i[1]
       points = i[2]
       flex = i[3]
       mealplanname = i[4]
    
  # Handle the case where dinningdata is None
    return render_template("user_profile.html", dict = {'swipes': swipes, 'dining_dollars': dinning_dollars, 'points': points, 'flex': flex, 'mealplanname': mealplanname})


@app.route('/account_tracking.html', methods=['GET','POST'])
def transactionHistory():
    uni = session.get('uni', "")
    query = text('SELECT * FROM transaction_acchis ta JOIN account_belongsto ab ON ta.accountid = ab.accountid AND ab.uni = :uni')
    params = {'uni': uni}
    result = g.conn.execute(query, params)
    g.conn.commit()
    
    for i in result:
       transactionid = i[0]
       dateoftransaction = i[1]
       amount = i[2]
       location = i[3]
       purpose = i[4]
       accountid = i[5]
       typ = i[6]

    return render_template("account_tracking.html", dict = {'transactionid': transactionid, 'dateoftransaction':dateoftransaction, 'amount': amount, 'location': location, 'purpose': purpose, 'accountid': accountid, 'typ': typ} )


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """
   
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()


