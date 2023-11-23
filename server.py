
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
from sqlalchemy import *
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
DATABASEURI = "postgresql://ihenetu:908176@34.75.94.195/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
#conn = engine.connect()
with engine.connect() as conn:
    with conn.begin():
# The string needs to be wrapped around text()

        conn.execute(text("""CREATE TABLE IF NOT EXISTS account_belongsto (
          uni text,
          accountid serial
        );"""))


        conn.execute(text("""
        INSERT INTO account_belongsto(accountid, uni)
        VALUES
          (10023423411, 'qwe1234'),
          (10024723422, 'wer2345'),
          (10067820402, 'ert3456'),
          (10020708002, 'tea2120'),
          (10011108202, 'pao6790'),
          (10018100002, 'jam6078'),
          (10099808101, 'bji8432'),
          (10080808008, 'bfe7406'),
          (10023323300, 'joo8920'),
          (10023325079, 'ton5079');
        """))
    conn.commit()
    
    with engine.connect() as conn:
        with conn.begin():
        
          conn.execute(text("""CREATE TABLE IF NOT EXISTS checkings_account (
            accountid serial,
            balance NUMERIC
          );"""))
          #conn.commit()

          conn.execute(text("""
          INSERT INTO checkings_acoount(accountid, balance)
          VALUES
            (10023423411, 5000),
            (10024723422, 6700),
            (10067820402, 506),
            (10020708002, 100),
            (10011108202, 250),
            (10018100002, 300),
            (10099808101, 10000),
            (10080808008, 350),
            (10023323300, 2000),
            (10023325079, 450);
          """))
    conn.commit()
    
    with engine.connect() as conn:
        with connection.begin():
          conn.execute(text("""CREATE TABLE IF NOT EXISTS dining_attachedto (
            accountid serial,
            swipes NUMERIC,
            dinning_dollars NUMERIC,
            points NUMERIC,
            flex NUMERIC,
            mealplanname text
          );"""))
        #conn.commit()

          conn.execute(text("""
          INSERT INTO dining_attachedto(accountid, swipes, dining_dollars, points, flex, mealplanname)
          VALUES
            (10023423411, 210, 100, 0, 100, 'PlanA'),
            (10024723422, 210, 100, 0, 100, 'PlanA'),
            (10067820402, 210, 100, 0, 100, 'PlanA'),
            (10020708002, 150, 75, 0, 75, 'PlanC'),
            (10011108202, 30, 0, 150, 0, 'BarPlanD'),
            (10018100002, 75, 0, 0, 75, 'GSPlan'),
            (10099808101, 125, 0, 400, 0, 'BarPlanB'),
            (10080808008, 0, 0, 500, 0, 'BarPlanE'),
            (10023323300, 210, 0, 0, 0, 'PlanA2'),
            (10023325079, 100, 0, 125, 0, 'PlanD');
          """))
    conn.commit()

    with engine.connect() as conn:
        with conn.begin():
          conn.execute(text("""CREATE TABLE IF NOT EXISTS has_plan (
            schoolcode text,
            mealplannname text
          );"""))
          

          conn.execute(text("""
          INSERT INTO has_plan(schoolcode, mealplanname)
          VALUES
            (2456, 'PlanA'),
            (2456, 'PlanB'),
            (2456, 'PlanC'),
            (2456, 'PlanD'),
            (2456, 'PlanA2'),
            (2456, 'PlanB2'),
            (2708, 'BarPlanA'),
            (2708, 'BarPlanB'),
            (2708, 'BarPlanC'),
            (2708, 'BarPlanD'),
            (2708, 'BarPlanE'),
            (2706, 'GSPlan'),
            (2707, 'PlanA'),
            (2707, 'PlanA2'),
            (2707, 'PlanB'),
            (2707, 'PlanB2'),
            (2707, 'PlanC'),
            (2707, 'PlanD');
          """))
    conn.commit()
    with engine.connect() as conn:
        with conn.begin():
          conn.execute(text("""CREATE TABLE IF NOT EXISTS institutions (
            school text,
            schoolcode text
          );"""))
          #conn.commit()

          conn.execute(text("""
          INSERT INTO institutions(school, schoolcode)
          VALUES
            ('Barnard College', 2708),
            ('Columbia College', 2456),
            ('General Studies', 2706),
            ('SEAS', 2707);
          """))
    conn.commit()
    with engine.connect() as conn:
        with connection.begin():
          conn.execute(text("""CREATE TABLE IF NOT EXISTS meal_plan (
            mealplanname text,
            swipes NUMERIC,
            flex NUMERIC,
            dinning_dollars NUMERIC,
            points NUMERIC
          );"""))
          #conn.commit()

          conn.execute(text("""
          INSERT INTO meal_plan(mealplanname, swipes, flex, dining_dollars, points)
          VALUES
            ('PlanA', 210, 100, 100, 0),
            ('PlanA2', 210, 0, 0, 0),
            ('PlanB', 175, 100, 100, 0),
            ('PlanB2', 175, 0, 200, 0),
            ('PlanC', 150, 75, 75, 0),
            ('PlanD', 100, 0, 125, 0),
            ('BarPlanA', 150, 0, 0, 625),
            ('BarPlanB', 125, 0, 0, 400),
            ('BarPlanC', 75, 0, 0, 200),
            ('BarPlanD', 30, 0, 0, 150),
            ('BarPlanE', 0, 0, 0, 500),
            ('GSPlan', 75, 0, 75, 0);
          """))
    conn.commit()
    with engine.connect() as conn:
        with connection.begin():
          conn.execute(text("""CREATE TABLE IF NOT EXISTS savings_account (
            accountid serial,
            balance NUMERIC
          );"""))
          #conn.commit()

          conn.execute(text("""
          INSERT INTO savings_account(accountid, balance)
          VALUES
            (10023423411, 30459),
            (10024723422, 25789),
            (10067820402, 40210),
            (10020708002, 10230),
            (10011108202, 45260),
            (10018100002, 23200),
            (10099808101, 37233),
            (10080808008, 94039),
            (10023323300, 76034),
            (10023325079, 66535);
          """))
    conn.commit()

    with engine.connect() as conn:
        with connection.begin():
          conn.execute(text("""CREATE TABLE IF NOT EXISTS transaction_acchis (
            transactionid serial,
            dateoftransaction Date,
            amount NUMERIC,
            location text,
            purpose text,
            accountid text,
            type text
          );"""))
          #conn.commit()

          conn.execute(text("""
          INSERT INTO transaction_acchis(transactionid, dateoftransaction, amount, location, purpose, accountid, type)
          VALUES
            (9764315, '2023-10-17', 1, 'grace dodge', 'lunch', 10067820402, 'swipe'),
            (2387469, '2023-10-02', 1, 'jjs', '2am snack', 10020708002, 'swipe'),
            (5641987, '2023-09-10', 1, 'chef dons', 'late lunch', 10011108202, 'swipe'),
            (7192834, '2023-09-10', 1, 'chef mikes', 'breakfast', 10018100002, 'swipe'),
            (3629157, '2023-09-04', 1, 'john jay', 'breakfast', 10099808101, 'swipe'),
            (4897263, '2023-09-04', 10, 'cafe east', 'sushi', 10080808008, 'points'),
            (6518274, '2023-09-15', 10, 'blue java', 'coffee', 10023323300, 'money'),
            (5738912, '2023-08-30', 10, 'blue java', 'coffee', 10023323300, 'flex'),
            (1245897, '2023-10-20', 1, 'Ferris', 'lunch', 10023423411, 'swipe'),
            (8357462, '2023-10-31', 1, 'john-jay', 'dinner', 10023423411, 'swipe');
          """))
    conn.commit()
    
    with engine.connect() as conn:
        with connection.begin():
          conn.execute(text("""CREATE TABLE IF NOT EXISTS user_attends (
            uni text,
            name text,
            username text,
            password text,
            schoolcode text
          );"""))
          #conn.commit()

          conn.execute(text("""
          INSERT INTO user_attends(uni, name, username, password, schoolcode)
          VALUES
            ('qwe1234', 'que', 'queEats', 'bubbles45', 2708),
            ('wer2345', 'willow', 'willowrah', 'camel99', 2708),
            ('ert3456', 'eliza', 'elizaTea', 'gelly34', 2708),
            ('tea2120', 'tiara', 'tiaraApple', 'caramel09', 2706),
            ('pao6790', 'patrick', 'pattyOprah', 'crystal78', 2707),
            ('jam6078', 'james', 'jmoney', 'bakery57', 2456),
            ('bji8432', 'benjamin', 'bennyBandz', 'kutie45', 2456),
            ('bfe7406', 'brown', 'brownErros', 'skyWall30', 2456),
            ('joo8920', 'joel', 'joelOlle', 'rippl3s78', 2706),
            ('ton5079', 'anthony', 'tonyGre', 'puddles35', 2708);
          """))

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

