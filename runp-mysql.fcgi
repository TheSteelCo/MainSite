#!flask/bin/python
import os

# use mysql
os.environ['DATABASE_URL'] = 'mysql://apps:apps@localhost/apps'

from flipflop import WSGIServer
from main_site import app

if __name__ == '__main__':
    WSGIServer(app).run()