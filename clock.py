import time
import RPi.GPIO as GPIO
import multiprocessing
from shifter import Shifter # shifter class
from temp_sensor import DHT # temp sensor class

class Clock():

  'Class for controlling the clock'

  # Different patterns for different numbers needed
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
    0b11111111, # blank
    0b10001110] # F

  def __init__(self, data, latch, clock, digitPins, switchPin, DHTPin):
    
    self.shifter = Shifter(data, latch, clock)

    # Pin setup:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(digitPins[0], GPIO.OUT) 
    GPIO.setup(digitPins[1], GPIO.OUT) 
    GPIO.setup(digitPins[2], GPIO.OUT) 
    GPIO.setup(digitPins[3], GPIO.OUT)
    GPIO.setup(switchPin, GPIO.IN)

    # Creating variables that can be used within the whole class
    self.digitPins = digitPins
    self.switchPin = switchPin

    self.currentMinute = '' # create current minute variable

    self.tempSensor = DHT(DHTPin) # create temp sensor obj

    self.tempRead = multiprocessing.Value('i') # create mp objects
    self.tempRead.value = 60 # initialize a value

    self.p = multiprocessing.Process(target=self.run,args=()) # create mp object
    self.p.daemon = True # daemon object
    self.p.start() # start mp

    self.t = multiprocessing.Process(target=self.readTemp,args=()) # create mp object
    self.t.daemon = True # daemon object
    self.t.start() # start mp

  def setNumber(self, num):  # display a given number
    self.shifter.shiftByte(Clock.numbers[num])

  def getTime(self):
    minute = time.localtime().tm_min # get current minute
    if minute < 10: minute = '0' + str(minute) # add a zero for single digit
    # Because the time comes up wrong:
    hour = time.localtime().tm_hour - 5
    if hour < 1: hour = hour + 24
    # Display non-military time:
    if hour > 12: hour = hour - 12
    # Making the time into a list of numbers:
    self.timeNow = str(hour) + str(minute)
    self.timeNow = list(self.timeNow)
    # Adding blank space if only three digits:
    if len(self.timeNow) == 3:
      self.timeNow.insert(0,10) # ten is a blank space
    return(self.timeNow)

  # Function for running the clock display:
  def runClock(self, timeNow):
    if str(time.localtime().tm_min) != self.currentMinute: # if the minute has changed
      self.timeNow = self.getTime() # the timeNow from gettime
      self.currentMinute = str(time.localtime().tm_min) # change the current minute value for comparing
    for d in range(4): # change each digit one at a time
      GPIO.output(self.digitPins[d],1)
      self.setNumber(int(self.timeNow[d]))
      time.sleep(0.005)
      GPIO.output(self.digitPins[d],0)

  # Function for running the temperature display:
  def runTemp(self):
    temp = str(self.tempRead.value) # get temp from readTemp which is continually running
    temp = list(temp) # turn into a list of numbers
    for d in range(4): # change each digit one at a time
      GPIO.output(self.digitPins[d],1)
      if d == 0: self.setNumber(10)
      elif d == 3: self.setNumber(11)
      else: self.setNumber(int(temp[d-1]))
      time.sleep(0.005)
      GPIO.output(self.digitPins[d],0) 

  # Function that runs the whole display (starts when clock object is created)
  def run(self):
    self.timeNow = self.getTime() # get the time
    while True:
      switch = GPIO.input(self.switchPin) # read switch value
      if switch == True:
        self.runClock(self.timeNow) # clock display
      elif switch == False:
        self.runTemp() # temperature display

  def readTemp(self):
    while True:
      self.tempSensor.readDHT11() # read temperature
      if self.tempSensor.temperature > 0: # handling random large negative values
        celsius = int(self.tempSensor.temperature)
        fahr = int(float(celsius)*(1.8) + 32) # convert to fahrenheit
        self.tempRead.value = fahr
      time.sleep(2) # only do this every two seconds or so
