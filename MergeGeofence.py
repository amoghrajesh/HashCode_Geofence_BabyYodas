







from shapely.geometry import Polygon
import pylab


########intersect##############

def Intersect(Polygon1Cords,Polygon2Cords):
	p1=Polygon(Polygon1Cords)
	p2=Polygon(Polygon2Cords)

	return p1.intersects(p2)



##########get all geofence and merge ##########


#source gfg

class Point: 
	def __init__(self, x, y): 
		self.x = x 
		self.y = y 

def Left_index(points): 
	
	
	minn = 0
	for i in range(1,len(points)): 
		if points[i].x < points[minn].x: 
			minn = i 
		elif points[i].x == points[minn].x: 
			if points[i].y > points[minn].y: 
				minn = i 
	return minn 

def orientation(p, q, r): 
	
	val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y) 

	if val == 0: 
		return 0
	elif val > 0: 
		return 1
	else: 
		return 2

def convexHull(points, n): 

	if n < 3: 
		return

	l = Left_index(points) 

	hull = [] 
	
	p = l 
	q = 0
	while(True): 
		
		 
		hull.append(p) 

		
		q = (p + 1) % n 

		for i in range(n): 
			
			 
			if(orientation(points[p], 
						points[i], points[q]) == 2): 
				q = i 

		
		p = q 

		
		if(p == l): 
			break

	
	toreturn=[]
	for each in hull: 
		toreturn.append((points[each].x, points[each].y)) 
	return toreturn
	







def merge(Geofences):
	finalgeofence=[]
	foundIntersect=1
	temList=list(Geofences)

	tempdict=Geofences.copy()


	while(foundIntersect==1):
		foundIntersect=0
		temList=list(tempdict)
		

		for i in range(0,len(temList)-1):

			
			firstitem=tempdict[temList[i]]
			
			firstID=temList[i]

			firstLatitues=firstitem["Latitudes"]

			firstLongtitudes=firstitem["Longitudes"]


			wegotsomething=0
			for j in range(i+1,len(temList)):

				seconditem=tempdict[temList[j]]
				
				secondID=temList[j]

				secondLatitues=seconditem["Latitudes"]

				secondLongtitudes=seconditem["Longitudes"]



				firstcoordinates=list(zip(firstLatitues,firstLongtitudes))
				secondcoordinates=list(zip(secondLatitues,secondLongtitudes))


				#print("ppebfabubvuaeb")

				#print(firstcoordinates)
				#print()
				#print(secondcoordinates)

				if Intersect(firstcoordinates,secondcoordinates):


					foundIntersect=1

					NewId=(firstID+secondID)*2   #sumofboth ids *2

					points=[]

					wegotsomething=1

					for pp in firstcoordinates:

						points.append(Point(pp[0],pp[1]))

					for pp in secondcoordinates:

						points.append(Point(pp[0],pp[1]))

					tempdict.pop(firstID)

					tempdict.pop(secondID)

					hullreturn=convexHull(points,len(points))
					newLatitudes=[]
					newLongitutes=[]

					for pp in hullreturn:
						newLatitudes.append(pp[0])
						newLongitutes.append(pp[1])

					tempdict[NewId]={"Latitudes":newLatitudes,"Longitudes":newLongitutes}

					break

			if wegotsomething==1:
				break

	#print(tempdict)

	return tempdict






##################testing ##############################

'''
x1=[12.936086817779337, 12.93494182375999, 12.93518232522289, 12.936541676958543]
y1=[77.53373956530413, 77.5336269125255, 77.53567612021288, 77.53495728819689]

x2=[12.936400513853748, 12.935307804154974, 12.93466995226186, 12.934758833361144]
y2=[77.53552055209002, 77.5344905838283, 77.53476416914782, 77.53593361227831]

Geofences={}
Geofences[1]={"Latitudes":x1,"Longitudes":y1}
Geofences[2]={"Latitudes":x2,"Longitudes":y2}



merge(Geofences)
'''


			









'''

(1, '1', 'polygon', '', '(12.935775792599, 77.53394353922)', '12.93629594853946#12.93519215123005#12.935354228165727#12.936311002769298', '77.53353035300097#77.53324474486331#77.53447319659213#77.5345751205347', '', '-5.76936e-08')
(2, '2', 'polygon', '', '(12.935318076723, 77.534593693507)', '12.935882284548246#12.935762034183197#12.934935964891165#12.934794800877723#12.935432652451622', '77.53494526537875#77.53400112780551#77.5339260259531#77.53530468138675#77.535170570936', '', '-5.7570799999999996e-08')
(3, '3', 'polygon', '', '(12.936502816484, 77.535748487404)', '12.936812915847907#12.93613846991528#12.936086187208675#12.936776318053392#12.936786774566663#12.937184121745917', '77.53535832556705#77.53518129977206#77.53622199686984#77.53629173430423#77.53582502993564#77.53565873297671', '', '-3.8291300000000005e-08')
(4, '4', 'polygon', '', '(12.93600237673, 77.536419742275)', '12.936577644218053#12.935286260431319#12.935500620146131#12.936682209414279', '77.53574456366519#77.53577675017337#77.53716077002505#77.53702665957431', '', '-8.307835000000001e-08')
'''




x1=[12.93629594853946,12.93519215123005,12.935354228165727,12.936311002769298]
y1=[77.53353035300097,77.53324474486331,77.53447319659213,77.5345751205347]

x2=[12.935882284548246,12.935762034183197,12.934935964891165,12.934794800877723,12.935432652451622]
y2=[77.53494526537875,77.53400112780551,77.5339260259531,77.53530468138675,77.535170570936]

x3=[12.936812915847907,12.93613846991528,12.936086187208675,12.936776318053392,12.936786774566663,12.937184121745917]
y3=[77.53535832556705,77.53518129977206,77.53622199686984,77.53629173430423,77.53582502993564,77.53565873297671]

x4=[12.936577644218053,12.935286260431319,12.935500620146131,12.936682209414279]
y4=[77.53574456366519,77.53577675017337,77.53716077002505,77.53702665957431]



Geofences={}
Geofences[1]={"Latitudes":x1,"Longitudes":y1}
Geofences[2]={"Latitudes":x2,"Longitudes":y2}

Geofences[3]={"Latitudes":x3,"Longitudes":y3}
Geofences[4]={"Latitudes":x4,"Longitudes":y4}


merge(Geofences)
