from flask import Flask, g, redirect, url_for, escape, request, session, send_from_directory, render_template, send_file, jsonify
from tools import initialize, hashify, getUser
from sqlalchemy import Table, Column, Integer, String, create_engine, MetaData
from sqlalchemy.orm import mapper, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
import random
import datetime

import importlib
import models
importlib.reload(models)
from models import *
import time
import json
from costanti import *
import os

def getUserResults(USER):
	userdir = "{}{}/".format(CODERGAME_UPLOAD_DIR, USER["username"])
	
	try:
		os.makedirs(userdir)
	except:
		pass
	
	user_result_file = userdir + "result.dict"
	if not os.path.exists(user_result_file):
		f = open(user_result_file, 'w')
		f.write("{}")
		f.close()
	d = eval(open(user_result_file, 'r').read())
	return d

def setLastUserResult(quizid, punteggio, USER):
	userdir = "{}{}/".format(CODERGAME_UPLOAD_DIR, USER["username"])
	user_result_file = userdir + "result.dict"
	d = getUserResults(USER)
	d[quizid] = punteggio
	open(user_result_file, 'w').write(json.dumps(d))
	return d
	
def loadEnabledQuizzes():
	result = []
	files = os.listdir(CODERGAME_QUIZ_DIR)
	files.sort()
	for f in files:
		result.append(readQuiz(f))
	return result
	
def readQuiz(quizid):
	quizdict = eval(open(f"{CODERGAME_QUIZ_DIR}{quizid}").read())
	# calcolo punteggio complessivo
	maxpoints = sum([tc["points"] for tc in quizdict["testcases"]])
	quizdict["maxpoints"] = maxpoints
	return quizdict

def saveuploadefile(content, quizid, lang, USER):
	userdir = "{}{}/{}/".format(CODERGAME_UPLOAD_DIR, USER["username"], quizid)
	try:
		os.makedirs(userdir)
	except:
		pass
	fname = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
	pathfname = "{}{}.{}".format(userdir, fname, lang)
	open(pathfname, 'wb').write(content)
	return pathfname


def compileuploadedfile(fname, lang):
	# compile
	print("Compilazione")
	import subprocess
	subp = subprocess.run(f"g++ {fname} -o {fname}.o", shell=True)
	returncode = subp.returncode
	print(("returncode=", returncode))
	return returncode

def testuploadedfile(fname, lang, task, testcase, USER):
	
	user_tmp_dir = "{}{}/{}/tmp/".format(CODERGAME_UPLOAD_DIR, USER["username"], task.id)
	try:
		os.makedirs(user_tmp_dir)
	except:
		pass
	
	print("fname = ", fname)
	print("input = ", testcase.input_text)
	print("atteso = ", testcase.output_atteso)
	
	finput_tmp = "{}/{}.input".format(user_tmp_dir, time.time())
	print("finput_tmp=", finput_tmp)
	open(finput_tmp, 'w').write(testcase.input_text)
	# compile
	foutput_tmp = "{}/{}.output".format(user_tmp_dir, time.time())
	import subprocess
	test_input_output = subprocess.run(f"timeout 1s {fname}.o < {finput_tmp} > {foutput_tmp}", shell=True)
	print(("test_input_output", test_input_output))
	
	if test_input_output.returncode == 0:
		output_reale = open(foutput_tmp, 'r').read().strip()
		result = {
				"input": testcase.input_text,
				"output": output_reale,
				"atteso": testcase.output_atteso,
				"punteggio": 0,
				"puntmax": testcase.punteggio,
				"corretto": False
			}
		
		if output_reale.strip() == testcase.output_atteso.strip():
			result["punteggio"] = testcase.punteggio
			result["corretto"] = True
			
	elif test_input_output.returncode == 124:
		# time limit excedeed
		result = {
				"input": testcase.input_text,
				"output": "TIME_LIMIT_EXCEDEED",
				"atteso": testcase.output_atteso,
				"punteggio": 0,
				"puntmax": testcase.punteggio,
				"corretto": False
			}
	else:
		# general error
		result = {
				"input": testcase.input_text,
				"output": "GENERAL_ERROR",
				"atteso": testcase.output_atteso,
				"punteggio": 0,
				"puntmax": testcase.punteggio,
				"corretto": False
			}
		
	return result	
		
