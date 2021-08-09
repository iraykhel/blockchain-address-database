import os
import subprocess
# import sqlite_web

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

subprocess.check_output(['sqlite_web', ROOT_DIR + '/data/addresses.db'])