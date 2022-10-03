from sqlalchemy import create_engine, MetaData, Table
from costanti import SQLITEDB

config = {
  'user': 'codergame',
  'password': 'c0d3rg4m3',
  'host': '127.0.0.1',
  'database': 'codergame',
  'raise_on_warnings': True,
  'base_path': "http://localhost:10000"
}


engine = create_engine('sqlite:////' + SQLITEDB)
metadata = MetaData(bind=engine)

mail_sender_config = {
	"sender_address": "",
	"sender_pass": "",
}
