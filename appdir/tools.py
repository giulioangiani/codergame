## protection by login
from functools import wraps
import hashlib
import random
import traceback
		
def initialize(fnz):
	@wraps(fnz)
	def f(*args, **kwargs):
		USER = args[0].get("USEROBJ")
#		print(args)
#		print(kwargs)
		if kwargs.get('request'):
			_object_id = kwargs['request'].form.get("_object_id", None)
			_object_hashcode = kwargs['request'].form.get("_object_hashcode", None)
#			print(_object_hashcode)
#			print(_object_id)
			return fnz(*args, **kwargs, USER=USER, _object_hashcode=_object_hashcode, _object_id=_object_id)
		else:
			_object_id = _object_hashcode = None
			return fnz(*args, **kwargs, USER=USER)

		return fnz(*args, **kwargs, USER=USER)
	return f


def parseform(fnz):
	@wraps(fnz)
	def f(*args, **kwargs):
		if kwargs.get('request'):
			form = kwargs["request"].form
			formvalues = {}
			for k in form:
				if k.startswith("values["):
					paramname = k.replace("values[", "").replace("]", "")
					paramvalue = form[k]
					if paramname:
						formvalues[paramname] = paramvalue
#					print(">>>", paramname, paramvalue)
			return fnz(*args, **kwargs, F=formvalues)
		else:
			_object_id = _object_hashcode = None
			return fnz(*args, **kwargs)

		return fnz(*args, **kwargs)
	return f


def hashify(obj):
	try:
		values = []
		for c in obj.__table__._columns:
			values.append(str(obj.__getattribute__(c.key)))
		values.sort()
		return hashlib.md5(repr(values).encode("utf-8", "ignore")).hexdigest()
	except:
		return hashlib.md5(repr(obj).encode("utf-8", "ignore")).hexdigest()


def generateNewPwd(n=8):
	L = '1234567890abcdefghijklmnopqrstuvz'
	s = ''
	for i in range(n):
		s += random.choice([ch for ch in L])
	return s
	

def average(lst):
    return sum(lst) / len(lst)
  
def getUser(USER):
	try:
		import models
		U = models.dbsession.query(models.Utente).filter_by(username=USER["username"]).one()
		return U
	except:
		print(traceback.format_exc())
		return None

