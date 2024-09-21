from multiprocessing import Pool
import requests

def procesar_datos(datos):
	requests.post("https://clioscan.com.co/block/"+datos)
temp=[]
for i in range(1,999):
	temp.append(str(i))
with Pool(processes=4) as pool:
	resultados = pool.map(procesar_datos, temp)
print("P1")
for i in range(1,669):
	temp=[]
	i=str(i)
	print(i)
	for j in range(0,999):
		j=str(j)
		if len(j)==1:
			j=i+"00"+j
		elif len(j)==2:
			j=i+"0"+j
		else:
			j=i+j
		temp.append(j)
		
		
	with Pool(processes=4) as pool:
	    resultados = pool.map(procesar_datos, temp)