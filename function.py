
"""
keep all distances in Km, if lat[] or long[] has one value, type is circle
1. find centroid(rad=NULL, type, centroid, lat[], long[]); return (lat, long)
2. calculate buffer distance based on size in Km(rad=NULL, type, centroid, lat[], long[]) [maybe consider (0.1) * distance b/w farthest 2 points] return dist
3. Find status of a user to a geofence considering buffer(rad=NULL, type, centroid, lat[], long=[], buffer, user_coords[lat, long]); 
    a. status = 0 if out, 1 if in
    b. compute shortest distance from boundary; dist is neg if point is inside, positive if outside
    c. compute coordinate on geofence for shortest distance on boundary (edge_lat, edge_long)
    return (status, dist, (edge_lat, edge_long))
4. Given all geofences find geofences within (x) Km (dict{"geofence_id":{'rad':x, 'type':t, 'centroid':y, 'lat':[], 'long':[]}, x=5)
    for all such geofences get info from function no. 3
    return {'id1':[status, dist, (edge_lat, edge_long)] , 'id2':[...]....}
"""





import math
INT_MAX=10000


def GetPolygonArea(type,Latitudes,Longitudes,rad=None):
	if type=="Circle":
		Area=math.pi *(rad**2)
		return Area

	else:
		Area=0

		for i in range (len(Latitudes)):
			x0=Latitudes[i]
			x1=Latitudes[(i+1)%len(Latitudes)]

			y0=Longitudes[i]
			y1=Longitudes[(i+1)%len(Longitudes)]

			temparea=(x0*y1)-(x1*y0)
			Area+=temparea


		Area*=0.5
		Area=round(Area,12)

		return Area


#taken from gfg
def GetMinDistance(A, B, E) : 

	AB = [None, None]; 
	AB[0] = B[0] - A[0]; 
	AB[1] = B[1] - A[1]; 


	BE = [None, None]; 
	BE[0] = E[0] - B[0]; 
	BE[1] = E[1] - B[1]; 


	AE = [None, None]; 
	AE[0] = E[0] - A[0]; 
	AE[1] = E[1] - A[1]; 


	AB_BE = AB[0] * BE[0] + AB[1] * BE[1]; 
	AB_AE = AB[0] * AE[0] + AB[1] * AE[1]; 


	Ans = 0; 

	coordinate=[]

	if (AB_BE > 0) : 

		#print("1")
		y = E[1] - B[1]; 
		x = E[0] - B[0]; 
		coordinate=[B[0],B[1]]
		Ans = math.sqrt(x * x + y * y); 

	 
	elif (AB_AE < 0) : 
		#print("2")
		y = E[1] - A[1]; 
		x = E[0] - A[0]; 
		coordinate=[A[0],A[1]]
		Ans = math.sqrt(x * x + y * y); 


	else: 

		#print("3")
		x1 = AB[0]; 
		y1 = AB[1]; 
		x2 = AE[0]; 
		y2 = AE[1]; 
		#print("p")
		coordinate=[(A[0]+B[0])/2,(A[1]+B[1])/2]
		mod = math.sqrt(x1 * x1 + y1 * y1); 
		Ans = abs(x1 * y2 - y1 * x2) / mod; 

	Ans=round(Ans,12)
	return (Ans,coordinate); 


#orientation dointersect and isinside
#source gfg

def orientation(p:tuple, q:tuple, r:tuple) -> int:
	
	val = (((q[1] - p[1]) *
			(r[0] - q[0])) -
		((q[0] - p[0]) *
			(r[1] - q[1])))
			
	if val == 0:
		return 0
	if val > 0:
		return 1 
	else:
		return 2 




def doIntersect(p1, q1, p2, q2):
	
	# Find the four orientations needed for 
	# general and special cases 
	o1 = orientation(p1, q1, p2)
	o2 = orientation(p1, q1, q2)
	o3 = orientation(p2, q2, p1)
	o4 = orientation(p2, q2, q1)

	# General case
	if (o1 != o2) and (o3 != o4):
		return True
	
	# Special Cases 
	# p1, q1 and p2 are colinear and 
	# p2 lies on segment p1q1 
	if (o1 == 0) and (onSegment(p1, p2, q1)):
		return True

	# p1, q1 and p2 are colinear and 
	# q2 lies on segment p1q1 
	if (o2 == 0) and (onSegment(p1, q2, q1)):
		return True

	# p2, q2 and p1 are colinear and 
	# p1 lies on segment p2q2 
	if (o3 == 0) and (onSegment(p2, p1, q2)):
		return True

	# p2, q2 and q1 are colinear and 
	# q1 lies on segment p2q2 
	if (o4 == 0) and (onSegment(p2, q1, q2)):
		return True

	return False





# Returns true if the point p lies 
# inside the polygon[] with n vertices 


