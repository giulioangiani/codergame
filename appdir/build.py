from sqlalchemy import Table, Column, Integer, String, create_engine, MetaData, Date, Text, Numeric, DateTime, UniqueConstraint
from sqlalchemy.orm import mapper, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.exc import *
from sqlalchemy.sql import func
import datetime

from models import *

print("Dropping tables...")
Base.metadata.drop_all(engine)

print("Creating tables...")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
dbsession = Session()
conn = engine.connect()
dbsession.expire_all()
dbsession.commit()
dbsession.close()

g = Gruppo()
g.id = 1
g.nomegruppo = "GROUP_1"
g.descgruppo = "Gruppo 1 - Scuola Codergame"
dbsession.add(g)

dbsession.commit()

# admin
u = Utente()
u.username = "administrator"
u.setNewPassword("admin")
u.description = "Amministratore Sistema"
u.role = 'ADMIN'
dbsession.add(u)
dbsession.commit()

## categorie
c = Categoria()
c.id = 1
c.nomecategoria = "Sequenza"
c.descrizione = "Task risolvibili in O(1) con sole operazioni sequenziali"
dbsession.add(c)

c = Categoria()
c.id = 2
c.nomecategoria = "Selezione"
c.descrizione = "Task risolvibili con l'uso dell'operatore di selezione"
dbsession.add(c)

c = Categoria()
c.id = 3
c.nomecategoria = "Cicli"
c.descrizione = "Task risolvibili con l'uso dei cicli"
dbsession.add(c)

c = Categoria()
c.id = 4
c.nomecategoria = "Array"
c.descrizione = "Task risolvibili con l'uso degli array monodimensionali"
dbsession.add(c)
dbsession.commit()
## tasks

t1 = Task()
t1.categoria_id = 1
t1.titolo = "Somma di due numeri"
t1.sottotitolo = "Leggere da input due numeri A e B interi positivi e stampare la somma"
t1.difficolta = 1
t1.html_text = """L'input del programma &egrave; cos&igrave; strutturato:<br>
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

# testcases
dbsession.add(TestCase("2 3", "5", 1, t1))
dbsession.add(TestCase("0 0", "0", 1, t1))
dbsession.add(TestCase("99999 99999", "199998", 2, t1))
dbsession.commit()

dbsession.close()
