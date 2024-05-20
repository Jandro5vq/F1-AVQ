#* [[[---- FLASK LIBRARIES ----]]]
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import *
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from flask_apscheduler import APScheduler
import config
#* [[[---- GENERAL LIBRARIES ----]]]
import datetime
#* [[[---- CUSTOM IMPORTS ----]]]
from fastf1Data import *
from dbIN import *
from dbOUT import *
#  ----- MODELS:
from models.ModelUser import ModelUser
# import models.ModelUser
#  ----- ENTITIES:
from models.entities.User import User

# =============== FLASK APP ================
app = Flask(__name__)
app.static_folder = 'static'

app.config['TRAP_HTTP_EXCEPTIONS']=True
app.config['SECRET_KEY']='6QUWcs*BZPcm&!@oT^tc'

#* ----------- DB / LOGIN MANAGER ----------
csrf = CSRFProtect()
db = MySQL(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Alejandro'
app.config['MYSQL_PASSWORD'] = '5122000'
app.config['MYSQL_DB'] = 'avqf1'
login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

#* ----------------- ROUTES ----------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/race', methods=['GET', 'POST'])
def race():
    return render_template('race.html', GDrivRes = dbGlobalDriverRes(db), GConRes = dbGlobalTeamRes(db), EndedGP = dbCompletedGP(db), ResPerGP= dbGetResPerGP(db), TeamResPerGP = dbGetTeamResPerGP(db))

@app.route('/bet', methods=['GET', 'POST'])
@login_required
def bet():
    return render_template('bet.html', DList = dbDriverList(db), UserList = dbGetUserPoints(db), Schedule = dbGetSchedule(db), EndedGP = dbCompletedGP(db))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        logged_user = ModelUser.login(db, request.form['username'], request.form['password'])
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user, remember= True)
                return redirect(url_for('bet'))
            else:
                flash("Invalid password...")
                return render_template('login.html')
        else:
            flash("User not found... Try registering first")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        ModelUser.register(db, request.form['username'], request.form['email'], request.form['password'], request.form['gender'] )
        return redirect(url_for('login'))
    else: 
        return render_template('register.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/db/update', methods=['POST', 'GET'])
def update():
    createScheduleTable(db)
    createTeamTable(db)
    createDriveTable(db)
    for x in range(lastGPNum() - 1):
        CreateGPRessTable(db, GPNum=(x + 1))
        CreateGPFastLaps(db, GPNum=(x + 1))
    print("========= DB UPDATED! =========")
    return redirect(url_for('home'))

#? --------------- DATA FETCH --------------
@app.route("/getgpres/<int:id>")
def getgpres(id):
    return dbGPRes(db, id)

@app.route("/getgpdat/<int:id>")
def getgpdat(id):
    return dbGPData(db, id)

@app.route("/getdlist")
def getdlist():
    return dbDriverList(db)

@app.route("/fastlaps/<int:id>")
def getfl(id):
    return dbFastLap(db, id)

@app.route("/SubmitBet/<string:userbet>", methods = ['POST', 'GET'])
def SubmitBet(userbet):
    bet = json.loads(userbet)
    AddBet(db, bet)
    return redirect(url_for('bet'))

@app.route("/getbet/<int:id>/<string:user>")
def getbet(id, user):
    return dbGetBet(db, user, id)

#! ---------------- TESTING ---------------
@app.route('/test', methods=['POST', 'GET'])
def test():
    print("===== TESTING =====")
    return redirect(url_for('home'))

#* ------------- ERROR HANDLER -------------
@app.errorhandler(401)
def status_401(error):
    return redirect(url_for('login'))

#* --------------- SCHEUDLES ---------------
scheduler = APScheduler()

@scheduler.task('cron', id='update_db', week='*', day_of_week='mon', hour ='00', minute='00')
def update_db():
    CreateLastGPResTable(db)
    CreateGPFastLaps(db)
    print('DB UPDATED!')

if __name__ == "__main__":
    app.config.from_object("config.DevelopmentConfig")
    app.register_error_handler(401, status_401)
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='0.0.0.0')


def run(app):
    app.config.from_object("config.DevelopmentConfig")
    app.register_error_handler(401, status_401)
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='0.0.0.0')