import time
import RPi.GPIO as GPIO
import multiprocessing
from shifter import Shifter # shifter class
from temp_sensor import DHT # temp sensor class

class Clock():

  'Class for controlling the clock'
  numbers = [ 
    0b11000000, # 0
    0b11111001, # 1
    0b10100100, # 2
    0b10110000, # 3
    0b10011001, # 4
    0b10010010, # 5
    0b10000010, # 6
    0b11111000, # 7
    0b10000000, # 8
    0b10010000, # 9
    0b11111111,
    0b10001110] # blank


  def __init__(self, data, latch, clock, digitPins, switchPin, DHTPin):
    
    self.shifter = Shifter(data, latch, clock)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(digitPins[0], GPIO.OUT) 
    GPIO.setup(digitPins[1], GPIO.OUT) 
    GPIO.setup(digitPins[2], GPIO.OUT) 
    GPIO.setup(digitPins[3], GPIO.OUT)
    GPIO.setup(switchPin, GPIO.IN)

    self.digitPins = digitPins
    self.switchPin = switchPin

    self.currentMinute = ''

    self.tempSensor = DHT(DHTPin)

    self.tempRead = multiprocessing.Value('i')
    self.tempRead.value = 60

    self.p = multiprocessing.Process(target=self.run,args=()) # create mp object
    self.p.daemon = True # daemon object
    self.p.start() # start mp

    self.t = multiprocessing.Process(target=self.readTemp,args=()) # create mp object
    self.t.daemon = True # daemon object
    self.t.start() # start mp

  def setNumber(self, num):  # display a given number
    self.shifter.shiftByte(Clock.numbers[num])

  def getTime(self):
    minute = time.localtime().tm_min
    # Because the time comes up wrong:
    hour = time.localtime().tm_hour - 5
    if hour < 1: hour = hour + 24
    # Display non-military time:
    if hour > 12: hour = hour - 12
    # Making the time into a list of numbers:
    timeNow = str(hour) + str(minute)
    timeNow = list(timeNow)
    # Adding blank space if only three digits:
    if len(timeNow) == 3:
      timeNow.insert(0,10) # ten is a blank space
    return(timeNow)

  def runClock(self, timeNow):
    if str(time.localtime().tm_min) != self.currentMinute:
      timeNow = self.getTime()
      self.currentMinute = str(time.localtime().tm_min)
    for d in range(4):
      GPIO.output(self.digitPins[d],1)
      self.setNumber(int(timeNow[d]))
      time.sleep(0.005)
      GPIO.output(self.digitPins[d],0)

  def runTemp(self):
    temp = str(self.tempRead.value)
    temp = list(temp)
    for d in range(4):
      GPIO.output(self.digitPins[d],1)
      if d == 0: self.setNumber(10)
      elif d == 3: self.setNumber(11)
      else: self.setNumber(int(temp[d-1]))
      time.sleep(0.005)
      GPIO.output(self.digitPins[d],0) 

  def run(self):
    timeNow = self.getTime()
    while True:
      switch = GPIO.input(self.switchPin)
      if switch == True:
        self.runClock(timeNow)
      elif switch == False:
        self.runTemp()

  def readTemp(self):
    while True:
      self.tempSensor.readDHT11()
      if self.tempSensor.temperature > 0:
        celsius = int(self.tempSensor.temperature)
        fahr = int(float(celsius)*(1.8) + 32)
        self.tempRead.value = fahr
      time.sleep(2)
