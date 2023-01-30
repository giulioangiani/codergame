from flask import Flask, g, redirect, url_for, escape, request, session, send_from_directory, render_template, send_file, jsonify
from tools import initialize, hashify
from sqlalchemy import Table, Column, Integer, String, create_engine, MetaData
from sqlalchemy.orm import mapper, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
import random

import importlib
import models
importlib.reload(models)
from models import *
import time
import json
from csv import DictReader

from costanti import *

@initialize
def home(session, USER=None):
	subtitle = ""
	pagetitle= "Dashboard"
	return "OK",  render_template("ajax_admin_home.html", **vars())
	
@initialize
def uploadusers(session, USER=None):
	subtitle = ""
	pagetitle= "Uploading users"
	gruppi = dbsession.query(Gruppo).all()
	return "OK",  render_template("ajax_admin_uploadusers.html", **vars())

@initialize
def uploadusers_execute(session, USER=None):
	import io
	codefile = request.files["codefile"]
	contenuto_codefile = io.BytesIO(codefile.read())
	content = contenuto_codefile.read()
	fname = MAIN_UPLOAD_USERS_DIR + time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
	open(fname, 'wb').write(content)
	
	group_id = request.form.get('group_id', '')
	if not group_id:
		return "KO", "Devi selezionare obbligatoriamente il gruppo "
	cont = 0
	with open(fname, 'r') as read_obj:
		# pass the file object to reader() to get the reader object
		csv_reader = DictReader(read_obj)
		# Iterate over each row in the csv using reader object
		for row in csv_reader:
			# row variable is a list that represents a row in csv
			u = Utente()
			u.username = row["username"]
			u.setNewPassword(row["password"])
			u.description = row["firstname"].capitalize() + " " + row["lastname"].capitalize()
			u.cognome = row["lastname"]
			u.nome = row["firstname"]
			u.role = 'GUEST'
			u.gruppo_id = group_id
			dbsession.add(u)
			cont += 1
		dbsession.commit()
			
	return "OK",  render_template("ajax_admin_uploadusers_confirm.html", **vars())

@initialize
def students(session, USER=None):
	subtitle = ""
	pagetitle= " Lista studenti "
	studenti = dbsession.query(Utente).order_by(Utente.cognome.asc()).filter_by(role='GUEST').all()
	gruppi = dbsession.query(Gruppo).all()
	
	dic_results = {}
	num_results = {}
	punti_per_studente = {}
	max_punti_per_studente = {}
	for s in studenti:
		num_results[s] = {"R":0, "N":0, "P":0}
		dic_results[s] = {}
		punti_per_studente[s] = 0
		max_punti_per_studente[s] = 0
		if not s.gruppo:
			continue
		tasks = s.gruppo.tasks
		for t in tasks:
			dic_results[s][t] = {}
			maxpoints_per_task = s.getMaxPointsPerTask(t)
			punti_per_studente[s] += maxpoints_per_task
			max_punti_per_studente[s] += t.maxpoints
			if  maxpoints_per_task == t.maxpoints:
				dic_results[s][t] = 'R'
			elif  maxpoints_per_task == 0:
				dic_results[s][t] = 'N'
			else:
				dic_results[s][t] = 'P'
			num_results[s][dic_results[s][t]] += 1
	
	return "OK",  render_template("ajax_admin_lista_studenti.html", **vars())

@initialize
def groups(session, USER=None):
	subtitle = ""
	pagetitle= " Lista Gruppi"
	gruppi = dbsession.query(Gruppo).order_by(Gruppo.nomegruppo.asc()).all()
	return "OK",  render_template("ajax_admin_lista_gruppi.html", **vars())

@initialize
def group_new(session, USER=None):
	gruppo = Gruppo()
	return "OK",  render_template("ajax_admin_group_edit.html", **vars())

@initialize
def group_update(session, object_id, USER=None):
	if object_id not in ('', None, "None"):
		gruppo = dbsession.query(Gruppo).get(object_id)
	else:
		gruppo = Gruppo()
	gruppo.nomegruppo = request.form.get("nomegruppo")
	gruppo.descgruppo = request.form.get("descgruppo")
	gruppo.ingara = 0
	dbsession.add(gruppo)
	dbsession.commit()
	return "OK",  "Update correctly"


@initialize
def group_removestudent(session, group_id, user_id, USER=None):
	gruppo = dbsession.query(Gruppo).get(group_id)
	utente = dbsession.query(Utente).get(user_id)
	gruppo.studenti.remove(utente)
	dbsession.add(gruppo)
	dbsession.commit()
	return group_edit(session, group_id)
	
