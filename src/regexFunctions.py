import regex as re

#Originalmente asi estaban compuestas nuestras tablas 
#la posicion de renglon y columna nos indica el codigo objeto
#las instrucciones se encuentran puras(solo instruccion o 
#todas las posibles combinaciones de registros validas) y 
#las que no son puras como las que contienen etiqutas, 
#direcciones o valores.
#___________________________________________________________
#  | 0                  | 1                  | 2                  
#0 | nop                | ld bc, {w}         | ld (bc), a         
#1 | djnz {+b}          | ld de, {w}         | ld (de), a        
#2 | jr nz, {+b}        | ld hl, {w}         | ld ({data}), hl    
#3 | jr nc, {+b}        | ld sp, {w}         | ld ({data}), a     
#____________________________________________________________

#El codigo que contiene cada instruccion que no es pura es el 
#siguiente:
#______________________________________________
#{b} valor de un byte, ejemplo 		  LD A, {b}
#{w} valor o direccion 2 bytes 		  LD HL, {w}
#{data} 2 bytes direccion      		  LD HL, ({data})
#{code} Etiquta                		  CALL {code}
#{+b} desplazamiento rango(-126, 129) JR {+b}
#{+i} indice de un byte               LD (IX+{+i}), A
#______________________________________________

#La informacion de las tablas se compuso en un diccionario de python
#y se serializo para cargarlo cada vez que se utilice el programa

#para poder usarlo hay dos situaciones:

#Si la instruccion es pura, simplemente la llave para el diccionario es 
#la misma instruccion

#Si no es pura entonces se tiene que hacer un tratamiento, las siguientes
#funciones hacen el tratamiento de la instruccion para poderla 
#transformar, en una llave para poder acceder al contenido del 
#diccionario para esa llave.



#____________________________________________________________
#def least_significant()
#Esta funcion convierte los valores en un formato de 2 bytes o 
#de uno acomodando del byte menos significatne al mas significante
#____________________________________________________________

def least_significant(value,pat):
	pat=pat
	
	
	if pat==1:
		data=["0","0","0","0"]
		j=len(data)-1
		
		c=value
		c=list(c)
	if pat==2:
		data=["0","0"]
		j=len(data)-1
		c=value
		c=list(c)

	for i in range(len(c)-1,-1,-1):

		data[j]=c[i]
		j-=1
	data[:2],data[2:]=data[2:],data[:2]
	data="".join(data)


	return data
	



def pat1(inst):#{data}
	cl=2
	pattern4=re.compile("\(\wh\)")
	pattern3=re.compile("\(\w{2}h\)")
	pattern2=re.compile("\(\w{3}h\)")
	pattern1=re.compile("\(\w{4}h\)")
	patterns=[pattern1,pattern2,pattern3,pattern4]
	for pattern in patterns:
		search=pattern.search(inst)
		if search:
			insta=search.group()
			value=insta[1:len(insta)-2]

			inst=inst.replace(insta,"({data})")
			
			value=least_significant(value,1)
			return inst, cl,value

	return False


def pat2(inst):#{b}
	cl=1
	pattern1=re.compile(r", \w{2}h")	
	pattern2=re.compile(r", \wh")
	pattern3=re.compile(r" \w{2}h")
	pattern4=re.compile(r" \wh")

	patterns=[pattern1,pattern2]
	i=0
	for pattern in patterns:
		search=pattern.search(inst)
		i+=1
		if search:
			position=search.span()
			insta=search.group()
			value=least_significant(insta[2:len(insta)-1],2)

			
			inst=inst.replace(insta,", {b}")
			
			return inst, cl, value
			

	patterns=[pattern3,pattern4]
	for pattern in patterns:
		search=pattern.search(inst)
		i+=1
		if search:
			position=search.span()
			insta=search.group()
			value=least_significant(insta[1:len(insta)-1],2)
			inst=inst.replace(insta," {b}")
			return inst, cl, value

	return False
	


def pat3(inst):#{w}
	#print(len(inst[:5]))
	cl=2

	#wlist=["ld bc","ld be","ld hl","ld sp","ld ix","ld iy"]
	wlist=["ld bc","ld de","ld hl","ld sp","ld ix","ld iy"]
	
	if inst[:5] in wlist:

		pattern1=re.compile(r" \w{4}h")	
		pattern2=re.compile(r" \w{3}h")
		pattern3=re.compile(r" \w{2}h")
		pattern4=re.compile(r" \wh")

		#patterns=[pattern1,pattern2,pattern3,pattern4]
		patterns=[pattern4,pattern3,pattern2,pattern1]

		i=0
		for pattern in patterns:
			search=pattern.search(inst)
			i+=1
			if search:
				position=search.span()
				insta=search.group()
				value=least_significant(insta[1:len(insta)-1],1)
				inst=inst.replace(insta," {w}")
			
				return inst, cl, value
		return False	
	return False



def pat4(inst):#{code}
	cl=2
	jump=False
	flags=["nz,","nc,","po,","p,","z,","c,","pe,","m,"]

	if inst[:4]=="call":#call
		if inst[5:7] in flags:#dos
			value=inst[8:]
			inst=inst.replace(inst[8:],"{code}")
			
			return inst, cl,value, jump


		if inst[5:6] in flags:#uno

			value=inst[7:]
			inst=inst.replace(inst[7:],"{code}")
			
			return inst, cl,value, jump

		value=inst[5:]
		inst=inst.replace(inst[5:],"{code}")	
		return inst, cl,value, jump


	if inst[:2]=="jp":#jp
		if inst[3:6] in flags:#dos
			value=inst[7:]
			inst=inst.replace(inst[7:],"{code}")
			return inst, cl,value, jump


		if inst[3:5] in flags:#uno
			value=inst[6:]
			inst=inst.replace(inst[6:],"{code}")
			return inst, cl,value, jump

		value=inst[3:]
		inst=inst.replace(inst[3:],"{code}")
		return inst, cl,value, jump

	return False


def pat5(inst):#{+b}
	flags=["nz,","nc,","z,","c,"]
	cl=1
	jump=True
	if inst[:5]=="djnz ":
		value=inst[5:]
		inst=inst.replace(inst[5:],"{+b}")
		return inst, cl, value, jump

	if inst[:3]=="jr ":
		if inst[3:6] in flags:
			value=inst[7:]
			inst=inst.replace(inst[7:],"{+b}")
			return inst, cl, value, jump

		if inst[3:5] in flags:
			value=inst[6:]
			inst=inst.replace(inst[6:],"{+b}")
			return inst, cl, value, jump

		value=inst[3:]
		inst=inst.replace(inst[3:],"{+b}")
		return inst,cl, value, jump

	return False



def pat6(inst):#{+i}
	cl=1
	pattern1=re.compile("\+\w{2}h")
	pattern2=re.compile("\+\wh")
	patterns=[pattern1,pattern2]
	for pattern in patterns:
		search=pattern.search(inst)
		if search:
			insta=search.group()
			value=least_significant(insta[1:len(insta)-1],2)
			inst=inst.replace(insta,"{+i}")
			
			if pat2(inst):
				inst,b,c=pat2(inst)
				value=value+c
			
			return inst, cl, value
	return False


