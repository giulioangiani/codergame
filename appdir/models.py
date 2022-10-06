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
		print(self.difficolta)
		print(self.testcases)
		return sum([tc.punteggio for tc in self.testcases])

	def sottomissioni(self):
		return dbsession.query(Sottomissioni).filter_by(task_id=self.id).all()
	
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


 
if __name__ == '__main__':

	if 1:
		print("Dropping tables...")
		Base.metadata.drop_all(engine)

	if 1:
		print("Creating tables...")
		Base.metadata.create_all(engine)

	Session = sessionmaker(bind = engine)
	dbsession = Session()
	conn = engine.connect()
	dbsession.expire_all()
	dbsession.commit()
	dbsession.close()

	if 1:
		g = Gruppo()
		g.id=1
		g.nomegruppo = "1M_20222023"
		g.descgruppo = "Classe 1M IIS Pascal - Anno Scolastico 2022/2023"
		dbsession.add(g)
		
		g = Gruppo()
		g.id=2
		g.nomegruppo = "2M_20222023"
		g.descgruppo = "Classe 1M IIS Pascal - Anno Scolastico 2022/2023"
		dbsession.add(g)

		dbsession.commit()

		users="""c.rossi;Carlo;Rossi;1M INFORMATICA;1234;c.rossi@studenti.local;1
a.verdi;Andrea;Verdi;1M INFORMATICA;1234;a.verdi@studenti.local;1
l.gialli;Luisa;Gialli;2M INFORMATICA;1234;l.gialli@studenti.local;2
k.blue;Katrine;Blue;2M INFORMATICA;1234;k.blue@studenti.local;2"""

		rows = [elem.split(";") for elem in users.split("\n")]

		for elem in rows:
			print(elem)
			u = Utente()
			u.username = elem[0]
			u.setNewPassword(elem[4])
			u.nome=elem[1]
			u.cognome=elem[2]
			u.description = elem[1] + " " + elem[2]
			u.role = 'GUEST'
			
			g = dbsession.query(Gruppo).get(elem[6])
			u.gruppo = g

			dbsession.add(u)
		
		dbsession.commit()

	# admin
	if 1: 
		u = Utente()
		u.username = "giulio.angiani"
		u.setNewPassword("gggg")
		u.description = "Giulio Angiani"
		u.role = 'ADMIN'
		dbsession.add(u)
		dbsession.commit()
	
	## categorie
	c = Categoria()
	c.id=1
	c.nomecategoria = "Sequenza"
	c.descrizione = "Task risolvibili in O(1) con sole operazioni sequenziali"
	dbsession.add(c)

	c = Categoria()
	c.id=2
	c.nomecategoria = "Selezione"
	c.descrizione = "Task risolvibili con l'uso dell'operatore di selezione"
	dbsession.add(c)
		
	c = Categoria()
	c.id=3
	c.nomecategoria = "Cicli"
	c.descrizione = "Task risolvibili con l'uso dei cicli"
	dbsession.add(c)

	c = Categoria()
	c.id=4
	c.nomecategoria = "Array"
	c.descrizione = "Task risolvibili con l'uso degli array monodimensionali"
	dbsession.add(c)
	dbsession.commit()
	## tasks
	
	t1 = Task()
	t1.categoria_id = 1
	t1.titolo="Somma di due numeri"
	t1.sottotitolo="Leggere da input due numeri A e B interi positivi e stampare la somma"
	t1.difficolta=1
	t1.html_text="""L'input del programma &egrave; cos&igrave; strutturato:<br>
		Sono forniti due valori interi A e B<br>
		l'<b>OUTPUT</b> del programma consiste in un unico valore intero N che &agrave; la somma di A e B
		<b>NOTA</b><br>
		Per leggere 2 numeri una sola riga puoi usare l'istruzione:<br>
		<pre><tt>cin >> A >> B;</tt></pre>
		<hr>
		<b>ESEMPIO 1</b><br>
		<b>input</b><br>
		3 4<br>
		<b>output</b><br>
		7<br>
		<hr>
		<b>ESEMPIO 2</b><br>
		<b>input</b><br>
		1 1<br>
		<b>output</b><br>
		2<br>
		<hr>
		<b>ASSUNZIONI</b><br>
		1 <= A,B <= 100000<br>
		2 <= N <= 200000<br>
		"""
	dbsession.add(t1)


	t2 = Task()
	t2.categoria_id = 1
	t2.titolo="Massimo di tre numeri"
	t2.sottotitolo="Leggere da input tre numeri A, B, C interi positivi e stampare il più grande"
	t2.difficolta=2
	t2.html_text="""L'input del programma &egrave; cos&igrave; strutturato:<br>"""
	dbsession.add(t2)

	dbsession.commit()
	
	t1.gruppi.append(g)
	dbsession.commit()

	# testcases
	dbsession.add(TestCase("2 3", "5", 1, t1))
	dbsession.add(TestCase("0 0", "0", 1, t1))
	dbsession.add(TestCase("99999 99999", "199998", 2, t1))
	
	dbsession.add(TestCase("2 3 5", "5", 1, t2))
	dbsession.add(TestCase("0 0 0", "0", 1, t2))
	dbsession.add(TestCase("9 5 1", "9", 1, t2))
	dbsession.add(TestCase("100000 0 50000", "100000", 1, t2))
	dbsession.commit()
	
	
	dbsession.close()
