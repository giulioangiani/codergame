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
from costanti import *


@initialize
def home(session, USER=None):
	print("QUI")
	subtitle = ""
	pagetitle= " Lista elaborati in concorso "
	elaborati = dbsession.query(Elaborato).all()
	u = dbsession.query(Utente).get(USER["userid"])
	descr_tipologie = DESCR_TIPOLOGIE
	return "OK",  render_template("ajax_dashboard.html", **vars())


@initialize
def view(session, idelaborato, USER=None):
	subtitle = ""
	e = dbsession.query(Elaborato).get(idelaborato)
	pagetitle= "Scheda di valutazione elaborato"
	elaborati = dbsession.query(Elaborato).all()
	u = dbsession.query(Utente).get(USER["userid"])
	descr_tipologie = DESCR_TIPOLOGIE
	return "OK",  render_template("ajax_dashboard_leggielaborato.html", **vars())

@initialize
def setvalutazione(session, USER=None):
	idelaborato = request.form.get("idelaborato", None)
	valutazione = request.form.get("valutazione", None)
	tipologia = request.form.get("tipologia", None)
	u = dbsession.query(Utente).get(USER["userid"])
	e = dbsession.query(Elaborato).get(idelaborato)
	# elimina precedente valutazione se esiste
	v = u.getValutazione(e, tipologia)
	if v:
		print("Cancello esistente")
		dbsession.delete(v)
		dbsession.commit()
	
	
	v = Valutazione()
	v.tipovalutazione = tipologia
	v.user_id = USER["userid"]
	v.valutazione = valutazione
	e.valutazioni.append(v)
	dbsession.commit()
	
	print(e)
	
	
	return "OK",  "OK"
	




@initialize
def answer_execute(session, USER=None):
	id_risposta = int(request.form.get("id_risposta"))
	id_domanda = int(request.form.get("id_domanda"))
	u = dbsession.query(Utente).get(USER["userid"])
	rids = [r.id for r in u.risposte]
	if id_risposta not in rids:
		return "KO", "Risorsa non disponibile"
	else:
		r = dbsession.query(Risposta).get(id_risposta)
		return exec_query(DBID, r.risposta)
		

@initialize
def answer_delete(session, USER=None):
	id_risposta = int(request.form.get("id_risposta"))
	id_domanda = int(request.form.get("id_domanda"))
	u = dbsession.query(Utente).get(USER["userid"])
	rids = [r.id for r in u.risposte]
	if id_risposta not in rids:
		return "KO", "Risorsa non disponibile"
	else:
		r = dbsession.query(Risposta).get(id_risposta)
		dbsession.delete(r)
		dbsession.commit()
		return "OK", render_template("risposteutente.html", **vars())
		
	
