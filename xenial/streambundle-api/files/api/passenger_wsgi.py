import sys, os

INTERP = os.path.expanduser("/usr/bin/python3.5")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from streambundle_api.stream_api import app as application
