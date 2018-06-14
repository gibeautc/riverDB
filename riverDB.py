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
		self.api=OsmApi()
	def connectDB(self):
		self.db,self.curs=openDB()
	def closeDB(self):
		self.db.close()

def openDB():
	d=sqlite3.connect('map.db')
	c=d.cursor()
	return d,c
	
def buildDB(full,tok):
	if full:
		print("Deleting Database")
		time.sleep(1)
		os.remove('map.db')
		tok.connectDB()
	print("Building Database")
	tok.curs.execute('CREATE TABLE IF NOT EXISTS nodes(id bigint,lat float(8,5),lon float(8,5),changeset bigint,tags text,version int,user varchar(20),uid int,ts datetime,visible bool,primary key(id))')
	tok.curs.execute('CREATE TABLE IF NOT EXISTS ways(id bigint,changeset,tags text,version int,user varchar(20),uid int,ts datetime,visible bool,primary key(id))')
	tok.curs.execute('CREATE TABLE IF NOT EXISTS links(nid bigint,wid bigint,ord int,primary key(nid,wid))')
	tok.db.commit()
	print("Database Build Complete")

def addNodeDB(n,tok):
	db_out=[str(n['id']),str(n['lat']),str(n['lon']),str(n['tag']),str(n['changeset']),str(n['version']),str(n['user']),str(n['uid']),str(n['timestamp']),str(n['visible'])]
	q="insert or ignore into nodes(id,lat,lon,tags,changeset,version,user,uid,ts,visible) values(?,?,?,?,?,?,?,?,?,?)"
	try:
		tok.curs.execute(q,db_out)
		tok.db.commit()
	except:
		tok.db.rollback()
		print("Error Adding Node")
		print(sys.exc_info())
		
def addWayDB(n,tok):
	db_out=[str(n['id']),str(n['tag']),str(n['changeset']),str(n['version']),str(n['user']),str(n['uid']),str(n['timestamp']),str(n['visible'])]
	q="insert or ignore into ways(id,tags,changeset,version,user,uid,ts,visible) values(?,?,?,?,?,?,?,?)"
	try:
		tok.curs.execute(q,db_out)
		tok.db.commit()
	except:
		tok.db.rollback()
		print("Error Adding Way")
		print(sys.exc_info())

def addLinkDB(nid,wid,index,tok):
	db_out=[str(nid),str(wid),str(index)]
	q="insert or ignore into links(nid,wid,ord) values(?,?,?)"
	try:
		tok.curs.execute(q,db_out)
		tok.db.commit()
	except:
		tok.db.rollback()
		print("Error Adding Link")
		print(sys.exc_info())

def getFullMap(tok):
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
	print("Returned "+str(len(data))+" elements")
	return 
	for d in data:
		if d['type']=='node':
			nodes.append(d['data'])
		if d['type']=='way':
			ways.append(d['data'])
		if d['type']=='relation':
			relations.append(d['data'])
	print("Number of Nodes: "+str(len(nodes)))
	print("Number of Ways: "+str(len(ways)))
	print("Number of Relations: "+str(len(relations)))
	for n in nodes:
		addNodeDB(n,tok)
	for w in ways:
		cnt=0
		for n in w['nd']:
			addLinkDB(n,w['id'],cnt,tok)
			cnt=cnt+1
			
		addWayDB(w,tok)



if __name__=="__main__":
	mainToken=Token()
	getFullMap(mainToken)
