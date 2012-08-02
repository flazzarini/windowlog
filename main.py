#!/usr/bin/env python
import logging, subprocess, sys
from time import sleep
from sqlalchemy import create_engine, MetaData, Column, Table, ForeignKey, Integer, String


# Logging configuration
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Database configuration
engine = create_engine('sqlite:///windowlog.db', echo=True)
metadata = MetaData(bind=engine)
	
windowlog = Table('windowlog', metadata,
		  Column('moment', Integer, primary_key=True),
		  Column('windowname', String(40)))

metadata.create_all()
connection = engine.connect()


class window :
	def __init__(self) :
		self.id   = self.getWindowId()
		self.name = self.getWindowName(id)
		self.pid  = self.getWindowPid(id)
		self.bin  = self.getWindowBin(id)
		logger.info('---> Window Class initialized <---')

	def getWindowId(self) :
		winIdOutput, winIdError = subprocess.Popen("xprop -root | grep '_NET_ACTIVE_WINDOW(WINDOW)' | cut -d ' ' -f 5 | tr -d '\n'", shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		logger.debug('winIdOutput : %s' % winIdOutput)
		logger.debug('winIdError  : %s'  % winIdError)

		if winIdError == '' :
			logger.info('Current Window Id : %s' % winIdOutput)
			return winIdOutput
		else :
			return None

	def getWindowName(self, id) :
		winNameOutput, winNameError = subprocess.Popen("xwininfo -id %s | grep 'xwininfo: Window id:' | awk 'BEGIN {FS=\"\\\"\"}/xwininfo: Window id/{print $2}' | tr -d '\n'" % id, \
								shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		logger.debug('winNameOutput : %s ' % winNameOutput)
		logger.debug('winNameError  : %s'   % winNameError )

		if winNameError == '' :
			logger.info('Current Window Name : %s' % winNameOutput)
			return winNameOutput
		else :
			return None
	
	def getWindowPid(self, id) :
		winPidOutput, winPidError = subprocess.Popen("xprop -id %s | awk '/_NET_WM_PID\(CARDINAL\)/{ print $3 }' | tr -d '\n'" % id, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		logger.debug('winPidOutput : %s ' % winPidOutput)
		logger.debug('winPidError  : %s ' % winPidError)

		if winPidError == '' :
			logger.info('Current Window Pid : %s' % winPidOutput)
			return winPidOutput
		else :
			return None

	def getWindowBin(self, id) :
		winBinOutput, winBinError = subprocess.Popen("xprop -id %s | awk '/WM_COMMAND\(STRING\)/{ print $4 }' | tr -d '\n'" % id, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		logger.debug('winBinOutput : %s ' % winBinOutput)
		logger.debug('winBinError  : %s ' % winBinError)

		if winBinError == '' :
			logger.info('Current Window Binary : %s' % winBinOutput)
			return winBinOutput
		else :
			return None


	def getId(self) :
		return self.id

	def getName(self) :
		return self.name

	def getPid(self) :
		return self.pid

	def getBin(self) :
		return self.bin


if __name__ == "__main__" :
	
	logger.info('Windowlog started ...')

	while True :
		try :
			# Initialize the window class
			#  TODO __init__ should get the id of current window on initialization
			w = window()
			#print w.getId()
			#print w.getName()
			#print w.getPid()
			#print w.getBin()
			w.getWindowName(w.getWindowId())
			w.getWindowBin(w.getWindowId())
			w.getWindowPid(w.getWindowId())
			sleep(2)
		except KeyboardInterrupt :
			logger.info('Windowlog exited ...')
			sys.exit(0)


	#newdata = windowlog.insert().values(moment = 201201012010, windowname = 'test')
	#connection.execute(newdata)