#
# Budget Tracker 1st attempt
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#  
#Route for budgetTracker
@app.route('/budgetTracker', methods=['GET'])
def budgetTracker():
    query = text("SELECT * FROM user_attends WHERE uni = :uni AND password = :password")
    login_data = engine.execute(query, uni=request.args.get('uni'), password = request.args.get('password')).fetchall()
    if login_data:
        return redirect("/budgetTracker/user_profile?uni=" + request.args.get('uni'))
    else:
        return "Invalid username or password"

# Route for User Profile
@app.route('/budgetTracker/user_profile', methods=['POST'])
def user_profile():
    query = text("SELECT * FROM user_attends WHERE uni = :uni")
    user_profile_data = engine.execute(query, uni=request.args.get('uni')).fetchall()
    return render_template("user_profile.html", data = user_profile_data)

# Route for Account Tracking
@app.route('/budgetTracker/savings', methods=['POST'])
def savings():
    with engine.connect() as conn:
      query = text("SELECT balance FROM savings_acount WHERE accountid = :accountid")
      savingsAccount_data = engine.execute(query, balance=request.args.get('balance')).fetchall()
      return render_template("account_tracking.html", data= savingsAccount_data)
      
@app.route('/budgetTracker/checkings', methods=['POST'])
def checkings():
    query = text("SELECT balance FROM checkings_account WHERE accountid = :accountid")
    checkingsAccount_data = engine.execute(query, balance=request.args.get('balance')).fetchall()
    return render_template("account_tracking.html", data= checkingsAccount_data)

@app.route('/budgetTracker/meal_plan', methods=['POST'])
def mealPlan():
    query = text("SELECT swipes, dining_dollars, points, flex FROM dining_attachedto WHERE accountid = :accountid")
    mealPlan_data = engine.execute(query, swipes=request.args.get('swipes'), 
                                   dining_dollars=request.args.get('dining_dollars'), 
                                    points=request.args.get('points'), flex=request.args.get('flex')).fetchall()
    return render_template("account_tracking.html", data= mealPlan_data)


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