@initialize
def home(session, USER=None):
	subtitle = ""
	pagetitle= " Codergame Dashboard "
	U = getUser(USER)
	if not U:
		return "KO", "Not Authorized"
	punteggio_studente = sum([U.getMaxPointsPerTask(task) for task in U.gruppo.tasks])
	maxpunteggio = sum([t.maxpoints for t in U.gruppo.tasks])
	return "OK",  render_template("cg_ajax_dashboard.html", **vars())


@initialize
def form(session, taskid, USER=None):
	subtitle = ""
	pagetitle= " Codergame Submit Form "
	U = getUser(USER)
	task = dbsession.query(Task).get(taskid)
	return "OK",  render_template("cg_ajax_form.html", **vars())

@initialize
def uploadfile(session, USER=None):
	import io
	codefile = request.files["codefile"]
	contenuto_codefile = io.BytesIO(codefile.read())
	content = contenuto_codefile.read()
	taskid = request.form.get("taskid")
	task = dbsession.query(Task).get(taskid)
	print("taskid=", taskid)
	lang = "cpp"
	U = getUser(USER)
	
	# salva il contenuto su file e su DB
	fname = saveuploadefile(content, taskid, lang, USER)
	s = Submission()
	s.lang=lang
	s.code=content
	s.timestamp=datetime.datetime.now()
	s.task_id=taskid
	s.user_id=U.id
	
	# compilazione
	compile_return_code = compileuploadedfile(fname, lang)
	if compile_return_code != 0:
		errore_compilazione = True
		s.punteggio=0
		s.compilazione=0
		dbsession.add(s)
		dbsession.commit()
		return "OK",  render_template("cg_ajax_results_compileerror.html", **vars())

	s.compilazione=1

	
	# test e risultati
	
	# leggo quiz
	testcases = task.testcases
	print("testcases=", testcases)
	
	punteggio = 0
	puntmax = 0
	tests = {}
	
	for testcase in testcases:
		ntest = testcase.id
		testcase_result = testuploadedfile(fname, lang, task, testcase, USER)

		tests[ntest] = testcase_result
		print(f"test {ntest} :  {testcase_result}")
		punteggio += testcase_result["punteggio"]
		puntmax += testcase_result["puntmax"]

	print(("puntmax=", puntmax))
	print(("punteggio=", punteggio))
	s.punteggio=punteggio
	dbsession.add(s)
	dbsession.commit()

	return "OK",  render_template("cg_ajax_results.html", **vars())

@initialize
def results(session, USER=None):
	usersdir = "{}/".format(CODERGAME_UPLOAD_DIR)
	risultati = {}
	for f in os.listdir(usersdir):
		user_result_file = "{}{}/result.dict".format(CODERGAME_UPLOAD_DIR, f)
		risultati[f] = eval(open(user_result_file, 'r').read())
		
	quizzes = loadEnabledQuizzes()
	
	massimo_punteggio = 0
	for quizdict in quizzes:
#		print(("=", sum([tc["points"] for tc in quizdict["testcases"]])))
		massimo_punteggio += sum([tc["points"] for tc in quizdict["testcases"]])	
	
	id_quiz_enabled = [elem['id'] for elem in quizzes]

	totali = {}
	for r in risultati:
		print(risultati[r])
		
		valori = []
		for k in risultati[r]:
			if k in id_quiz_enabled:
				valori.append(risultati[r][k])
		
		#totali[r] = sum(risultati[r].values())
		totali[r] = sum(valori)
		
	totali = dict(sorted(totali.items(), key=lambda item: "{}:{}".format(-item[1], item[0])))	
	totali = dict(sorted(totali.items(), key=lambda item: -item[1]))	

	return "OK", render_template("cg_ajax_classifica.html", **vars())
