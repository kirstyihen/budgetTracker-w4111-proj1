
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
from flask import Flask, jsonify, request, render_template, g, redirect, Response, abort, session
import psycopg2, psycopg2.extras
from urllib.parse import urlparse

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

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
uni = result.username
database = result.path[1:]
hostname = result.hostname
port = result.port
conn = psycopg2.connect( database = database, uni = uni, host = hostname, port = port )

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

def isValidUni(uni):
    validUni = False
    with engine.connect() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT EXISTS(SELECT 1 FROM user_attends WHERE uni = %s)", (uni,))
        validUni = cursor.fetchone()[0]
    return validUni


@app.route('/login.html', methods=['POST', 'GET'])
def login():
    with engine.connect() as conn:
        if request.method == 'POST':
            if "uni" not in request.form:
                return jsonify(valid=False)
            
            uni = request.form["uni"]
            session[uni] = uni
            name = request.form["name"]
            session[name] = name

            if not isValidUni(uni):
                return jsonify(valid=False)
            else:
                return redirect("/user_profile.html/{}".format(name))
        else:
            return render_template("login.html")

# Endpoint for User Profile
@app.route('/user_profile.html/{}', methods=['POST', 'GET'])
def user_profile(name):
    with engine.connect() as conn:
        if request.method == 'POST':
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("SELECT u.name FROM user_attends u JOIN institutions i ON u.uni = i.uni WHERE u.uni = :uni AND u.name = :name")
            profile = cursor.fetchone()

            p = []
            for value in profile:
               p.append(value)
            info = {'uni': p[0], 'name': p[1], 'username':p[2], 'password':p[3],'schoolcode':[4]}
            return render_template("user_profile.html",  **info)  
    return render_template("user_profile.html/{}" **info)

# Endpoint for Savings

@app.route('/savings', methods=['GET'])
def savings():
  with engine.connect() as conn:
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT balance FROM savings_account s JOIN account_belongsto ab ON s.accountid = ab.accountid WHERE ab.accountid = %s'", (session['accountid']))
    balance = cursor.fetchone()
    
  return render_template ("user_profile.html/{}", balance = balance)

#Endpoint for Checkings      
@app.route('/checkings', methods=['POST'])
def checkings():
  with engine.connect() as conn:
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT balance FROM checkings_account c JOIN account_belongsto ab ON c.accountid = ab.accountid WHERE ab.accountid = :accountid")
    balance = cursor.fetchone()
  return render_template ("user_profile.html/{}", balance = balance)

@app.route('/meal_plan', methods=['GET','POST'])
def mealPlan():
  with engine.connect() as conn:
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("SELECT swipes, dining_dollars, points, flex FROM dining_attachedto WHERE accountid = :accountid")
    dinningdata = cursor.fetchone()

    dd = []
    for value in dinningdata:
       dd.append(value)
      
    cursor.execute("SELECT mp.* FROM meal_plan mp JOIN has_plan hp ON mp.mealplanname = hp.mealplanname")
    mealplanname = cursor.fetchone()
    dict = {'swipes': dd[0], 'dining_dollars': dd[1], 'points': dd[2], 'flex': dd[3], 'mealplanname' : mealplanname}        
  return render_template("user_profile.html", **dict)

@app.route('/account_tracking.html', methods=['GET','POST'])
def transactionHistory():
  with engine.connect() as conn:
     cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
     cursor.execute("SELECT * FROM transaction_acchis WHERE accountid = :accountid")
     transactionHistorydata = cursor.fetchone()
     tH = []
     for value in transactionHistorydata:
        tH.append(value)

        dict = {'transactionid': tH[0], 'dateoftransaction':tH[1], 'amount': tH[2], 'location': tH[3], 'purpose': tH[4], 'accountid': tH[5], 'type': tH[6]}
  return render_template("account_tracking.html", **dict)


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