def is_inside_polygon(points:list, p:tuple) -> bool:
	
	n = len(points)
	
	# There must be at least 3 vertices
	# in polygon
	if n < 3:
		return False
		
	# Create a point for line segment
	# from p to infinite
	extreme = (INT_MAX, p[1])
	count = i = 0
	
	while True:
		next = (i + 1) % n
		
		# Check if the line segment from 'p' to 
		# 'extreme' intersects with the line 
		# segment from 'polygon[i]' to 'polygon[next]' 
		if (doIntersect(points[i],
						points[next], 
						p, extreme)):
							
			# If the point 'p' is colinear with line 
			# segment 'i-next', then check if it lies 
			# on segment. If it lies, return true, otherwise false 
			if orientation(points[i], p, 
						points[next]) == 0:
				return onSegment(points[i], p, 
								points[next])
								
			count += 1
			
		i = next
		
		if (i == 0):
			break
	
	return (count % 2 == 1)




def isInsideCircle(cx,cy,rad,x,y):
	if ( (((x-cx)*2) +( (y-cy)**2) ) <= rad**2):
		return True
	else:
		return False



#1. find centroid(rad=NULL, type, centroid, lat[], long[]); return (lat, long)

def Centroid(type,Latitudes,Longitudes,rad=None):

	if(type=="Circle"):

		return (Latitudes[0],Longitudes[0])


	else:
		

		ans=[0,0]
		signedArea=0

		for i in range (len(Latitudes)):
			x0=Latitudes[i]
			x1=Latitudes[(i+1)%len(Latitudes)]

			y0=Longitudes[i]
			y1=Longitudes[(i+1)%len(Longitudes)]

			area=(x0*y1)-(x1*y0)
			signedArea+=area

			ans[0]+=(x0+x1)*area
			ans[1]+=(y0+y1)*area

		signedArea*=0.5
		ans[0] = (ans[0]) / (6 * signedArea) 
		ans[1] = (ans[1]) / (6 * signedArea) 


		'''Latitudelength=len(Latitudes)
		Longitudelength=len(Longitudes)

		CentroidLatitute=sum(Latitudes)/Latitudelength
		CentroidLongitute=sum(Longitudes)/Longitudelength

		return (CentroidLatitute,CentroidLongitute)'''




		ans[0]=round(ans[0],12)
		ans[1]=round(ans[1],12)

		final=(ans[0],ans[1])

		#print(final)
		return final




#2. calculate buffer distance based on size in Km(rad=NULL, type, centroid, lat[], long[]) [maybe consider (0.1) * distance b/w farthest 2 points] return dist

def CalculateBufferDistance(type,Latitudes,Longitudes,rad=None):

	#considering 5 percent of the area
	bufferdistance=0
	Polygonarea=GetPolygonArea(type,Latitudes,Longitudes,rad)

	bufferdistance=0.05*Polygonarea
	return bufferdistance



	

'''
3. Find status of a user to a geofence considering buffer(rad=NULL, type, centroid, lat[], long=[], buffer, user_coords[lat, long]); 
    a. status = 0 if out, 1 if in
    b. compute shortest distance from boundary; dist is neg if point is inside, positive if outside
    c. compute coordinate on geofence for shortest distance on boundary (edge_lat, edge_long)
    return (status, dist, (edge_lat, edge_long))'''







def GetStatus(type,centroid,Latitudes,Longitudes,Buffferdistance,user_coords,rad=None):
	minDistance=math.inf
	mincoordinate=[None,None]
	if(type=="Circle"):
		tempstatus=isInsideCircle(Latitudes[0],Longitudes[0],rad,user_coords[0],user_coords[1])
		status=1
		if(tempstatus==False):
			status=0

		minDistance= math.sqrt( (Latitudes[1]-user_coords[0])**2 + (Longitudes[1]-user_coords[1])**2)


		return (status,minDistance,mincoordinate)

	else:


		PolygonPoints=list(zip(Latitudes,Longitudes))
		tempstatus=is_inside_polygon(PolygonPoints,user_coords)
		status=1
		if(tempstatus==False):
			status=0


		
		
		for i in range(0,len(Latitudes)):
			x0=Latitudes[i]
			x1=Latitudes[(i+1)%len(Latitudes)]

			y0=Longitudes[i]
			y1=Longitudes[(i+1)%len(Longitudes)]
			tempdis,tempcoordinates=GetMinDistance([x0,y0],[x1,y1],[user_coords[0],user_coords[1]])
			#print(tempdis,tempcoordinates,(x0,y0),(x1,y1))
			if tempdis<minDistance:
				mincoordinate=tempcoordinates
				minDistance=tempdis


		return (status,minDistance,mincoordinate)




			


	


















#[ (0, 0), (10, 0), (10, 10), (0, 10) ]

#check functions

#Centroid("poly",[1,3,6],[2,-4,-7])
#print(CalculateBufferDistance("Poly",[0,4,4,0],[0,0,4,4],None))
#print(CalculateBufferDistance("Circle",[],[],4))
#print(GetStatus("Poly",[],[0,10,10,0],[0,0,10,10],9,[5,5]))

print(GetStatus("Poly",[],[0,10,10,0],[0,0,10,10],9,[5,5]))