@initialize
def group_edit(session, object_id, USER=None):
	gruppo = dbsession.query(Gruppo).get(object_id)
	return "OK",  render_template("ajax_admin_group_edit.html", **vars())
		
@initialize
def group_abilitazione(session, mode, object_id, USER=None):
	gruppo = dbsession.query(Gruppo).get(object_id)
	if mode == 'on':	# da on a off
		gruppo.in_gara = 0
	if mode == 'off':
		gruppo.in_gara = 1
	print(gruppo, mode)
	dbsession.add(gruppo)
	dbsession.commit()
	return "OK",  "Mode = " + mode

	
@initialize
def submissions(session, USER=None):
	subtitle = ""
	pagetitle= " Lista Sottoposizioni"
	submissions = dbsession.query(Submission).all()
	return "OK",  render_template("ajax_admin_lista_sottoposizioni.html", **vars())

@initialize
def submissions_delete(session, submission_id, USER=None):
	print("DEL submission_id", submission_id)
	submission = dbsession.query(Submission).get(submission_id)
	dbsession.delete(submission)
	dbsession.commit()
	return "OK",  "<span class='m-3 text-success'>Sottomissione cancellata con successo</span>"

@initialize
def tasks(session, USER=None):
	subtitle = ""
	pagetitle= " Lista Task "
	categorie = dbsession.query(Categoria).all()
	tasks = dbsession.query(Task).all()
	return "OK",  render_template("ajax_admin_lista_tasks.html", **vars())

@initialize
def task_edit(session, object_id, USER=None):
	task = dbsession.query(Task).get(object_id)
	categorie = dbsession.query(Categoria).all()
	return "OK",  render_template("ajax_admin_task_edit.html", **vars())

@initialize
def task_new(session, USER=None):
	task = Task()
	categorie = dbsession.query(Categoria).all()
	return "OK",  render_template("ajax_admin_task_edit.html", **vars())

@initialize
def task_assegna(session, object_id, USER=None):
	task = dbsession.query(Task).get(object_id)
	gruppi = dbsession.query(Gruppo).all()
	return "OK",  render_template("ajax_admin_task_assegna.html", **vars())

@initialize
def task_update(session, object_id, USER=None):
	if object_id not in ('', None, "None"):
		task = dbsession.query(Task).get(object_id)
	else:
		task = Task()
	task.titolo = request.form.get("titolo")
	task.sottotitolo = request.form.get("sottotitolo")
	task.difficolta = request.form.get("difficolta")
	task.categoria_id = request.form.get("categoria_id")
	task.html_text = request.form.get("html_text")
	task.cpp_template = request.form.get("cpp_template")
	task.python_template = request.form.get("python_template")
	dbsession.add(task)
	dbsession.commit()
	return "OK",  "Update correctly"

def task_duplica(session, object_id, USER=None):
	task = dbsession.query(Task).get(object_id)
	newtask = task.copy()
	dbsession.add(newtask)
	dbsession.commit()
	return "OK",  "Duplicated correctly"


@initialize
def task_abilita_disabilita(session, mode, USER=None):
	task_id = request.form.get('task_id')
	gruppo_id = request.form.get('gruppo_id')
	task = dbsession.query(Task).get(task_id)
#	print("task=", task)
	gruppo = dbsession.query(Gruppo).get(gruppo_id)
	print("gruppo=", gruppo)
	if mode == 'R':
		gruppo.tasks.remove(task)
	if mode == 'A':
		gruppo.tasks.append(task)
	
	dbsession.add(gruppo)
	dbsession.commit()
	return "OK",  "OK"


@initialize
def task_disabilita(session, USER=None):
	return task_abilita_disabilita(session, 'R')
	
@initialize
def task_abilita(session, USER=None):
	return task_abilita_disabilita(session, 'A')

@initialize
def task_addtestcase(session, USER=None):
	task_id = request.form.get('task_id')
	task = dbsession.query(Task).get(task_id)
	
	new_input = request.form.get("new_input")
	new_output = request.form.get("new_output")
	new_punteggio = request.form.get("new_punteggio")
	
	tc = TestCase(new_input, new_output, new_punteggio, task)
	dbsession.add(tc)
	dbsession.commit()
	return "OK", "Aggiunto"

@initialize
def task_export_testcases(session, object_id, USER=None):
	task = dbsession.query(Task).get(object_id)
	print(task.testcases)
	result = []
	for tc in task.testcases:
		result.append({
			"input": tc.input_text,
			"output": tc.output_atteso
		})
	return json.dumps(result)
