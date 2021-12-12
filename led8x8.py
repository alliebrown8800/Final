from shifter16 import Shifter16
import time
from multiprocessing import Process,Array

class led8x8():

	def __init__(self,data,latch,clock):
		self.shift = Shifter16(data,latch,clock)
		self.out = [0]*16
		self.patt = Array('i', [0b00111100, 0b01000010, 0b10100101, 0b10000001, 0b10100101, 0b10011001, 0b01000010, 0b00111100])
		self.p = Process(name = 'display',target = self.display,args = ())
		self.p.daemon = True
		self.p.start()

	# These two methods exists because I wired the light differently
	# and didnt want to rewire it
	def toCol(self,byte):
		i = 7
		self.out[4] = (byte & 1 << i) >> i
		i = i-1
		self.out[1] = (byte & 1 << i) >> i
		i = i-1
		self.out[6] = (byte & 1 << i) >> i
		i = i-1
		self.out[0] = (byte & 1 << i) >> i
		i = i-1
		self.out[12] = (byte & 1 << i) >> i
		i = i-1
		self.out[7] = (byte & 1 << i) >> i
		i = i-1
		self.out[10] = (byte & 1 << i) >> i
		i = i-1
		self.out[15] = (byte & 1 << i) >> i
		i = i-1
	def toRow(self,byte):
		i = 7
		self.out[11] = (byte & 1 << i) >> i
		i = i-1
		self.out[2] = (byte & 1 << i) >> i
		i = i-1
		self.out[3] = (byte & 1 << i) >> i
		i = i-1
		self.out[14] = (byte & 1 << i) >> i
		i = i-1
		self.out[5] = (byte & 1 << i) >> i
		i = i-1
		self.out[13] = (byte & 1 << i) >> i
		i = i-1
		self.out[9] = (byte & 1 << i) >> i
		i = i-1
		self.out[8] = (byte & 1 << i) >> i
		i = i-1
	

	def send(self,row,col):
		self.toRow(row) #maps the rows
		self.toCol(col) #maps the cols

		# Puts mapped outputs back to binary
		a = 0b00000000
		for j in range(8):
			a += self.out[-j-1]<<j

		b = 0b00000000
		for j in range(8,16):
			b += self.out[-j-1]<<j
		

		self.shift.shiftByte(a+b)
		# Ended up changing to 16 bit update
		# because I kept getting light artifacts
		# when I only pushed 8 at a time


	def display(self):
	
		while 1:
			mask = 0b11111111
			for i in range(8):
				row = mask & ~(1<<i)
				col = self.patt[7-i]
				self.send(row,col)
				time.sleep(.001)


	def updatePattern(self,pattern):
		for i in range(8):
			self.patt[i] = pattern[i]