import math
from tkinter import *
import copy
import keyboard

def vectLen(V):
	return math.sqrt(V[0]*V[0]+V[1]*V[1]+V[2]*V[2])

def vectMultiplty(a, b):
	return [a[1]*b[2]-b[1]*a[2],b[0]*a[2]-a[0]*b[2],a[0]*b[1]-b[0]*a[1]]

F = 1
D = 10
Ov = [0, 0, 0]
N = [1, 1, 2]
T = [0, 1, 0]

class Camera3D:
	
	def __init__(self, L, R, B, T):
		self.L = L
		self.R = R
		self.B = B
		self.T = T
		self.W = 720
		self.H = 720
		
	def WorldToView(self, WordV):
		lenV = vectLen(N)
		Kv = [N[0]/lenV, N[1]/lenV, N[2]/lenV]
		TxN = vectMultiplty(T, N)
		lenV = vectLen(TxN)
		Iv = [TxN[0]/lenV, TxN[1]/lenV, TxN[2]/lenV]
		Jv = vectMultiplty(Kv, Iv)
		Swv = [[Iv[0], Iv[1], Iv[2], - (Iv[0]*Ov[0] + Iv[1]*Ov[1] + Iv[2]*Ov[2])],
				[Jv[0], Jv[1], Jv[2], - (Jv[0]*Ov[0] + Jv[1]*Ov[1] + Jv[2]*Ov[2])],
				[Kv[0], Kv[1], Kv[2], - (Kv[0]*Ov[0] + Kv[1]*Ov[1] + Kv[2]*Ov[2])],
				[0, 0, 0, 1]]
		ViewV = [[0 for _ in range(1)] for _ in range(4)]
		for i in range(4):
			ViewV[i] = Swv[i][0]*WordV[0] + Swv[i][1]*WordV[1] + Swv[i][2]*WordV[2] + Swv[i][3]*WordV[3]
		return ViewV
	
	def ViewToPerspective(self, ViewV):
		Svp = [[1, 0, 0, 0],
				[0, 1, 0, 0],
				[0, 0, -1/F, 1]]
		PerV = [[0 for _ in range(1)] for _ in range(3)]
		for i in range(3):
			PerV[i] = Svp[i][0]*ViewV[0] + Svp[i][1]*ViewV[1] + Svp[i][2]*ViewV[2] + Svp[i][3]*ViewV[3]
		return PerV
	
	def PerspectiveToScreen(self, Perv):
		ScreenV = [[0 for _ in range(1)] for _ in range(2)]
		ScreenV[0] = int((Perv[0] - self.L) * self.W / (self.R - self.L))
		ScreenV[1] = int((self.T - Perv[1]) * self.H / (self.T - self.B))
		return ScreenV
	
	def ViewToNormalized(self, ViewV):
		Svn = [[2/(self.R - self.L), 0, (self.L + self.R)/(F*(self.R - self.L)), -(self.L + self.R)/(self.R - self.L)],
				[0, 2/(self.T - self.B), (self.T + self.B)/(F*(self.T - self.B)), -(self.T + self.B)/(self.T - self.B)],
				[0, 0, -(2*F + D)/(F*D), -1],
				[0, 0, -1/F, 1]]
		NormV = [[0 for _ in range(1)] for _ in range(4)]
		for i in range(4):
			NormV[i] = Svn[i][0]*ViewV[0] + Svn[i][1]*ViewV[1] + Svn[i][2]*ViewV[2] + Svn[i][3]*ViewV[3]
		return NormV
	
	def NormalizedToScreen(self, NormV):
		ScreenV = [[0 for _ in range(1)] for _ in range(2)]
		ScreenV[0] = int(((self.R - self.L)*NormV[0]/2 - self.L) * self.W/ (self.R - self.L))
		ScreenV[1] = int((self.T - (self.T - self.B)*NormV[1]/2) * self.H/ (self.T - self.B))
		return ScreenV
	
	def WorldToScreen(self, WordV):
		return self.NormalizedToScreen(self.ViewToNormalized(self.WorldToView(WordV)))
		
	def CoordinatePlaneCreator(self, graph, h):
		X0 = self.WorldToScreen([0, 0, 0, 1])[0]
		Y0 = self.WorldToScreen([0, 0, 0, 1])[1]
		graph.create_line(X0, Y0, X0, 0, width=2, arrow=LAST)
		graph.create_line(X0, self.WorldToScreen([0, self.B, 0, 1])[1], X0, Y0, width=2, dash=(10,1))
		graph.create_line(X0, Y0,  self.WorldToScreen([self.R, 0, 0, 1])[0], self.WorldToScreen([0, -N[2], 0, 1])[1], width=2, arrow=LAST)
		graph.create_line(0, self.WorldToScreen([0, N[2], 0, 1])[1], X0, Y0, width=2, dash=(10,1))
		graph.create_line(X0, Y0, 0, self.WorldToScreen([0, self.B + N[1], 0, 1])[1], width=2, arrow=LAST)
		graph.create_line(self.WorldToScreen([self.R + N[2], 0, 0, 1])[0], self.WorldToScreen([0, self.T, 0, 1])[1], X0, Y0, width=2, dash=(10,1))
		
	def LineTo(self, graph, X0, Y0, Z0, U0, X1, Y1, Z1, U1):
		graph.create_line(self.WorldToScreen([X0, Y0, Z0, U0])[0], self.WorldToScreen([X0, Y0, Z0, U0])[1], self.WorldToScreen([X1, Y1, Z1, U1])[0], self.WorldToScreen([X1, Y1, Z1, U1])[1], width = 2, fill = 'black')
		
