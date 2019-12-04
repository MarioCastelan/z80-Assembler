import pickle
import hashlib
from tabulate import tabulate
import regex as re
import regexFunctions as regx

#_____________________________________________________________________________________
#Carga tabla de menomonicos y su codigo objeto
#_____________________________________________________________________________________

with open("Z80.dat","rb") as Z80tbl:
	Z80=pickle.load(Z80tbl)

#__________________
#Variables globales
cl=0
jumpDefinition={}
finalProgram=[]
jumps=[]
instCounter=0
lineCounter=0
#__________________

#_____________________________________________________________________________________
#def tohex()
#Regresa un string conteniendo la conversion de decimal a hexadecimal 
#lo regresa del byte menos signifcante al mas significante si se ingresa el
#numero de nbits como 16 (2 bytes)
#_____________________________________________________________________________________

def tohex(val, nbits, LSB=False):

	data=["0"]*int(nbits/4)
	h=hex((val + (1 << nbits)) % (1 << nbits))[2:]
	h=list(h)
	j=len(data)-1
	for i in range(len(h)-1,-1,-1):
		data[j]=h[i]
		j-=1
	if nbits==16 and LSB:
		data[:2],data[2:]=data[2:],data[:2]
	h="".join(data)

	return h.upper()

#____________________________________________________________________________________
#def assembler()
#Lee linea por linea.

#Cada vez de que se lee una linea se genera el codigo objeto(llama a toOpCode()) 
#de la instruccion y su contador de localidades.

#Si la instruccion no esta bien definida marca error y devuelve el numero
#de line de la instruccion donde marco el error.

#Si la instruccion tiene un salto al terminar se genera el codigo objeto pero solo falta
#el codigo que se genera en el salto.

#Al final de terminar de leer cada linea se verifica si hay instrucciones que quedaron con su
#codigo objeto incompleto, esto es porque eran instrucciones que involucraban saltos
#relativos o absolutos; entonces se completa su codigo objeto ya al final de haber
#leido todo el archivo. (llama a makeJumps())

#Cuando se llama a makeJumps() se hacen los saltos relativos y/o absolutos, si 
#al hacer un salto relativo, si al hacer el calculo da un numero fuera de este
#rango (-126, 129)10 marca un error 
#____________________________________________________________________________________

def assembler(file):
	global finalProgram
	finalProgram=[]
	#lee todas las instrucciones del archivo asm
	try:
		with open(file, encoding="utf8", errors='ignore') as f:
			inst=""
			prog=[]
			first_space=True
			global_counter=0
			global lineCounter
			for line in f:
				lineCounter+=1
				first_space=True
				for char in line:
					if " " in char: #esta condicion es para poder leer las etiquetas
						if first_space and inst:
						#if first_space and inst and (":" in inst):
							first_space=False
							inst=inst+char
							continue
						continue
					if ";" in char:
						break
					if "\t" in char:
						continue
					if "\n" in char:
						break
					if "," in char:
						inst=inst+char+" "
						continue
					if ":" in char:
						inst=inst+char
						toOpCode(inst.lower())
						prog.append(inst.lower())
						inst=""
						continue
					inst=inst+char
				if inst:
					#nuevo
					if len(inst.split())==1:
						inst="".join(inst.split())
	   				#fin
					ObjectCode=toOpCode(inst.lower())
			
					if ObjectCode==False:
						return ("instruccion", lineCounter)

					#prog.append(inst.lower())
				inst=""
			if jumps:
				j=makeJumps()
				if j:
					#print(j)
					return j
	
		#return True
	except FileNotFoundError:
		#print("archivo no existe")
		return "file"


#____________________________________________________________________________________
#def toOpCode()
#Esta funcion es llamada cada vez que se lee una instruccion esta, funcion analiza 
#la instruccion a traves de dos pasos: 

#Si la instruccion es pura(la instruccion no contiene direcciones, saltos(etiquetas)
# o valores)

