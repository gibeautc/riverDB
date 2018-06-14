#/usr/bin/env python3


#Utilites for riverDB

import time
import sys
from shutil import move


def setSetting(which,what):
	s=getSetting(which)
	if s==what:
		#they already match, no need to recreate conf file
		return
	old=None
	t=time.time()
	while old is None:
		try:
			old=open("river.conf","r")
		except:
			log.warning("river.conf busy or does not exist")
			time.sleep(1)
		if time.time()-t>5:
			print("river.conf Timeout!")
			return None
	try:
		new=open("river.tmp","w+")
	except:
		print("failed to create temp file")
		return
	try:
		done=False
		d=old.read()
		d=d.split("\n")
		old.close()
		for line in d:
			if line=="":
				continue
			if line.startswith("#"):
				new.write(line)
				new.write("\n")
				continue
			el=line.split(":")
			if el[0]==which:
				new.write(which+":"+str(what)+"\n")
				done=True
			else:
				new.write(line+"\n")
		if not done:
			new.write(which+":"+str(what)+"\n")
	except:
		print("No Old settings file?")
		print(sys.exc_info())
		new.write(which+":"+str(what))
		new.write("\n")
	
	new.close()
	move("river.tmp","river.conf")


#able to return native type for int,bool   all others will be returned as strings
def getSetting(which):
	f=None
	t=time.time()
	while f is None:
		try:
			f=open("river.conf","r")
		except:
			print("river.conf busy or does not exist")
			time.sleep(1)
		if time.time()-t>5:
			log.error("river.conf Timeout!")
			return None
	d=f.read()
	d=d.split("\n")
	for line in d:
		if line.startswith("#"):
			continue
		try:
			el=line.split(":")
			if el[0]==which:
				r=el[1]
				r=r.replace("\n","")
				if r=="False":
					return False
				if r=="True":
					return True
				try:
					return int(r)
				except:
					return r.replace("\n","")
		except:
			continue
	return None
