#!/usr/bin/env python
import logging, subprocess, sys
from time     import sleep
from datetime import datetime
from uuid     import uuid1
from sqlalchemy     import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from models         import Windowlog

# Logging configuration
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class window :
	def __init__(self) :
		logger.debug('---> Window Class initialized <---')
		self.id      = self.getWindowId()
		self.oldid   = self.id
		self.name    = self.getWindowName(self.id)
		self.pid     = self.getWindowPid(self.id)
		self.bin     = self.getWindowBin(self.id)
		self.changed = True
		self.getInfo()

	def getInfo(self) :
		logger.info('Window id   : %s'   % self.id)
		logger.info('Window name : %s'   % self.name)
		logger.info('Window pid  : %s'   % self.pid)
		logger.info('Window bin  : %s'   % self.bin)

	def getWindowId(self) :
		cmd = "xprop -root | grep -a '_NET_ACTIVE_WINDOW(WINDOW)' | cut -d ' ' -f 5 | tr -d '\n'"
		winIdOutput, winIdError = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		logger.debug('winIdOutput : %s' % winIdOutput)
		logger.debug('winIdError  : %s' % winIdError)

		if winIdError == '' :
			logger.debug('Current Window Id : %s' % winIdOutput)
			return winIdOutput
		else :
			return None

	def getWindowName(self, id) :
		cmd = "xwininfo -id %s | grep -a 'xwininfo: Window id:' | awk -F \"\\\"\" '{ print $2 }' | tr -d '\n'" % id
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
		cmd = "xwd -id %s -out /tmp/windowlog-%s.xwd && convert -scale 35%% /tmp/windowlog-%s.xwd /tmp/windowlog-%s.png && rm -Rf /tmp/windowlog-%s.xwd" % (id, uuid, uuid, uuid, uuid)
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

	def getChanged(self) :
		return self.changed

	def setId(self) :
		self.id = self.getWindowId()

	def setName(self) :
		self.name = self.getWindowName(self.id)

	def setPid(self) :
		self.pid = self.getWindowPid(self.id)

	def setBin(self) :
		self.bin = self.getWindowBin(self.id)

	def setChanged(self, value) :
		self.changed = value

	def update(self) :
		self.setId()
		self.setName()
		self.setPid()
		self.setBin()
		self.setChanged(False)
	
		if self.id != self.oldid :
			logger.info('--> Window Changed <--')
			self.getInfo()
			self.oldid = self.id
			self.getWindowScreenshot(self.id)
			self.setChanged(True)
		

if __name__ == "__main__" :
	
	logger.info('Windowlog started ...')
	
	# Database configuration
	engine  = create_engine('sqlite:///windowlog.db', echo=False)
	Session = sessionmaker(bind=engine)
	session = Session()
	
	window = window()

	while True :
		try :
			window.update()

			if window.getChanged() :
				windowlog = Windowlog( datetime.now(), unicode(window.getName(), errors='replace') )
				session.add(windowlog)
				session.commit()
			sleep(2)
		except KeyboardInterrupt :
			logger.info('Windowlog exited ...')
			sys.exit(0)

