#!flask/bin/python
import os

# use mysql
os.environ['DATABASE_URL'] = 'mysql://dbsteelco:Royal72uk@thesteelco.com/thesteelco'

from flipflop import WSGIServer
from main_site import app

if __name__ == '__main__':
    WSGIServer(app).run()