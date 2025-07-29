#encoding:utf-8
import math
from maths_add.except_error import decorate

@decorate
def isPrime(num):
	if num==1 or num==0: return False
	if num==2: return True
	if num%2==0: return False
	for i in range(3,int(math.sqrt(num))+1):
		if num%i==0: return False
	return True

@decorate
def countPrime(n):
	count=0
	for i in range(1,n+1):
		if not isPrime(i): continue
		else: count+=1
	return count

@decorate
def printPrime(n):
	result=[]
	for i in range(1,n+1):
		if not isPrime(i): continue
		else: result.append(i)
	return result



