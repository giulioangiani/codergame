from sqlalchemy import Table, Column, Integer, String, create_engine, MetaData, Date, Text, Numeric, DateTime, UniqueConstraint
from sqlalchemy.orm import mapper, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.exc import *
from sqlalchemy.sql import func
import datetime


Base = declarative_base()

from config import engine
metadata = MetaData(bind=engine)
Session = sessionmaker(bind = engine)
dbsession = Session()
conn = engine.connect()


import time
import hashlib
import random
import string
from costanti import *
from tools import average

class App:
	pass

GruppiTask = Table('gruppi_task', Base.metadata,
		Column('id', Integer, primary_key=True),
		Column('gruppo_id', Integer, ForeignKey('gruppi.id')),
		Column('task_id', Integer, ForeignKey('tasks.id'))
	)

Sottomissioni = Table('sottomissioni', Base.metadata,
		Column('id', Integer, primary_key=True),
		Column('user_id', Integer, ForeignKey('utenti.id')),
		Column('task_id', Integer, ForeignKey('tasks.id')),
		Column('submission_id', Integer, ForeignKey('submissions.id'))
	)

class TestCase(Base):
	__tablename__ = 'testcases'
	
	def __init__(self, it='', ot='', p='', task=None):
		if it: self.input_text = it
		if ot: self.output_atteso = ot
		if p: self.punteggio = p
		if task: self.task = task
	
	id = Column(Integer, primary_key=True)
	input_text = Column(Text)
	output_atteso = Column(Text)
	punteggio = Column(Integer)
	task_id = Column(ForeignKey('tasks.id'))
	
class Task(Base):
	__tablename__ = 'tasks'
	id = Column(Integer, primary_key=True)
	titolo = Column(String(100))
	sottotitolo = Column(Text)
	html_text = Column(Text)
	difficolta = Column(Integer)
	testcases = relationship("TestCase", backref="task")
	categoria_id = Column(ForeignKey('categorie.id'))
	gruppi = relationship('Gruppo', secondary=GruppiTask, backref='task')
	
	@property
	def maxpoints(self):
		# calcolato come somma dei punteggi dei ogni testcase associati
	#	print(self.difficolta)
	#	print(self.testcases)
		return sum([tc.punteggio for tc in self.testcases])

	def sottomissioni(self):
		return dbsession.query(Sottomissioni).filter_by(task_id=self.id).all()
		
	def copy(self):
		t = Task()
		t.titolo=self.titolo
		t.sottotitolo=self.sottotitolo
		t.html_text=self.html_text
		t.difficolta=self.difficolta
		t.categoria_id=self.categoria_id
		return t



class Categoria(Base):
	__tablename__ = 'categorie'
	id = Column(Integer, primary_key=True)
	nomecategoria = Column(String(100))
	descrizione = Column(Text)
	tasks = relationship("Task", backref="categoria")

class Gruppo(Base):
	__tablename__ = 'gruppi'
	id = Column(Integer, primary_key=True)
	nomegruppo = Column(String(100))
	descgruppo = Column(String(100))
	in_gara = Column(Integer)
	studenti = relationship("Utente", backref="gruppo", order_by="Utente.cognome")
	tasks = relationship('Task', secondary=GruppiTask, backref='gruppo')
	
class Submission(Base):
	__tablename__ = 'submissions'
	id = Column(Integer, primary_key=True)
	lang = Column(String(10))
	code = Column(Text)
	timestamp = Column(DateTime)
	punteggio  = Column(Integer)
	compilazione = Column(Integer)
	user_id = Column(Integer)
	task_id = Column(Integer)
	
	def __repr__(self):
		return "Sub {} - User {} - Task {} - Punteggio {}".format(self.id, self.user_id, self.task_id, self.punteggio)

	def task(self):
		return dbsession.query(Task).get(self.task_id)

	def utente(self):
		return dbsession.query(Utente).get(self.user_id)
		

class Utente(Base):
	__tablename__ = 'utenti'

	id = Column(Integer, primary_key=True)
	username = Column(String(30))
	password = Column(String(50))
	email = Column(String(200))
	salt = Column(String(30))
	role = Column(String(30))
	description = Column(String(50))
	cognome = Column(String(50))
	nome = Column(String(50))
	gmail_id = Column(String(100))
	gmail_email = Column(String(200))
	gmail_description = Column(String(200))
	gmail_user_profile_url = Column(String(200))
	fb_id = Column(String(100))
	fb_email = Column(String(100))
	fb_description = Column(String(200))
	regstatus = Column(String(30))
	regcode = Column(String(100))
	gruppo_id = Column(ForeignKey('gruppi.id'))

	def generateSalt(self):
		salt = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(20))
		self.salt = salt
		return salt

	def setNewPassword(self, newpassword):
		salt = self.generateSalt()
		self.password = hashlib.md5((newpassword + salt).encode('utf-8')).hexdigest()
		return self.password

	def checkPassword(self, password):
		return self.password == hashlib.md5((password + self.salt).encode('utf-8')).hexdigest()

	def __repr__(self):
		return "User: {} {} {}".format(self.username, self.description, self.role)
		
	def getValutazione(self, e, tipologia):
		valutazioni = e.valutazioni
		for v in valutazioni:
			if v.user_id == self.id and v.elaborato_id == e.id and v.tipovalutazione == tipologia:
				return v
		return None
			
	def getValutazioni(self, e):
		return [v for v in e.valutazioni if v.user_id == self.id]
		
	def submissions(self, task):
		return dbsession.query(Submission).filter_by(task_id=task.id).filter_by(user_id=self.id).order_by(Submission.timestamp.desc()).all()
 
	def getMaxPointsPerTask(self, task):
		if not self.submissions(task):
			return 0
		maxpoints_task = max([s.punteggio for s in self.submissions(task)])
		return maxpoints_task

