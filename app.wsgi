#!/usr/bin/python3
import sys
import os
abspath = "/media/HOMEDEV/WWW/wsgi/codergame/"
sys.path.insert(0, abspath)
sys.path.insert(0, abspath+"appdir")
from appdir import app as application
