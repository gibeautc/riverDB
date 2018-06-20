#!/usr/bin/env python3


#River OSM Data
from riverUtils import * 
from osmapi import OsmApi
import os
import time
import sys
import sqlite3
import datetime
import hashlib
import logging as log



#need to come up with a method of multitple boxes inside a larger bounding box. as it seams the limit for the api is around .25 (maybe degree?)




def checkSetLogLevel():
	l=getSetting("loglevel")
	ll=log.WARNING  #default
	if l=="DEBUG":
		ll=log.DEBUG
	if l=="INFO":
		ll=log.INFO
	if l=="WARNING":
		ll=log.WARNING
	if l=="ERROR":
		ll=log.ERROR
	log.setLevel=ll
	
#logging setup
FORMAT='%(levelname)s %(asctime)s %(threadName)s : %(message)s'
LOGFILE='/home/chadg/logs/riverDB.log'
log.basicConfig(format=FORMAT,datefmt='%m-%d-%y %H:%M:%S',filename=LOGFILE,level=log.WARNING)
checkSetLogLevel()
log.info('Logging Started')

class Token():
	def __init__(self):
		self.db,self.curs=openDB()
		self.api=OsmApi(passwordfile='.pwdFile')
	def connectDB(self):
		self.db,self.curs=openDB()
	def closeDB(self):
		self.db.close()

def openDB():
	d=sqlite3.connect('river.db')
	c=d.cursor()
	return d,c
	
def buildDB(full,tok):
	if full:
		log.warning("Deleting Database")
		time.sleep(1)
		try:
			os.remove('river.db')
		except:
			pass
		tok.connectDB()
	log.info("Building Database")
	tok.curs.execute('CREATE TABLE IF NOT EXISTS nodes(id bigint,lat float(8,5),lon float(8,5),changeset bigint,tags text,version int,user varchar(20),uid int,ts datetime,visible bool,primary key(id))')
	tok.curs.execute('CREATE TABLE IF NOT EXISTS ways(id bigint,changeset,tags text,version int,user varchar(20),uid int,ts datetime,visible bool,closed bool,primary key(id))')
	tok.curs.execute('CREATE TABLE IF NOT EXISTS links(nid bigint,wid bigint,ord int,primary key(nid,wid))')
	tok.curs.execute('CREATE TABLE IF NOT EXISTS relations(id bigint,changeset bigint,tags text,version int,user varchar(20),uid int,ts datetime,visible bool,primary key(id))')
	tok.curs.execute('CREATE TABLE IF NOT EXISTS relLinks(rid bigint,lid bigint,ord int,type varchar(20),role varchar(20),primary key(rid,lid))')
	tok.curs.execute('CREATE TABLE IF NOT EXISTS myChangeSets(id bigint,commentCount int,primary key(id))')
	tok.curs.execute('CREATE TABLE IF NOT EXISTS config(name varchar(20),value varchar(50),primary key(name))')
	tok.db.commit()
	log.info("Database Build Complete")

def addNodeDB(n,tok):
	db_out=[str(n['id']),str(n['lat']),str(n['lon']),str(n['tag']),str(n['changeset']),str(n['version']),str(n['user']),str(n['uid']),str(n['timestamp']),str(n['visible'])]
	q="insert or replace into nodes(id,lat,lon,tags,changeset,version,user,uid,ts,visible) values(?,?,?,?,?,?,?,?,?,?)"
	try:
		tok.curs.execute(q,db_out)
		tok.db.commit()
		log.info("Added Node: "+str(n['id']))
	except:
		tok.db.rollback()
		log.error("Error Adding Node")
		log.error(sys.exc_info())
		
def addWayDB(n,tok):
	nodes=n['nd']
	if nodes[0]==nodes[-1]:
		log.debug("Closed Way")
		closed=True
	else:
		log.debug("Open Way")
		closed=False
	db_out=[str(n['id']),str(n['tag']),str(n['changeset']),str(n['version']),str(n['user']),str(n['uid']),str(n['timestamp']),str(n['visible']),str(closed)]
	q="insert or replace into ways(id,tags,changeset,version,user,uid,ts,visible,closed) values(?,?,?,?,?,?,?,?,?)"
	try:
		tok.curs.execute(q,db_out)
		tok.db.commit()
		log.info("Added Way: "+str(n['id']))
	except:
		tok.db.rollback()
		log.error("Error Adding Way")
		log.error(sys.exc_info())
		
def addRelationDB(r,tok):
	db_out=[str(r['id']),str(r['tag']),str(r['changeset']),str(r['version']),str(r['user']),str(r['uid']),str(r['timestamp']),str(r['visible'])]
	q="insert or replace into relations(id,tags,changeset,version,user,uid,ts,visible) values(?,?,?,?,?,?,?,?)"
	try:
		tok.curs.execute(q,db_out)
		tok.db.commit()
		log.info("Added Relation: "+str(r['id']))
	except:
		tok.db.rollback()
		log.error("Error Adding Relation")
		log.error(sys.exc_info())

