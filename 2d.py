import math
from tkinter import *
import copy
import keyboard

class Camera2D:
	
	def __init__(self, L, R, B, T):
		self.L = L
		self.R = R
		self.B = B
		self.T = T
		self.W = 1024
		self.H = 1024
		self.posX = 0
		self.posY = 0
		
	def WorldToScreen(self, X, Y):
		ScreenX = int((X - self.L) * self.W / (self.R - self.L))
		ScreenY = int((self.T - Y) * self.H / (self.T - self.B))
		return [ScreenX, ScreenY]

	def ScreenToWorld(self, X, Y):
		WorldX = self.L + (self.R - self.L) * (self.X + 0.5) / self.W
		WorldY = self.T - (self.T - self.B) * (Y + 0.5) / self.H
		return [WorldX, WorldY]
	
	def MoveTo(self, X, Y):
		self.posX = X
		self.posY = Y
		
	def Axes(self, graph, step):
		graph.create_line(self.W/2,self.H,self.W/2,0,width=2,arrow=LAST)
		graph.create_line(0,self.H/2,self.W,self.H/2,width=2,arrow=LAST)

		graph.create_line(self.WorldToScreen(0, 0)[0], -3 + self.WorldToScreen(0, 0)[1], self.WorldToScreen(0, 0)[0], 3 + self.WorldToScreen(0, 0)[1], width = 0.5, fill = 'black')
		graph.create_text(self.WorldToScreen(0, 0)[0] + 15, -10 + self.WorldToScreen(0, 0)[1], text = str(0), fill="purple", font=("Helvectica", "10"))

		for i in range(step, self.R, step):
			graph.create_line(self.WorldToScreen(i, 0)[0], -3 + self.WorldToScreen(i, 0)[1], self.WorldToScreen(i, 0)[0], 3 + self.WorldToScreen(i, 0)[1], width = 1.5, fill = 'black')
			graph.create_text(self.WorldToScreen(i, 0)[0] + 15, -10 + self.WorldToScreen(i, 0)[1], text = str(i), fill="purple", font=("Helvectica", "10"))
	
		for i in range(step, self.T, step):
			graph.create_line(-3 + self.WorldToScreen(0, i)[0], self.WorldToScreen(0, i)[1], 3 + self.WorldToScreen(0, i)[0], self.WorldToScreen(0, i)[1], width = 1.5, fill = 'black')
			graph.create_text(self.WorldToScreen(0, i)[0] + 15, -10 + self.WorldToScreen(0, i)[1], text = str(i), fill="purple", font=("Helvectica", "10"))

		for i in range(-step, self.B, -step):
			graph.create_line(-3 + self.WorldToScreen(0, i)[0], self.WorldToScreen(0, i)[1], 3 + self.WorldToScreen(0, i)[0], self.WorldToScreen(0, i)[1], width = 1.5, fill = 'black')
			graph.create_text(self.WorldToScreen(0, i)[0] + 15, -10 + self.WorldToScreen(0, i)[1], text = str(i), fill="purple", font=("Helvectica", "10"))
	
		for i in range(-step, self.L, -step):
			graph.create_line(self.WorldToScreen(i, 0)[0], -3 + self.WorldToScreen(i, 0)[1], self.WorldToScreen(i, 0)[0], 3 + self.WorldToScreen(i, 0)[1], width = 1.5, fill = 'black')
			graph.create_text(self.WorldToScreen(i, 0)[0] + 15, -10 + self.WorldToScreen(i, 0)[1], text = str(i), fill="purple", font=("Helvectica", "10"))
		
	def LineTo(self, graph, X0, Y0, X1, Y1):
		self.MoveTo(X0, Y0)
		graph.create_line(self.WorldToScreen(self.posX, self.posY)[0], self.WorldToScreen(self.posX, self.posY)[1], self.WorldToScreen(X1, Y1)[0], self.WorldToScreen(X1, Y1)[1], width = 2, fill = 'black')
		self.MoveTo(X1, Y1)
		
class Model2D:
	
	def __init__(self, vertexMatrix, k2Matrix):
		self.vertexMatrix = vertexMatrix
		self.k2Matrix = k2Matrix
		self.vertexMatrixAT = [[1, 0, 0],
								[0, 1, 0],
								[0, 0, 1]]
		
	def initVertexMatrixAT(self):
		self.vertexMatrixAT = [[1, 0, 0],
								[0, 1, 0],
								[0, 0, 1]]
		
	def ModelDrawer(self, camera, matrix):
		for i in range(len(self.k2Matrix)):
			camera.LineTo(graph, matrix[k2Matrix[i][0]-1][0]/matrix[k2Matrix[i][0]-1][2],matrix[k2Matrix[i][0]-1][1]/matrix[k2Matrix[i][0]-1][2],matrix[k2Matrix[i][1]-1][0]/matrix[k2Matrix[i][1]-1][2],matrix[k2Matrix[i][1]-1][1]/matrix[k2Matrix[i][1]-1][2])
		
	def ApplyAT(self, matrix, AT):
		res = [[0 for _ in range(3)] for _ in range(len(self.k2Matrix))]
		for i in range(len(self.k2Matrix)):
			for j in range(3):
				res[i][j] = matrix[i][0] * AT[j][0] + matrix[i][1] * AT[j][1] + matrix[i][2] * AT[j][2]
		self.vertexMatrixAT = copy.deepcopy(res)
	
	def matrixMultiplier(self, matrix):
		res = [[0 for _ in range(3)] for _ in range(3)]
		for i in range(3): 
			for j in range(3): 
				for k in range(3): 
					res[i][j] += matrix[i][k] * self.vertexMatrixAT[k][j]
		self.vertexMatrixAT = copy.deepcopy(res)

