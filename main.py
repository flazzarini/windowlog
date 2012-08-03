#!/usr/bin/env python
import logging, subprocess, sys
from time import sleep
from sqlalchemy import create_engine, MetaData, Column, Table, ForeignKey, Integer, String
from uuid import uuid1


# Logging configuration
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class window :
	def __init__(self) :
		logger.debug('---> Window Class initialized <---')
		self.id    = self.getWindowId()
		self.oldid = self.id
		self.name  = self.getWindowName(self.id)
		self.pid   = self.getWindowPid(self.id)
		self.bin   = self.getWindowBin(self.id)
		self.getInfo()

	def getInfo(self) :
		logger.info('Window id   : %s'   % self.id)
		logger.info('Window name : %s'   % self.name)
		logger.info('Window pid  : %s'   % self.pid)
		logger.info('Window bin  : %s'   % self.bin)

	def getWindowId(self) :
		cmd = "xprop -root | grep '_NET_ACTIVE_WINDOW(WINDOW)' | cut -d ' ' -f 5 | tr -d '\n'"
		winIdOutput, winIdError = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		logger.debug('winIdOutput : %s' % winIdOutput)
		logger.debug('winIdError  : %s' % winIdError)

		if winIdError == '' :
			logger.debug('Current Window Id : %s' % winIdOutput)
			return winIdOutput
		else :
			return None

	def getWindowName(self, id) :
		cmd = "xwininfo -id %s | grep 'xwininfo: Window id:' | awk -F \"\\\"\" '{ print $2 }' | tr -d '\n'" % id
		winNameOutput, winNameError = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		logger.debug('winNameOutput : %s ' % winNameOutput)
		logger.debug('winNameError  : %s'  % winNameError )

		if winNameError == '' :
			logger.debug('Current Window Name : %s' % winNameOutput)
			return winNameOutput
		else :
			return None
	
	def getWindowPid(self, id) :
		cmd = "xprop -id %s | awk '/_NET_WM_PID\(CARDINAL\)/{ print $3 }' | tr -d '\n'" % id
		winPidOutput, winPidError = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		logger.debug('winPidOutput : %s ' % winPidOutput)
		logger.debug('winPidError  : %s ' % winPidError)

		if winPidError == '' :
			logger.debug('Current Window Pid : %s' % winPidOutput)
			return winPidOutput
		else :
			return None

	def getWindowBin(self, id) :
		cmd = "xprop -id %s | awk '/WM_COMMAND\(STRING\)/{ print $4 }' | tr -d '\n'" % id
		winBinOutput, winBinError = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		logger.debug('winBinOutput : %s ' % winBinOutput)
		logger.debug('winBinError  : %s ' % winBinError)

		# If empty try to find binary via pid
		if winBinOutput == '' :
			pid = self.getWindowPid(id)
			cmd = "ps aux | grep %s | grep -v grep | awk '{ print $11 }' | tr -d '\n'" % pid
			winBinOutput, winBinError = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
			logger.debug('winBinOutput : %s ' % winBinOutput)
			logger.debug('winBinError  : %s ' % winBinError)

		if winBinError == '' :
			logger.debug('Current Window Binary : %s' % winBinOutput)
			return winBinOutput
		else :
			return None


	def getWindowScreenshot(self, id):
		uuid = uuid1()	
		cmd = "xwd -id %s -out /tmp/windowlog-%s.xwd && convert /tmp/windowlog-%s.xwd /tmp/windowlog-%s.png && rm -Rf /tmp/windowlog-%s.xwd" % (id, uuid, uuid, uuid, uuid)
		winScreenOut, winScreenError = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		
		logger.debug('cmd            : %s' % cmd)
		logger.debug('winScreenOut   : %s' % winScreenOut)
		logger.debug('winScreenError : %s' % winScreenError)


	def getId(self) :
		return self.id

	def getName(self) :
		return self.name

	def getPid(self) :
		return self.pid

	def getBin(self) :
		return self.bin

	def setId(self) :
		self.id = self.getWindowId()

	def setName(self) :
		self.name = self.getWindowName(self.id)

	def setPid(self) :
		self.pid = self.getWindowPid(self.id)

	def setBin(self) :
		self.bin = self.getWindowBin(self.id)

	def update(self) :
		self.setId()
		self.setName()
		self.setPid()
		self.setBin()
	
		if self.id != self.oldid :
			logger.info('--> Window Changed <--')
			self.getInfo()
			self.oldid = self.id
			self.getWindowScreenshot(self.id)
		

if __name__ == "__main__" :
	
	logger.info('Windowlog started ...')
	
	# Database configuration
	#engine = create_engine('sqlite:///windowlog.db', echo=True)
	#metadata = MetaData(bind=engine)
	#	
	#windowlog = Table('windowlog', metadata,
	#		  Column('moment', Integer, primary_key=True),
	#		  Column('windowname', String(40)))
	#
	#metadata.create_all()
	#connection = engine.connect()

	#newdata = windowlog.insert().values(moment = 201201012010, windowname = 'test')
	#connection.execute(newdata)
	
	w = window()

	while True :
		try :
			w.update()
			#print w.getId()
			#print w.getName()
			#print w.getPid()
			#print w.getBin()
			#w.getWindowName(w.getWindowId())
			#w.getWindowBin(w.getWindowId())
			#w.getWindowPid(w.getWindowId())
			sleep(2)
		except KeyboardInterrupt :
			logger.info('Windowlog exited ...')
			sys.exit(0)