def addLinkDB(nid,wid,index,tok):
	db_out=[str(nid),str(wid),str(index)]
	q="insert or replace into links(nid,wid,ord) values(?,?,?)"
	try:
		tok.curs.execute(q,db_out)
		tok.db.commit()
		log.info("Added Link: "+str(nid)+" : "+str(wid))
	except:
		tok.db.rollback()
		log.error("Error Adding Link")
		log.error(sys.exc_info())

def addRelLinkDB(m,rid,cnt,tok):
	#relLinks(rid bigint,lid bigint,ord int,type varchar(20),role varchar(20),primary key(rid,lid))')
	try:
		db_out=[str(rid),str(m['ref']),str(cnt),str(m['type']),str(m['role'])]
		q="insert or replace into relLinks(rid,lid,ord,type,role) values(?,?,?,?,?)"
	except:
		pass
	try:
		db_out=[str(rid),str(m['ref']),str(cnt),str(m['type'])]
		q="insert or replace into relLinks(rid,lid,ord,type) values(?,?,?,?)"
	except:
		pass
	try:
		tok.curs.execute(q,db_out)
		tok.db.commit()
		log.info("Added Relation Link: "+str(rid))
	except:
		tok.db.rollback()
		log.error("Error Adding Link")
		log.error(sys.exc_info())
		
def removeNodeDB(n,tok):
	q="delete from nodes where id=?"
	try:
		tok.curs.execute(q,[int(n['id']),])
		tok.db.commit()
		log.info("Removed Node: "+str(n['id']))
		return True
	except:
		tok.db.rollback()
		log.error("Error Removing Node")
		log.error(sys.exc_info())
		return False
		
def removeWayDB(w,tok):
	q="delete from ways where id=?"
	try:
		tok.curs.execute(q,[int(w['id']),])
		tok.db.commit()
		log.info("Removed Way: "+str(w['id']))
		return True
	except:
		tok.db.rollback()
		log.error("Error Removing Way")
		log.error(sys.exc_info())
		return False
	q="delete from links where wid=?"
	try:
		tok.curs.execute(q,[int(w['id']),])
		tok.db.commit()
		return True
	except:
		tok.db.rollback()
		log.error("Error Removing Links")
		log.error(sys.exc_info())
		return False
	
	
	
def removeRelationDB(r,tok):
	q="delete from relations where id=?"
	try:
		tok.curs.execute(q,[int(r['id']),])
		tok.db.commit()
		log.info("Removed Relation: "+str(r['id']))
	except:
		tok.db.rollback()
		log.error("Error Removing Relation")
		log.error(sys.exc_info())
		return False
	q="delete from relLinks where rid=?"
	try:
		tok.curs.execute(q,[int(r['id']),])
		tok.db.commit()
		return True
	except:
		tok.db.rollback()
		log.error("Error Removing Relation Links")
		log.error(sys.exc_info())
		return False

def getFullMap(tok):
	#will update if we already have data in database, but it will still be slow
	boundBoxString=getSetting("boundBox")
	latLonPairs=boundBoxString.split(";")
	lat1,lon1=latLonPairs[0].split(",")
	lat2,lon2=latLonPairs[1].split(",")
	
	data=tok.api.Map(min(float(lon1),float(lon2)),min(float(lat1),float(lat2)),max(float(lon1),float(lon2)),max(float(lat1),float(lat2)))
	if data is None or len(data)<1:
		log.warning("Bad data returned from map function?")
		return
	nodes=[]
	ways=[]
	relations=[]
	totalCount=len(data)
	log.info("Returned "+str(totalCount)+" elements")
	retTime=int(time.mktime(time.gmtime()))
	procCnt=0
	for d in data:
		log.debug("Sorting:"),
		log.debug(procCnt/totalCount)
		procCnt=procCnt+1
		if d['type']=='node':
			nodes.append(d['data'])
		if d['type']=='way':
			ways.append(d['data'])
		if d['type']=='relation':
			relations.append(d['data'])
	log.debug("Number of Nodes: "+str(len(nodes)))
	log.debug("Number of Ways: "+str(len(ways)))
	log.debug("Number of Relations: "+str(len(relations)))
	 
	procCnt=0
	for n in nodes:
		addNodeDB(n,tok)
		log.info("Adding Node:"),
		log.debug(procCnt/totalCount)
		procCnt=procCnt+1
	for w in ways:
		log.info("Adding Way:"),
		log.debug(procCnt/totalCount)
		procCnt=procCnt+1
		cnt=0
		for n in w['nd']:
			addLinkDB(n,w['id'],cnt,tok)
			cnt=cnt+1
		addWayDB(w,tok)
	for r in relations:
		log.info("Adding Relation:"),
		log.debug(procCnt/totalCount)
		procCnt=procCnt+1
		addRelationDB(r,tok)
		cnt=0
		for m in r['member']:
			addRelLinkDB(m,r['id'],cnt,tok)
			cnt=cnt+1
	setSetting("lastBoundBox",getSetting("boundBox"))
	setSetting("lastUpdate",int(retTime))

