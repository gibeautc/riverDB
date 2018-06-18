#!/usr/bin/env python


#Library for geometric type functions




def isPointInPolygon(point,poly):
	#returns true if point is inside polygon
	pass
	
	
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