def parallelTransferToAVector(aX, aY):
	return [[1, 0, aX],
			[0, 1, aY],
			[0, 0, 1]]

def rotationByAngleFi(fi):
	return [[math.cos(fi), -math.sin(fi), 0],
			[math.sin(fi), math.cos(fi), 0],
			[0, 0, 1]]

def rotationByCosSin(cos, sin):
	return [[cos, -sin, 0],
			[sin, cos, 0],
			[0, 0, 1]]

def scalingAlongCoordinateAxes(kX, kY):
	return [[kX, 0, 0],
			[0, kY, 0],
			[0, 0, 1]]

def reflectionToAbscissaAxis():
	return [[1, 0, 0],
			[0, -1, 0],
			[0, 0, 1]]

def reflectionToOrdinateAxis():
	return [[-1, 0, 0],
			[0, 1, 0],
			[0, 0, 1]]

def reflectionToOrigin():
	return [[-1, 0, 0],
			[0, -1, 0],
			[0, 0, 1]]

camera = Camera2D(-10, 10, -10, 10)
window = Tk()
graph = Canvas(window, width = camera.W, height = camera.H, bg = "white")
step = 2
camera.Axes(graph, step)

print("Enter number of vertices: ", end="")
M = int(input())
vertexMatrix = [[0 for _ in range(3)] for _ in range(M)]
print("\nEnter matrix of vertices: ")
for i in range(M):
	vertexMatrix[i] = input().split()
	for j in range(3):
		vertexMatrix[i][j] = float(vertexMatrix[i][j])

k2Matrix = [[0 for _ in range(2)] for _ in range(M)]
print("\nEnter vertex adjacency matrix: ")
for i in range(M):
	k2Matrix[i] = input().split()
	for j in range(2):
		k2Matrix[i][j] = int(k2Matrix[i][j])
triangle = Model2D(vertexMatrix, k2Matrix)
triangle.initVertexMatrixAT()
triangle.ModelDrawer(camera, triangle.vertexMatrix)

graph.pack()
window.update()

programState = 'yes'
while programState == 'yes':
	window.update()
	command = 'affine'
	while command == 'affine':
		print("\nParallel transfer - move\nRotation by an angle - rotate\nScaling along coordinate axes - scale\nReflection to abscissa axis - refleAbs\nReflection to ordinate axis - refleOrd\nReflection to origin - refleOrigin\nWhich affine transformation do you want to use? ", end="")
		commandAT = input()
		match commandAT.split():
			case ["move"]:
				print("\nEnter vector coordinates to be moved to: ")
				aX, aY = input().split()
				aX = float(aX)
				aY = float(aY)
				ATMatrix = parallelTransferToAVector(aX, aY)
				triangle.matrixMultiplier(ATMatrix)
			case ["rotate"]:
				print("\nEnter rotation angle (counterclockwise): ")
				fi = input()
				fi = float(fi)
				ATMatrix = rotationByAngleFi(math.radians(fi))
				triangle.matrixMultiplier(ATMatrix)
			case ["scale"]:
				print("\nEnter scaling coefficients: ")
				kX, kY = input().split()
				kX = float(kX)
				kY = float(kY)
				ATMatrix = scalingAlongCoordinateAxes(kX, kY)
				triangle.matrixMultiplier(ATMatrix)
			case ["refleAbs"]:
				ATMatrix = reflectionToAbscissaAxis()
				triangle.matrixMultiplier(ATMatrix)
			case ["refleOrd"]:
				ATMatrix = reflectionToOrdinateAxis()
				triangle.matrixMultiplier(ATMatrix)
			case ["refleOrigin"]:
				ATMatrix = reflectionToOrigin()
				triangle.matrixMultiplier(ATMatrix)
			case ["sostav"]:
				ang=int(input())
				mx,my=triangle.vertexMatrix[1][0]/triangle.vertexMatrix[1][2],triangle.vertexMatrix[1][1]/triangle.vertexMatrix[1][2]			
				triangle.matrixMultiplier(parallelTransferToAVector(-mx, -my))
				triangle.matrixMultiplier(rotationByAngleFi(math.radians(5+ang)))
				triangle.matrixMultiplier(parallelTransferToAVector(mx, my))
			case _: print("\nWrong command.")
		
		#print(triangle.vertexMatrixAT)
		print("\nDraw current matrix - draw, apply another affine transformation - affine: ", end="")
		command = input()
	if command == 'draw':
		triangle.ApplyAT(triangle.vertexMatrix, triangle.vertexMatrixAT)
		triangle.ModelDrawer(camera, triangle.vertexMatrixAT)
		triangle.initVertexMatrixAT()
		graph.pack()
		window.update()
	else:
		print("\nWrong command.")
	print("\nContinue or quit? ", end="")
	programState = input()

window.mainloop()