def checkGetChangeSets(tok):
	#self, min_lon=None, min_lat=None, max_lon=None, max_lat=None, userid=None, username=None, closed_after=None, created_before=None, only_open=False, only_closed=False
	boundBoxString=getSetting("boundBox")
	latLonPairs=boundBoxString.split(";")
	lat1,lon1=latLonPairs[0].split(",")
	lat2,lon2=latLonPairs[1].split(",")
	
	lastUpdate=getSetting("lastUpdate")
	tString=datetime.datetime.fromtimestamp(int(lastUpdate)).strftime('%Y-%m-%d %H:%M:%S')
	try:
		data=tok.api.ChangesetsGet(min(float(lon1),float(lon2)),min(float(lat1),float(lat2)),max(float(lon1),float(lon2)),max(float(lat1),float(lat2)),only_closed=True,closed_after=tString)
		retTime=int(time.mktime(time.gmtime()))
	except:
		return
	for d in data:
		log.info("Change Set: "+str(d))
		log.debug(data[d])
		changeData=tok.api.ChangesetDownload(d)
		#changeData is a list of dicts
		#'type': node|way|relation
		#'action': create|delete|modify
		#'data' : {}
		#'data' will then have the standard data for that type 'id', 'username','changeset' ect
		
		#if action is add, we can just add as normal
		#if its update. I think the best way would be to remove all referance, and re- add
		#if its delete then just remove all referance. Not going to worry about cacheing anything at this point. 
		suc=True  #think we are good, until we are not
		for c in changeData:
			if c['action']=="delete":
				# we are removing the element
				if c['type']=='way':
					if not removeWayDB(c['data'],tok):
						suc=False
				elif c['type']=='node':
					if not removeNodeDB(c['data'],tok):
						suc=False
				elif c['type']=='relation':
					if not removeRelationDB(c['data'],tok):
						suc=False
				else:
					print("Unknown Type for Removal")
			elif c['action']=='create':
				#we are making a new element
				if c['type']=='way':
					addWayDB(c['data'],tok)
					cnt=0
					for n in c['data']['nd']:
						addLinkDB(n,c['data']['id'],cnt,tok)
						cnt=cnt+1
				elif c['type']=='node':
					addNodeDB(c['data'],tok)
				elif c['type']=='relation':
					addRelationDB(c['data'],tok)
					cnt=0
					for m in c['data']['member']:
						addRelLinkDB(m,c['data']['id'],cnt,tok)
						cnt=cnt+1
				else:
					log.warning("Unknown Type for Removal")
			elif c['action']=='modify':
				#updating an element, probably delete it, and readd
				if c['type']=='way':
					if not removeWayDB(c['data'],tok):
						suc=False
					addWayDB(c['data'],tok)
					cnt=0
					for n in c['data']['nd']:
						addLinkDB(n,c['data']['id'],cnt,tok)
						cnt=cnt+1
				elif c['type']=='node':
					if not removeNodeDB(c['data'],tok):
						suc=False
					addNodeDB(c['data'],tok)
				elif c['type']=='relation':
					if not removeRelationDB(c['data'],tok):
						suc=False
					addRelationDB(c['data'],tok)
					cnt=0
					for m in c['data']['member']:
						addRelLinkDB(m,c['data']['id'],cnt,tok)
						cnt=cnt+1
				else:
					log.warning("Unknown Type for Removal")
			else:
				log.warning("Unknown Action:"+c['action'])
		if suc:
			setSetting("lastUpdate",int(retTime))	
	#once we process and make these changes, we need to update the lastUpdate setting to mark we are current


def getMyChangeSets(tok):
	data=tok.api.ChangesetsGet(username="gibeautc")
	#print(data)
	m = hashlib.md5()
	m.update(str(data).encode('utf-8'))
	csMd5=str(m.hexdigest())
	if csMd5!=getSetting("myChangeHash"):
		log.warning("There are changes to my changesets")
		setSetting("myChangeHash",str(csMd5))
	
#Notes area
# Nodes added that we want to push to main OSM server will not have a changeset
# If we add nodes just for local use, we will give them a changeset of -1
# They also will not have a node ID......how are we actully dealing with this

if __name__=="__main__":
	mainToken=Token()
	buildDB(False,mainToken)
	#getFullMap(mainToken)
	while True:
		checkSetLogLevel()
		if getSetting("boundBox")!=getSetting("lastBoundBox"):
			getFullMap(mainToken)
		checkGetChangeSets(mainToken)
		getMyChangeSets(mainToken)
		time.sleep(10)
