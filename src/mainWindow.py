from tkinter import *
from tkinter import  messagebox
import nuevoEnsamblador as ens

class assamblerGUI:
	def __init__(self, master):
		self.master=master
		frame1=Frame(root, bg="white")
		frame2=Frame(root, bg="white")
		frame1.pack(side=TOP)
		frame2.pack()
		self.var=IntVar()
		self.var.set(0)
		self.solicitud=Label(frame1,text="Ingrese el nombre del archivo a ensamblar", bg="white", font=("Arial Black", 12))
		self.archivo=Entry(frame1, width=30, bd=1, relief=GROOVE, borderwidth=5)
		self.enter=Button(frame1,text="Enter", command=self.enterButton)
		self.archivo.focus()
		self.archivo.bind('<Return>', self.focusOnButton)
		self.status=Label(frame2, bg="white", width=30, justify=CENTER, fg="red")
		self.HEX=Radiobutton(frame2, text="HEX File", variable=self.var, value=1, bg="white", command=self.openFile)
		self.LST=Radiobutton(frame2, text="LST File", variable=self.var, value=2, bg="white", command=self.openFile)
		self.HEX.config(state=DISABLED)
		self.LST.config(state=DISABLED)
		self.pantalla=Text(frame2, bg="white")



		self.solicitud.pack(side=TOP)
		self.archivo.pack(side=LEFT)
		self.enter.pack(side=LEFT)
		self.status.pack(side=TOP)
		self.HEX.pack()
		self.LST.pack()
		self.pantalla.pack(side=BOTTOM)
		self.openFile

	def focusOnButton(self, event=None):
		self.master.focus()
		self.enterButton()

	def openFile(self):
		self.pantalla.delete('1.0',END)
		if self.var.get()==1:
			with open(self.archivo.get().split(".")[0] +".HEX",mode='r') as f:
				for line in f:
					self.pantalla.insert(INSERT, line)			


		if self.var.get()==2:

			with open(self.archivo.get().split(".")[0] +".LST",mode='r') as f:
				for line in f:
					self.pantalla.insert(INSERT, line)


	def ensamblaje(self,archivo):
		statusKind=None
		statusKind=ens.main(archivo)

		if statusKind=="file":
			reintentar=messagebox.askretrycancel(title="Error", message="Archivo no encontrado")
			if reintentar:
				self.enter.config(state=ACTIVE)
				self.archivo.focus()
				return True
			else:

				self.master.destroy()
				
			return False


		if statusKind=="correcto":

			self.HEX.config(state=ACTIVE)
			self.LST.config(state=ACTIVE)
			#self.openFile()
			self.status.config(text="Ensamblado correcto")
			self.archivo.config(state=DISABLED)



			return True

		if statusKind:
			#print(statusKind)
			
			reintentar=messagebox.askretrycancel(title="Error", message=f"Error: {statusKind[0]}, linea:{statusKind[1]}")
			
			if reintentar:
				self.enter.config(state=ACTIVE)
				self.archivo.focus()
			else:
				self.master.destroy()



			#self.master.focus()

			#self.status.config(text=f"Error: {statusKind[0]}, linea:{statusKind[1]}")
			return False

	def enterButton(self):
		self.enter.config(state=DISABLED)
		file=self.archivo.get()
		opciones=None
		opciones=self.ensamblaje(file)


if __name__=="__main__":
	root = Tk()  
	root.wm_geometry("800x600")
	root.config(bg="white")

	assamblerGUI(root)

	root.mainloop()