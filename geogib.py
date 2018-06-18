#!/usr/bin/env python


#Library for geometric type functions
import time
from math import sin, cos, sqrt, atan2, radians



def isPointInPolygon(point,poly):
	#returns true if point is inside polygon, false if not
	try:
		i=point['id']
		lat=point['lat']
		lon=point['lon']
	except:
		#we were just given lat/lon pair
		lat=point[0]
		lon=point[1]
	#poly should be given as list of lat/lon pairs, dont want to deal with database connection in this lib to pull node info
	
	#get bounding box cords(min/max)
	#check 
		
		
	
	
def doLineSegmentsIntersect(l1,l2):
	#returns the cords for intersection if they do, return None if not
	pass
	
	
def doesWayCrossPolygon(way,poly):
	#retuns a list of points cords where way(multiple line segments) crosses a polygon (closed way)
	#used for error checking that a river way falls within a riverbank polygon
	#Eventually need to upgrade this to a relationship or multiple polygons since a riverbank will rarely be a single way
	pass


def findDistanceOfWay(w,start=None,end=None):
	#returns the distance in ft of a way. Optional start and end node id's, if not used will return the entires length
	#also will check if way is closed?
	pass
	
	
def findDistnace(p1,p2):
	#return distance in ft between two points
	try:
		lat1=p1['lat']
		lon1=p1['lon']
	except:
		try:
			lat1=float(p1[0])
			lon1=float(p1[1])
		except:
			print('failed to parse point one')
			return None
	
	try:
		lat2=p2['lat']
		lon2=p2['lon']
	except:
		try:
			lat2=float(p2[0])
			lon2=float(p2[1])
		except:
			print('failed to parse point two')
			return None
	
	R = 6373.0
	lat1 = radians(lat1)
	lon1 = radians(lon1)
	lat2 = radians(lat2)
	lon2 = radians(lon2)
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))
	d = R * c
	#currently in km 
	return int(d*3280.84)
	

def test():
	print("Starting Tests")
	#---------------Distance(pair)--------------------
	tp1=[44.615760,-123.073796]#27th and fulton
	tp2=[44.615771,-123.072643]#27th and waverly
	t=time.time()
	d=findDistnace(tp1,tp2)
	t=time.time()-t
	if d==299:
		print("findDistance(pair): PASS "+str(t))
	else:
		print("findDistance(pair): FAIL "+str(t))
	#---------------Distance(dict)--------------------
	tp1={}#27th and fulton
	tp2={}#27th and waverly
	tp1['lat']=44.615760
	tp1['lon']=-123.073796
	tp2['lat']=44.615771
	tp2['lon']=-123.072643
	t=time.time()
	d=findDistnace(tp1,tp2)
	t=time.time()-t
	if d==299:
		print("findDistance(dict): PASS "+str(t))
	else:
		print("findDistance(dict): FAIL "+str(t))
	
	
if __name__=="__main__":
	test()
