from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def get_db():
    if not hasattr(current_app, 'db'):
        engine = create_engine('mysql://dbsteelco:Royal72uk@thesteelco.com/thesteelco')
        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        current_app.db = db_session
    return current_app.db
