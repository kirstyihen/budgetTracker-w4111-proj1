
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
from flask import Flask, request, render_template, g, redirect, Response, abort

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


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI, pool_pre_ping=True)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
conn = engine.connect()
conn.commit()
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


#Route for budgetTracker
@app.route('/budgetTracker', methods=['GET'])
def budgetTracker():
   query = text("SELECT username,password FROM user_attends WHERE username = :username AND password = :password")
   login_cursor = engine.execute(query, username=request.args.get('username'), password=request.args.get('password'))
   login_data = login_cursor.fetchall()
   if request.args.get('username') not in login_data or login_data[request.args.get('username')] != request.args.get('password'):
      return "Invalid username or password"
   else:
      return redirect("/budgetTracker/user_profile?uni=" + request.args.get('username'))

   
  # login_data = {"queEats":"bubbles45", "willowrah":"camel99", "elizaTea":"gelly24", "tiaraApple":"caramel09", "pattyOprah":"crystal78", "jmoney":"bakery57", "bennyBandz": "kutie45", "brownErros":"skyWall30", "joelOlle":"rippl3s78", "tonyGre":"puddles35"}
  # if request.args.get('username') in login_data and login_data[request.args.get('username')] == request.args.get('password'):
  #     return redirect("/budgetTracker/user_profile?uni=" + request.args.get('username'))
  # else:
  #     return "Invalid username or password"


# Endpoint for User Profile
@app.route('/budgetTracker/user_profile/<username>', methods=['POST'])
def user_profile(username):
    query = text("SELECT * FROM user_attends WHERE uni = :uni")
    user_profile_data = engine.execute(query, uni=request.args.get('uni')).fetchall()
    return render_template("user_profile.html", data = user_profile_data)

@app.route('/budgetTracker/SignUp', methods= ['POST'])
def signUp():
   query = text("INSERT INTO user_attends(uni, name, username, password, schoolcode) VALUES (:uni, :name, :username, :password, :schoolcode)")  
   engine.execute(query, uni=request.args.get('uni'), name=request.args.get('name'), username=request.args.get('username'), password=request.args.get('password'), schoolcode=request.args.get('schoolcode'))
   
# Endpoint for Savings
@app.route('/budgetTracker/savings', methods=['GET','POST'])
def savings():
    with engine.connect() as conn:
      query = text("SELECT balance FROM savings_acount WHERE accountid = :accountid")
      savingsAccount_data = engine.execute(query, balance=request.args.get('balance')).fetchall()
      return render_template("user_profile.html", data= savingsAccount_data)
      
@app.route('/budgetTracker/checkings', methods=[ 'GET','POST'])
def checkings():
    query = text("SELECT balance FROM checkings_account WHERE accountid = :accountid")
    checkingsAccount_data = engine.execute(query, balance=request.args.get('balance')).fetchall()
    return render_template("user_profile.html", data= checkingsAccount_data)

@app.route('/budgetTracker/meal_plan', methods=['GET','POST'])
def mealPlan():
    query = text("SELECT swipes, dining_dollars, points, flex FROM dining_attachedto WHERE accountid = :accountid")
    mealPlan_data = engine.execute(query, swipes=request.args.get('swipes'), 
                                   dining_dollars=request.args.get('dining_dollars'), 
                                    points=request.args.get('points'), flex=request.args.get('flex')).fetchall()
    return render_template("user_profile.html", data= mealPlan_data)

@app.route('/budgetTracker/transactions_history', methods=['GET','POST'])
def transactionHistory():
    query = text("SELECT * FROM transaction_acchis WHERE accountid = :accountid")
    transaction_data = engine.execute(query, accountid=request.args.get('accountid')).fetchall()
    return render_template("account_tracking.html", data= transaction_data)

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

