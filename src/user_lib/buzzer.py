from utime import sleep
from machine import Pin

class Buzzer:
  def __init__(self, pin):
    self._pin = Pin(pin, Pin.OUT)

  def buzz(self, times, interval):
    for i in range(times):
      self._pin.value(1)
      sleep(interval)
      self._pin.value(0)
      sleep(interval)
