activate_this = '/home/wfournier/.virtualenvs/triangulator/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
import os
sys.path.insert(0, '/'.join(os.path.realpath(__file__).split('/')[:-1]))
from app import app as application