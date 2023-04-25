from datetime import datetime
import hashlib
import os
from venv import logger
from services import Services
import logging
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    send_file,
    session,
    url_for,
)
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logging.info('Application started')

template_dir = os.path.abspath('/home/imad/Documents/python/Ouafellaoui_Imad/Templates')
app = Flask(__name__, template_folder=template_dir, static_folder='static')
app.secret_key = "1234"
def generate_key(login):
    return hashlib.md5(str(login).encode('utf-8')).hexdigest()

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/home/<name>')
def home(name):
    ser.getContent(name)
    first_key = next(iter(ser.index))
    path = ser.index[first_key]
    if os.path.isdir(first_key):
        return render_template("home.html", db=path, Space=ser.get_nb_of_Dirs()["Space"], Dirs=ser.get_nb_of_Dirs()["Dirs"], Files=ser.get_nb_of_Dirs()["Files"],texte="")
    else :
       return render_template("home.html", db=[], Space="", Dirs="", Files="",texte=ser.Cat_File(first_key))

@app.route('/Rechercher')
def rechercher():
    keyword = request.args.get('keyword')
    return render_template('home.html', db=ser.rechercher(keyword), Space=ser.get_nb_of_Dirs_by_Keyword(keyword)["Space"], Dirs=ser.get_nb_of_Dirs_by_Keyword(keyword)["Dirs"], Files=ser.get_nb_of_Dirs_by_Keyword(keyword)["Files"],text="")

@app.route('/telecharger')
def download_home_dir():
    path=ser.Compresser_zip()
    logging.info('Home directory downloaded')
    return send_file(path, as_attachment=True)


@app.route('/logout')
def logout():
    logger.info('User %s logged out', session.get('user_id'))
    session.pop('user_id',None)
    ser.index={}
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    try:
        _res = ser.Connecter_User(username, password)
        if _res:
            app.secret_key=generate_key(login)
            session['user_id'] = username
            response = app.make_response(redirect(url_for('home', name=username)))
            response.set_cookie('access_time', str(datetime.now()))
            logging.info('Successful login for user: %s', username)
            return response
        else:
            logging.warning('Failed login attempt for user: %s', username)
            return render_template('login.html', error_auth='login or password incorrect')
    except Exception as e:
        logging.error('Exception occurred during login: %s', str(e))
        return render_template('login.html', error_auth=str(e))


@app.route('/CreerUser', methods=['GET'])
def creer_user():
    return render_template('creer_user.html')

@app.route('/create_user', methods=['POST', 'GET'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        success = ser.Creer_User(username, password1, password2)
        if success == 'Utilisateur bien ajouté':
            return redirect(url_for('index'))
        else:
            return render_template('creer_user.html', error_create=success)
    else:
        return render_template('creer_user.html')
    
@app.route('/back')
def back():
    ser.modifier_key()
    first_key = next(iter(ser.index))
    return render_template("home.html", db=ser.index[first_key], Space=ser.get_nb_of_Dirs()["Space"], Dirs=ser.get_nb_of_Dirs()["Dirs"], Files=ser.get_nb_of_Dirs()["Files"],texte="")

if __name__ == '__main__':
    ser = Services()
    logging.basicConfig(filename='app.log', level=logging.INFO)
    app.run(host='0.0.0.0', port=8080, debug=True)
