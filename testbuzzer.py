import time
from gpiozero import Buzzer

buzzer = Buzzer(21)


while True:

  buzzer.on()
  time.sleep(5)
  buzzer.off(5)
  time.sleep(5)