#Si la instruccion no es una instruccion pura entonces se analiza pensando en que 
#si contiene saltos, direcciones o valores, si al analizarla no se encuentra que 
#es una instruccion se retorna error

#Una etiqueta cuenta como instruccion
#

#____________________________________________________________________________________	
def toOpCode(inst):
	#prog=getInstructions("b.txt")
	change=False
	global cl
	global jumpDefinition
	global finalProgram
	global jumps
	global instCounter
	global lineCounter

	if ":" in inst:
		jumpDefinition[inst]=cl

		finalProgram.append([inst, cl,"",""])
		change=True
		instCounter+=1
		return True
		
	if inst in Z80:#exite key en el diccionario?

		finalProgram.append([inst, cl, Z80[inst]])
		change=True
		instCounter+=1

		cl+=int(len(Z80[inst])/2)
	else:
		pats=[regx.pat3(inst),regx.pat2(inst),
		regx.pat1(inst),regx.pat4(inst),
 		regx.pat5(inst),regx.pat6(inst)]
		for i in range(len(pats)):
			
			if pats[i]:
				try:

					instruction, cltemp, value=pats[i]
					#print(instruction, i, lineCounter)
					#NEW
					#END
					try:
						finalProgram.append([inst, cl, (Z80[instruction]+value).upper()])
						change=True
						instCounter+=1
						cl+=int(len(Z80[instruction])/2+cltemp)

					except KeyError:
						
						return False

				except ValueError: #la instruccion tiene saltos
					instruction, cltemp, value, jump=pats[i]

					if jump:

						finalProgram.append([inst, cl, Z80[instruction], value, "jump", lineCounter ])
						change=True
						jumps.append(instCounter)
						instCounter+=1
						cl+=int(len(Z80[instruction])/2+cltemp)
					else:


						finalProgram.append([inst, cl, Z80[instruction], value, lineCounter])
						change=True
						jumps.append(instCounter)
						instCounter+=1
						cl+=int(len(Z80[instruction])/2+cltemp)

	if change:

		return True
	else:
		return False

#___________________________________________________________________________________
#def makeJumps()
#Esta funcion es llamada cuando se han encontrado saltos en la funcion toOpCode()
#ya despues de haber leido y traducido cada linea

#Regresa dos tipos de errores 

#etiqueta; este es retornado cuando no se ha encontrado una defincion de la etiqueta
#Salto relativo; este es retornado cuando el salto relativo supera el rango en que
#se puede saltar

#Si no se encuentra un error, el codigo objeto de la instruccion es actualizada con 
#el valor del salto

#La manera en que se sabe que saltos hay, es a travez de un diccionario que es 
#actualizado cuando se estan leyendo las instrucciones, este contiene la direccion
#de la instruccion que necesita ser actualizada.
#___________________________________________________________________________________				


def makeJumps():

	for i in jumps:
		if "jump" in finalProgram[i]:#saltos relativos
			#NEW
			#END
			try:
				new=jumpDefinition[finalProgram[i][3]+":"]
			except KeyError:
				return ("etiqueta", finalProgram[i][5])
			old=finalProgram[i+1][1]
			new=new-old
			#NEW
			if -126<= new <=129:

				finalProgram[i][2]+=tohex(new,8)
				del(finalProgram[i][3])
				del(finalProgram[i][3])

				continue

			else:

				return ("Salto relativo",finalProgram[i][5])


		else:#saltos absolutos

			try:
			
				finalProgram[i][2]+=tohex(jumpDefinition[finalProgram[i][3]+":"],16, True)

			except KeyError:
				return ("etiqueta", finalProgram[i][4] )

			del(finalProgram[i][3])

			continue

