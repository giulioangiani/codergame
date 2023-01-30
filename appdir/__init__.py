from flask import Flask, g, redirect, url_for, escape, request, session, send_from_directory, render_template, send_file, make_response
import sys
import random
import pprint
import time
import os
import json
import traceback
import zipfile
import hashlib

#from flask_sslify import SSLify
#from OpenSSL import SSL
from sqlalchemy import create_engine, MetaData, Table

## protection by login
from functools import wraps

from jinja2.filters import FILTERS, environmentfilter

# just for user checking...
from sqlalchemy.orm import mapper, relationship, sessionmaker
from config import engine
from models import Utente
metadata = MetaData(bind=engine)
Session = sessionmaker(bind = engine)
dbsession = Session()

def protected(fnz):
	@wraps(fnz)
	def f(*args, **kwargs):
		if not session.get("USER"):
			return login(*args, **kwargs)
		global USER
		USER = session.get("USEROBJ")	# dict userinfo
		print("USER ", USER["username"], request.url)
		return fnz(*args, **kwargs)
	return f

import admin


VERSION = "1.0.0"
app = Flask(__name__)
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
app.secret_key = "labelSecretKet2021"
app.config["TEMPLATES_AUTO_RELOAD"] = True	# ricarica i templates dinamicamente

@environmentfilter
def multilinequery(environment, s):
    """Custom filter"""
    return s.lower().replace("\n", "<br>").replace(" from ", "<br>from ").replace(" where ", "<br>where ").replace(" order by ", "<br>order by ").replace(" having ", "<br>having ")
FILTERS["multilinequery"] = multilinequery

import models
from flask.signals import request_finished
def expire_session(sender, response, **extra):
	dbsession.expire_all()
#	import importlib
#	importlib.reload(dashboard)
#	importlib.reload(models)
#	importlib.reload(admin)
request_finished.connect(expire_session, app)

import dashboard
import codergame
from costanti import *
import importlib

from config import engine, metadata
Users = Table('utenti', metadata, autoload=True)

def errormsg(msg, info='info', specmsg=''):
	return render_template("error_msg.html", msg=msg, tipoinfo=info, specmsg=specmsg)

def checkUser(username, password):
	obj = dbsession.query(Utente).filter_by(username=username)
	if not obj.count():
		return None
	u = obj[0]
	if not u.checkPassword(password):
		return None
	else:
		return {
				"username": username,
				"userid": u.id,
				"description": u.description,
				"role": u.role,
				"preferences": {
					"lang": "IT",
				},
			}

@app.route('/')
@app.route('/home')
@protected
def home():

	if session["USEROBJ"]["role"] != 'ADMIN' and time.strftime("%Y-%m-%d--%H:%M:%S")<"2022-01-25--08:00:00": 	
		return render_template("close.html", MAIN_APP_TITLE=MAIN_APP_TITLE)
	
	return render_template("home.html", MAIN_APP_TITLE=MAIN_APP_TITLE, LOGIN_APP_DESCRIPTION=LOGIN_APP_DESCRIPTION)
	
@app.route('/login')
def login():
	print("LOGIN_APP_DESCRIPTION=", LOGIN_APP_DESCRIPTION)
	print("MAIN_APP_TITLE=", MAIN_APP_TITLE)
	return render_template("login_cg.html", MAIN_APP_TITLE=MAIN_APP_TITLE, LOGIN_APP_DESCRIPTION=LOGIN_APP_DESCRIPTION)


@app.route('/register')
def register_main():
	return render_template("register.html", **vars())

@app.route('/register/save', methods=["POST"])
def register_save():
	importlib.reload(register)
	(status, html) = register.save(session)
	return genericJsonResponse(status, html)

@app.route('/register/activate')
def register_confirm():
	importlib.reload(register)
	return register.activate(session)

@app.route('/check', methods=['POST'])
def check():
	username = request.form.get('usr', "")
	password = request.form.get('pwd', "")
	print("In check")

	result = {
		"status": "KO"
	}
	userinfo = checkUser(username, password)
	if userinfo:
		session["USER"] = username
		session["USEROBJ"] = userinfo
		result["status"] = "OK"

	return json.dumps(result)

@app.route('/logout')
def logout():
	print(session.items())
	print(session.keys())
	try:
		del session["USER"]
		del session["USEROBJ"]
		del session["U"]
	except:
		print("NO KEYS PRESENT")
	return home()

@app.route('/images/<path:path>')
def send_images(path):
	return send_from_directory('images', path)

@app.route('/static/<path:path>')
def send_static(path):
	return send_from_directory('static', path)



####################################################
@app.route('/dashboard', methods=["GET"])
@protected
def dashboard_home():
	import importlib
	importlib.reload(dashboard)
	(status, html) = dashboard.home(session)
	return genericJsonResponse(status, html)


@app.route('/view/<int:idelaborato>', methods=["GET"])
@protected
def dashboard_view(idelaborato):
	import importlib
	importlib.reload(dashboard)
	(status, html) = dashboard.view(session, idelaborato)
	return genericJsonResponse(status, html)


@app.route('/setvalutazione', methods=["POST"])
@protected
def dashboard_setvalutazione():
	import importlib
	importlib.reload(dashboard)
	(status, html) = dashboard.setvalutazione(session)
	return genericJsonResponse(status, html)

####################################################
@app.route('/codergame', methods=["GET"])
@protected
def codergame_home():
	import importlib
	importlib.reload(codergame)
	(status, html) = codergame.home(session)
	return genericJsonResponse(status, html)

@app.route('/codergame/form/<quizid>', methods=["GET"])
@protected
def codergame_form(quizid):
	import importlib
	importlib.reload(codergame)
	(status, html) = codergame.form(session, quizid)
	return genericJsonResponse(status, html)

