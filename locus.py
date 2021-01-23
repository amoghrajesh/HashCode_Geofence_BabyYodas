


import random as rd
#import pylab 

latitutes=[]
longititues=[]

for i in range(0,100):
	latitutes.append(rd.uniform(12.996800557961398, 12.91390750578042))
	longititues.append(rd.uniform(77.45285487041474,77.59344553813935))
#pylab.plot(longititues,latitutes) 
#pylab.show()
print(list(zip(latitutes,longititues))) 



