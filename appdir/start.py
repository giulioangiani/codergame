from __init__ import *
port = int(sys.argv[1])
app.run(
	host="0.0.0.0",
	port=port,
)