def lstFile(finalProgram, name):

	global jumpDefinition

	for i in range(len(finalProgram)):
		finalProgram[i][1]=tohex(finalProgram[i][1],16)

	with open(name, 'w', encoding="utf8") as f:
		f.write(tabulate(finalProgram, headers=("instruccion", "CL", "OpCode")))
		for i,j in jumpDefinition.items():

			f.write(f"\n{i} {str(j)}")


def hexFile(HEXF, name):
	with open(name, 'w', encoding="utf8") as f:
		for line in HEXF:
			f.write(f"{line}\n")




#a=assembler("f.ASM")

def checksum(data):
	data= [int(data[i:i+2], 16) for i in range(0, len(data), 2)]
	result=256-sum(data)
	return tohex(result,8)


def record(finalProgram):
	sizeCounter=0
	f=[]
	sixteenbytes=""
	ByteCount=0
	Address=0
	RecordType="00"

	for i in range(len(finalProgram)):

		for char in finalProgram[i][2]:
			sixteenbytes+=char
			sizeCounter+=1
				
			if sizeCounter==32:
				
				ByteCount="10"
				sixteenbytes=ByteCount+tohex(Address,16)+RecordType+sixteenbytes
				sixteenbytes+=checksum(sixteenbytes)
				f.append(":"+sixteenbytes)
				sixteenbytes=""
				Address+=16
				sizeCounter=0

	if sixteenbytes:
		ByteCount=int(len(sixteenbytes)/2)
		sixteenbytes=tohex(ByteCount,8)+tohex(Address,16)+RecordType+sixteenbytes
		sixteenbytes+=checksum(sixteenbytes)
		f.append(":"+sixteenbytes)
		f.append(":00000001FF")
	return f	

#assembler("f.ASM")
#f=record(finalProgram)
#print(tabulate(f))

def main(fileASM):
	global cl
	global jumpDefinition
	global finalProgram
	global jumps
	global instCounter
	global lineCounter
	cl=0
	jumpDefinition={}
	finalProgram=[]
	jumps=[]
	instCounter=0
	lineCounter=0
	#finalProgram=[]
	#fileASM=input("ingrese el nombre del archivo: \n")
	ens=assembler(fileASM)
	if ens=="file":
		return "file"

	if ens:#hay error y retorna el tipo
		#print(ens)
		return ens
	else:
		lstFile(finalProgram, fileASM.split(".")[0]+".LST")
		HEXF=record(finalProgram)
		hexFile(HEXF,fileASM.split(".")[0]+".HEX")
		#return "Ensamblado correcto"
		return "correcto"

if __name__=="__main__":

	print(main("copiar.ASM"))





#f=record(finalProgram)
#print(tabulate(f))

#hexFile(f,"prueba.HEX")
#lstFile(finalProgram,"prueba.LST")


#print("__________________________________________")


# def bytesSume(finalProgram):
# 	sizeCounter=0
# 	f=[]
# 	sixteenbytes=""
# 	byte=""
# 	ck=0
# 	for i in range(len(finalProgram)):

# 		for char in finalProgram[i][2]:
# 			sixteenbytes+=char
# 			byte+=char
# 			sizeCounter+=1
# 			if len(byte)==2:

# 				ck+=int(byte, 16)
# 				byte=""
				
# 			if sizeCounter==32:
# 				ck+=len(f)*16+16
# 				f.append([sixteenbytes, ck])
# 				sixteenbytes=""
# 				ck=0
# 				sizeCounter=0

		
# 	f.append([sixteenbytes, ck+(len(sixteenbytes))+ len(f)*16])
# 	return f	



# def main():
# 	global finalProgram
# 	fileASM=input("ingrese el nombre del archivo: \n")
# 	ens=assembler(fileASM)
# 	if ens:
# 		print("Error", ens)

# 	if ens==False:
# 		exit=input()
# 		return False
# 	else:
# 		lstFile(finalProgram, fileASM.split(".")[0]+".LST")
# 		print("Ensamblado correcto")

# 	exit=input()

# #
# main()