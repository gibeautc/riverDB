#!/usr/bin/env python3


#River OSM Data

#collect/store and update River Related Data. This database should then be able to be handed off to the client, or exported as xml (.osm) document
#start with small area then expand to PNW

#have bounding box of area, request all data (first time through)

from riverUtils import * 
from osmapi import OsmApi
import os
import time
import sys
import sqlite3



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
		print("Deleting Database")
		time.sleep(1)
		try:
			os.remove('river.db')
		except:
			pass
		tok.connectDB()
	print("Building Database")
	tok.curs.execute('CREATE TABLE IF NOT EXISTS nodes(id bigint,lat float(8,5),lon float(8,5),changeset bigint,tags text,version int,user varchar(20),uid int,ts datetime,visible bool,primary key(id))')
	tok.curs.execute('CREATE TABLE IF NOT EXISTS ways(id bigint,changeset,tags text,version int,user varchar(20),uid int,ts datetime,visible bool,primary key(id))')
	tok.curs.execute('CREATE TABLE IF NOT EXISTS links(nid bigint,wid bigint,ord int,primary key(nid,wid))')
	tok.db.commit()
	print("Database Build Complete")

def addNodeDB(n,tok):
	db_out=[str(n['id']),str(n['lat']),str(n['lon']),str(n['tag']),str(n['changeset']),str(n['version']),str(n['user']),str(n['uid']),str(n['timestamp']),str(n['visible'])]
	q="insert or replace into nodes(id,lat,lon,tags,changeset,version,user,uid,ts,visible) values(?,?,?,?,?,?,?,?,?,?)"
	try:
		tok.curs.execute(q,db_out)
		tok.db.commit()
	except:
		tok.db.rollback()
		print("Error Adding Node")
		print(sys.exc_info())
		
def addWayDB(n,tok):
	db_out=[str(n['id']),str(n['tag']),str(n['changeset']),str(n['version']),str(n['user']),str(n['uid']),str(n['timestamp']),str(n['visible'])]
	q="insert or replace into ways(id,tags,changeset,version,user,uid,ts,visible) values(?,?,?,?,?,?,?,?)"
	try:
		tok.curs.execute(q,db_out)
		tok.db.commit()
	except:
		tok.db.rollback()
		print("Error Adding Way")
		print(sys.exc_info())

def addLinkDB(nid,wid,index,tok):
	db_out=[str(nid),str(wid),str(index)]
	q="insert or replace into links(nid,wid,ord) values(?,?,?)"
	try:
		tok.curs.execute(q,db_out)
		tok.db.commit()
	except:
		tok.db.rollback()
		print("Error Adding Link")
		print(sys.exc_info())

def getFullMap(tok):
	#will update if we already have data in database, but it will still be slow
	boundBoxString=getSetting("boundBox")
	latLonPairs=boundBoxString.split(";")
	lat1,lon1=latLonPairs[0].split(",")
	lat2,lon2=latLonPairs[1].split(",")
	
	data=tok.api.Map(min(float(lon1),float(lon2)),min(float(lat1),float(lat2)),max(float(lon1),float(lon2)),max(float(lat1),float(lat2)))
	if data is None or len(data)<1:
		print("Bad data returned from map function?")
		return
	nodes=[]
	ways=[]
	relations=[]
	totalCount=len(data)
	print("Returned "+str(totalCount)+" elements")
	retTime=time.time()
	procCnt=0
	for d in data:
		print("Sorting:"),
		print(procCnt/totalCount)
		procCnt=procCnt+1
		if d['type']=='node':
			nodes.append(d['data'])
		if d['type']=='way':
			ways.append(d['data'])
		if d['type']=='relation':
			relations.append(d['data'])
	print("Number of Nodes: "+str(len(nodes)))
	print("Number of Ways: "+str(len(ways)))
	print("Number of Relations: "+str(len(relations)))
	 
	procCnt=0
	for n in nodes:
		addNodeDB(n,tok)
		print("Adding Node:"),
		print(procCnt/totalCount)
		procCnt=procCnt+1
	for w in ways:
		print("Adding Way:"),
		print(procCnt/totalCount)
		procCnt=procCnt+1
		cnt=0
		for n in w['nd']:
			addLinkDB(n,w['id'],cnt,tok)
			cnt=cnt+1
		addWayDB(w,tok)
	setSetting("lastBoundBox",getSetting("boundBox"))
	setSetting("lastUpdate",int(retTime))

def checkGetChangeSets(tok):
	#self, min_lon=None, min_lat=None, max_lon=None, max_lat=None, userid=None, username=None, closed_after=None, created_before=None, only_open=False, only_closed=False
	boundBoxString=getSetting("boundBox")
	latLonPairs=boundBoxString.split(";")
	lat1,lon1=latLonPairs[0].split(",")
	lat2,lon2=latLonPairs[1].split(",")
	
	data=tok.api.ChangesetsGet(min(float(lon1),float(lon2)),min(float(lat1),float(lat2)),max(float(lon1),float(lon2)),max(float(lat1),float(lat2)),only_closed=True,closed_after=getSetting("lastUpdate"))
	print(data)

#Notes area
# Nodes added that we want to push to main OSM server will not have a changeset
# If we add nodes just for local use, we will give them a changeset of -1

if __name__=="__main__":
	mainToken=Token()
	buildDB(False,mainToken)
	while True:
		if getSetting("boundBox")!=getSetting("lastBoundBox"):
			getFullMap(mainToken)
		checkGetChangeSets(mainToken)
		time.sleep(10)
