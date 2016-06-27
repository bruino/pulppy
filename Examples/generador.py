#import random
#vector = []
#while len(vector)<10:
#	c = random.randint(1,10)
#	valor = False
#	for i in range(0,len(vector)):
#		if(valor == False):
#			valor = vector[i] == c
#		else:
#			break
#	if(valor != True):
#		vector.append(c)			
#print vector
import random
print random.sample(range(1, 11), len(range(1, 11)))