@app.route('/codergame/uploadfile', methods=["POST"])
@protected
def codergame_uploadfile():
	import importlib
	importlib.reload(codergame)
	(status, html) = codergame.uploadfile(session)
	return genericJsonResponse(status, html)

@app.route('/codergame/results', methods=["GET"])
@protected
def codergame_results():
	import importlib
	importlib.reload(codergame)
	(status, html) = codergame.results(session)
	return genericJsonResponse(status, html)




### ADMIN

@app.route('/admin/home', methods=["GET"])
@protected
def admin_home():
	(status, html) = admin.home(session)
	return genericJsonResponse(status, html)

@app.route('/admin/uploadusers', methods=["GET"])
@protected
def admin_uploadusers():
	(status, html) = admin.uploadusers(session)
	return genericJsonResponse(status, html)
	

@app.route('/admin/uploadusers/execute', methods=["POST"])
@protected
def admin_uploadusers_execute():
	(status, html) = admin.uploadusers_execute(session)
	return genericJsonResponse(status, html)	
	
@app.route('/admin/students', methods=["GET"])
@protected
def admin_studenti():
	(status, html) = admin.students(session)
	return genericJsonResponse(status, html)

@app.route('/admin/results', methods=["GET"])
@protected
def admin_risultati():
	(status, html) = admin.risultati(session)
	return genericJsonResponse(status, html)

@app.route('/admin/groups', methods=["GET"])
@protected
def admin_groups():
	(status, html) = admin.groups(session)
	return genericJsonResponse(status, html)

@app.route('/admin/group/new/<object_id>', methods=["GET"])
@protected
def admin_group_new(object_id):
	(status, html) = admin.group_new(session)
	return genericJsonResponse(status, html)

@app.route('/admin/group/edit/<object_id>', methods=["GET"])
@protected
def admin_group_edit(object_id):
	(status, html) = admin.group_edit(session, object_id)
	return genericJsonResponse(status, html)
	
@app.route('/admin/group/update/<object_id>', methods=["POST"])
@protected
def admin_group_update(object_id):
	(status, html) = admin.group_update(session, object_id)
	return genericJsonResponse(status, html)

@app.route('/admin/group/removestudent/<group_id>/<user_id>', methods=["GET"])
@protected
def admin_group_removestudent(group_id, user_id):
	(status, html) = admin.group_removestudent(session, group_id, user_id)
	return genericJsonResponse(status, html)
	
	
@app.route('/admin/submissions', methods=["GET"])
@protected
def admin_submissions():
	(status, html) = admin.submissions(session)
	return genericJsonResponse(status, html)

@app.route('/admin/submission/delete/<submission_id>', methods=["GET"])
@protected
def admin_submissions_delete(submission_id):
	print("QUI")
	(status, html) = admin.submissions_delete(session, submission_id)
	return genericJsonResponse(status, html)

@app.route('/admin/tasks', methods=["GET"])
@protected
def admin_tasks():
	(status, html) = admin.tasks(session)
	return genericJsonResponse(status, html)

@app.route('/admin/task/edit/<object_id>', methods=["GET"])
@protected
def admin_task_edit(object_id):
	(status, html) = admin.task_edit(session, object_id)
	return genericJsonResponse(status, html)

@app.route('/admin/task/new/<object_id>', methods=["GET"])
@protected
def admin_task_new(object_id):
	(status, html) = admin.task_new(session)
	return genericJsonResponse(status, html)

@app.route('/admin/task/update/<object_id>', methods=["POST"])
@protected
def admin_task_update(object_id):
	(status, html) = admin.task_update(session, object_id)
	return genericJsonResponse(status, html)

@app.route('/admin/task/addtestcase', methods=["POST"])
@protected
def admin_task_addtestcase():
	(status, html) = admin.task_addtestcase(session)
	return genericJsonResponse(status, html)


@app.route('/admin/task/export/testcases/<object_id>', methods=["GET"])
@protected
def admin_task_export_testcases(object_id):
	return admin.task_export_testcases(session, object_id)

	
@app.route('/admin/task/duplica/<object_id>', methods=["GET"])
@protected
def admin_task_duplica(object_id):
	(status, html) = admin.task_duplica(session, object_id)
	return genericJsonResponse(status, html)


@app.route('/admin/task/assegna/<object_id>', methods=["GET"])
@protected
def admin_task_assegna(object_id):
	(status, html) = admin.task_assegna(session, object_id)
	return genericJsonResponse(status, html)

@app.route('/admin/task/abilita', methods=["POST"])
@protected
def admin_task_abilita():
	(status, html) = admin.task_abilita(session)
	return genericJsonResponse(status, html)

@app.route('/admin/task/disabilita', methods=["POST"])
@protected
def admin_task_disabilita():
	(status, html) = admin.task_disabilita(session)
	return genericJsonResponse(status, html)

@app.route('/admin/group/abilitazione/<mode>/<object_id>', methods=["GET"])
@protected
def admin_group_abilitazione(mode, object_id):
	(status, html) = admin.group_abilitazione(session, mode, object_id)
	return genericJsonResponse(status, html)



### IMPOSTAZIONI
@app.route('/settings')
@protected
def settings():
	import settings
	import importlib
	importlib.reload(settings)
	(status, html) = settings.home(session)
	return genericJsonResponse(status, html)

@app.route('/settings/update', methods=["POST"])
@protected
def settings_update():
	import settings
	import importlib
	importlib.reload(settings)
	(status, html) = settings.update(session, request=request)
	return genericJsonResponse(status, html)


def genericJsonResponse(status, html):
	if models.conn:
		#print("closing ", models.conn)
		models.conn.close()
	result = {
		"status": status,
		"html": html
	}
	return json.dumps(result)