class Model3D:
	
	def __init__(self, vertexMatrix, k2Matrix):
		self.vertexMatrix = vertexMatrix
		self.k2Matrix = k2Matrix
		self.vertexMatrixAT = [[1, 0, 0, 0],
								[0, 1, 0, 0],
								[0, 0, 1, 0],
								[0, 0, 0, 1]]
		
	def initVertexMatrixAT(self):
		self.vertexMatrixAT = [[1, 0, 0, 0],
								[0, 1, 0, 0],
								[0, 0, 1, 0],
								[0, 0, 0, 1]]
		
	def ModelDrawer(self, camera, matrix):
		for i in range(len(self.k2Matrix)):
			camera.LineTo(graph, matrix[k2Matrix[i][0]-1][0],matrix[k2Matrix[i][0]-1][1],matrix[k2Matrix[i][0]-1][2],matrix[k2Matrix[i][0]-1][3],matrix[k2Matrix[i][1]-1][0],matrix[k2Matrix[i][1]-1][1],matrix[k2Matrix[i][1]-1][2],matrix[k2Matrix[i][1]-1][3])
		
	def ApplyAT(self, matrix, AT):
		res = [[0 for _ in range(4)] for _ in range(len(self.vertexMatrix))]
		for i in range(len(self.vertexMatrix)):
			for j in range(4):
				res[i][j] = matrix[i][0] * AT[j][0] + matrix[i][1] * AT[j][1] + matrix[i][2] * AT[j][2] + matrix[i][3] * AT[j][3]
		return res
	
	def matrixMultiplier(self, matrix):
		res = [[0 for _ in range(4)] for _ in range(4)]
		for i in range(4): 
			for j in range(4): 
				for k in range(4): 
					res[i][j] += matrix[i][k] * self.vertexMatrixAT[k][j]
		self.vertexMatrixAT = copy.deepcopy(res)

def parallelTransferToAVector(aX, aY, aZ):
	return [[1, 0, 0, aX],
			[0, 1, 0, aY],
			[0, 0, 1, aZ],
			[0, 0, 0, 1]]

def rotationByAngleFiAroundX(fi):
	fi = math.radians(fi)
	return [[1, 0, 0, 0],
			[0, math.cos(fi), -math.sin(fi), 0],
			[0, math.sin(fi), math.cos(fi), 0],
			[0, 0, 0, 1]]

def rotationByAngleFiAroundY(fi):
	fi = math.radians(fi)
	return [[math.cos(fi), 0, math.sin(fi), 0],
			[0, 1, 0, 0],
			[-math.sin(fi), 0, math.cos(fi), 0],
			[0, 0, 0, 1]]

def rotationByAngleFiAroundZ(fi):
	fi = math.radians(fi)
	return [[math.cos(fi), -math.sin(fi), 0, 0],
			[math.sin(fi), math.cos(fi), 0, 0],
			[0, 0, 1, 0],
			[0, 0, 0, 1]]

def scalingAlongCoordinateAxes(kX, kY, kZ):
	return [[kX, 0, 0, 0],
			[0, kY, 0, 0],
			[0, 0, kZ, 0],
			[0, 0, 0, 1]]

def reflectionToYZ():
	return [[-1, 0, 0, 0],
			[0, 1, 0, 0],
			[0, 0, 1, 0],
			[0, 0, 0, 1]]

def reflectionToZX():
	return [[1, 0, 0, 0],
			[0, -1, 0, 0],
			[0, 0, 1, 0],
			[0, 0, 0, 1]]

def reflectionToXY():
	return [[1, 0, 0, 0],
			[0, 1, 0, 0],
			[0, 0, -1, 0],
			[0, 0, 0, 1]]

def reflectionToAbscissaAxis():
	return [[1, 0, 0, 0],
			[0, -1, 0, 0],
			[0, 0, -1, 0],
			[0, 0, 0, 1]]

def reflectionToOrdinateAxis():
	return [[-1, 0, 0, 0],
			[0, 1, 0, 0],
			[0, 0, -1, 0],
			[0, 0, 0, 1]]

def reflectionToApplicationAxis():
	return [[-1, 0, 0, 0],
			[0, -1, 0, 0],
			[0, 0, 1, 0],
			[0, 0, 0, 1]]

def reflectionToOrigin():
	return [[-1, 0, 0, 0],
			[0, -1, 0, 0],
			[0, 0, -1, 0],
			[0, 0, 0, 1]]

camera = Camera3D(-10, 10, -10, 10)
window = Tk()
graph = Canvas(window, width = camera.W, height = camera.H, bg = "white")
camera.CoordinatePlaneCreator(graph, 2)

