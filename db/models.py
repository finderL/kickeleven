'''
Created on 2014-6-1

@author: nttdocomo
'''
import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base

DB_CONNECT_STRING = 'mysql+mysqldb://%s%s@localhost/%s?charset=utf8' % (settings.DATABASE_USERNAME, settings.DATABASE_PASSWORD, settings.DATABASE_NAME)
engine = create_engine(DB_CONNECT_STRING, echo=True)
DB_Session = sessionmaker(bind=engine,expire_on_commit=False)
sql_session = scoped_session(sessionmaker(bind=engine))

BaseModel = declarative_base()