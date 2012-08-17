from sqlalchemy import *
from sqlalchemy import Table, Column, DateTime, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import sessionmaker, scoped_session

engine = create_engine('sqlite:///windowlog.db', echo=True)
Base = declarative_base(bind=engine)
Session = scoped_session(sessionmaker(engine))

class Windowlog(Base) :

	__tablename__ = 'windowlog'

	moment     = Column(DateTime, primary_key=True)
	windowname = Column(String)

	def __init__(self, moment, windowname) :
		self.moment = moment
		self.windowname = windowname

	def __repr__(self) :
		return "<Windowlog('%s', '%s')>" % (self.moment, self.windowname)

Base.metadata.create_all()
