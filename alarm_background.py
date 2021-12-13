#!/usr/bin/python3

# Importing libraries:
import RPi.GPIO as GPIO
import time
import json 
from clock import Clock # the class that runs the clock display
from led8x8 import led8x8 # the class that runs the LED matrix display

# Pin Setup
dataPin, latchPin, clockPin = 17, 27, 22 # for the clock display registers
digitPins = [6, 5, 13, 19] # pins that activate digits on clock
motionPin = 4 # motion sensor data Pin
buzzerPin = 21 # buzzer output pin
switchPin = 18 # switch input pin
DHTPin = 23 # temperature sensor data input pin
pwmPin = 16 # for cannon
motorPin = 12 # for cannon
data, latch, clock = 24, 25, 26 # for the LED matrix display shift register
shotCheck = True # has not shot pong ball yet
# Setting pins as inputs/outputs
GPIO.setmode(GPIO.BCM)
GPIO.setup(motionPin, GPIO.IN)
GPIO.setup(buzzerPin, GPIO.OUT)
GPIO.setup(pwmPin, GPIO.OUT)
GPIO.setup(motorPin, GPIO.OUT)
GPIO.setup(data, GPIO.OUT)
GPIO.setup(latch, GPIO.OUT)
GPIO.setup(clock, GPIO.OUT)
# PWM setup for cannon:
pwm = GPIO.PWM(pwmPin, 50)
pwm.start(0)

# Create clock object and begin clock:
ourClock = Clock(dataPin, latchPin, clockPin, digitPins, switchPin, DHTPin)
# Create LED matrix object:
matrix = led8x8(data,latch,clock)

# Different patterns for LED matrix:
blankPattern = [0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000]
smilePattern = [0b00000000, 0b00100100, 0b00100100, 0b00000000, 0b01000010, 0b00100100, 0b00011000, 0b00000000]
sillyPattern = [0b00000000, 0b00100100, 0b00100100, 0b00000000, 0b01000010, 0b00111100, 0b00110000, 0b00000000]
heartPattern = [0b01100110, 0b10011001, 0b10000001, 0b10000001, 0b01000010, 0b01000010, 0b00100100, 0b00011000]
matrix.updatePattern(blankPattern) # start on blank until message is chosen

# Other initialized values:
chosen_alarm = '' # initialize with no alarm chosen
GPIO.output(buzzerPin,0) # make sure buzzer for alarm is OFF
alarmGoneOff = False
minute = time.localtime().tm_min

# Function for shooting cannon:
def cannon(pwm,motorPin):
  pwm.ChangeDutyCycle(2)
  GPIO.output(motorPin,1)
  time.sleep(5)
  pwm.ChangeDutyCycle(6)
  time.sleep(.5)
  GPIO.output(motorPin,0)
  pwm.ChangeDutyCycle(2)
  time.sleep(.5)


try:
  while True:
    with open("alarm.txt", 'r') as f:
      parents_options = json.load(f) # retrieving json data from txt
    chosen_message = str(parents_options['message']) # the message that the parents chose

    if str(parents_options['alarm']) != chosen_alarm and parents_options['alarm'] != 'null': # if the chosen alarm is different than what it was before
      chosen_alarm = str(parents_options['alarm']) # then change it - this will be a string i believe 0345 yanno
      alarmGoneOff = False
      
    if chosen_message == 'smile':
      matrix.updatePattern(smilePattern)
    elif chosen_message == 'silly':
      matrix.updatePattern(sillyPattern)
    elif chosen_message == 'heart':
      matrix.updatePattern(heartPattern)

    if int(minute) != time.localtime().tm_min: alarmGoneOff = False

    # Get the time:
    minute = time.localtime().tm_min
    if minute < 10: minute = '0' + str(minute)
    # Formatting time:
    hour = time.localtime().tm_hour - 5
    print(hour)
    if hour < 1: hour = hour + 24
    print(hour)
    if hour > 12: hour = hour - 12
    # Making the time into a list of numbers:
    currentTime = str(hour) + ':' + str(minute)
    checkTime = str(time.localtime().tm_hour - 5)+':'+str(minute) # this is the current time

    print(GPIO.input(motionPin))
    print(chosen_alarm)
    print(checkTime)
    print(alarmGoneOff)

    if chosen_alarm == checkTime and alarmGoneOff == False: # if the current time = alarm time, and the alarm hasn't gone off within this minute yet
      alarmGoneOff = True
      GPIO.output(buzzerPin,1); time.sleep(2) # turn on buzzer for 4 seconds      
      if shotCheck:
        cannon(pwm,motorPin) # fire cannon
        shotCheck = False # has shot pong ball
      while GPIO.input(motionPin) == False: # while the motion sensor senses no motion
        print(GPIO.input(motionPin))
        # Alarm beeps:
        GPIO.output(buzzerPin,1); time.sleep(.5)
        GPIO.output(buzzerPin,0); time.sleep(.5)
      GPIO.output(buzzerPin,0) # turn off alarm when motion is sensed
    
    time.sleep(1) # only run this loop every second or so

# Exception handling:
except KeyboardInterrupt: 
  print('\nExiting')
except Exception as e: # catch all other errors
  print(e)               # delete once code is debugged
  ourClock.p.terminate()      # terminate the process
  ourClock.p.join(2)          # wait up to 2 sec for process termination before ending code

GPIO.cleanup()