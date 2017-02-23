#!/usr/bin/env python3
import sys
import os

INTERP = os.path.expanduser("/usr/bin/python3")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())


from crm_backend.crm_backend import APP as application