vertexMatrix = [[0, 0, 3, 1],
				[0, 0, 0, 1],
				[3, 0, 0, 1],
				[3, 0, 3, 1],
				[0, 3, 3, 1]]
k2Matrix=[[1, 2],
		  [1, 4],
		  [1, 5],
		  [2, 3],
		  [2, 5],
		  [3, 4],
		  [3, 5],
		  [4, 5],]
figure = Model3D(vertexMatrix, k2Matrix)
figure.initVertexMatrixAT()
figure.ModelDrawer(camera, figure.vertexMatrix)

def applyParallelTransfer(event = ' '):
	print("Enter vector coordinates to be moved to: ", end="")
	aX, aY, aZ = input().split()
	aX = float(aX)
	aY = float(aY)
	aZ = float(aZ)
	ATMatrix = parallelTransferToAVector(aX, aY, aZ)
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def applyRotationAroudX(event = ' '):
	print("Enter rotation angle (counterclockwise): ", end="")
	fi = input()
	fi = float(fi)
	ATMatrix = rotationByAngleFiAroundX(fi)
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def applyRotationAroudY(event = ' '):
	print("Enter rotation angle (counterclockwise): ", end="")
	fi = input()
	fi = float(fi)
	ATMatrix = rotationByAngleFiAroundY(fi)
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def applyRotationAroudZ(event = ' '):
	print("Enter rotation angle (counterclockwise): ", end="")
	fi = input()
	fi = float(fi)
	ATMatrix = rotationByAngleFiAroundZ(fi)
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def applyScaling(event = ' '):
	print("Enter scaling coefficients: ", end="")
	kX, kY, kZ = input().split()
	kX = float(kX)
	kY = float(kY)
	kZ = float(kZ)
	ATMatrix = scalingAlongCoordinateAxes(kX, kY, kZ)
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def applyReflectionToYZ(event = ' '):
	ATMatrix = reflectionToYZ()
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def applyReflectionToZX(event = ' '):
	ATMatrix = reflectionToZX()
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def applyReflectionToXY(event = ' '):
	ATMatrix = reflectionToXY()
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def applyReflectionToX(event = ' '):
	ATMatrix = reflectionToAbscissaAxis()
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def applyReflectionToY(event = ' '):
	ATMatrix = reflectionToOrdinateAxis()
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def applyReflectionToZ(event = ' '):
	ATMatrix = reflectionToApplicationAxis()
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def applyReflectionToOrigin(event = ' '):
	ATMatrix = reflectionToOrigin()
	figure.matrixMultiplier(ATMatrix)
	matrixWithAT = figure.ApplyAT(figure.vertexMatrix, figure.vertexMatrixAT)
	figure.ModelDrawer(camera, matrixWithAT)
	
def reset(event = ' '):
	figure.initVertexMatrixAT()
	graph.pack()
	window.update()
	
def clean(event = ' '):
	graph.delete('all')
	camera.CoordinatePlaneCreator(graph, 2)
	figure.ModelDrawer(camera, figure.vertexMatrix)
	
tk = Tk()
tk.title('Buttons')
tk.geometry('500x300')

button1 = Button(tk, text = 'Parallel Transfer', height = 2, width = 15, command = applyParallelTransfer)
button1.place(x=10, y=10)

button2 = Button(tk, text = 'Rotate Around X', height = 2, width = 15, command = applyRotationAroudX)
button2.place(x=130, y=10)

button3 = Button(tk, text = 'Rotate Around Y', height = 2, width = 15, command = applyRotationAroudY)
button3.place(x=250, y=10)

button4 = Button(tk, text = 'Rotate Around Z', height = 2, width = 15, command = applyRotationAroudZ)
button4.place(x=370, y=10)

button5 = Button(tk, text = 'Scale', height = 2, width = 15, command = applyScaling)
button5.place(x=10, y=60)

button6 = Button(tk, text = 'Reflect to YZ', height = 2, width = 15, command = applyReflectionToYZ)
button6.place(x=130, y=60)

button7 = Button(tk, text = 'Reflect to ZX', height = 2, width = 15, command = applyReflectionToZX)
button7.place(x=250, y=60)

button8 = Button(tk, text = 'Reflect to XY', height = 2, width = 15, command = applyReflectionToXY)
button8.place(x=370, y=60)

button9 = Button(tk, text = 'Reflect to X', height = 2, width = 15, command = applyReflectionToX)
button9.place(x=10, y=110)

button10 = Button(tk, text = 'Reflect to Y', height = 2, width = 15, command = applyReflectionToY)
button10.place(x=130, y=110)

button11 = Button(tk, text = 'Reflect to Z', height = 2, width = 15, command = applyReflectionToZ)
button11.place(x=250, y=110)

button12 = Button(tk, text = 'Reflect to Origin', height = 2, width = 15, command = applyReflectionToOrigin)
button12.place(x=370, y=110)

button = Button(tk, text = 'Reset', height = 2, width = 10, command = reset)
button.place(x=160, y=250)

button_ = Button(tk, text = 'Clean', height = 2, width = 10, command = clean)
button_.place(x=250, y=250)

graph.pack()
window.mainloop()