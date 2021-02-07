from machine import Pin
from utime import ticks_ms

class PushButton(object):
    def __init__(self, pinNr, activeLow):

      self._pin = Pin(pinNr, Pin.IN, Pin.PULL_UP if activeLow else Pin.PULL_DOWN) 
      self._buttonReleasedState = 1 if activeLow else 0
      self._buttonPressedState = 0 if activeLow else 1
      self._longPressThreshold = 3000
      
      self._state = self._buttonReleasedState
      self._startTime = None
      self._eventHandled = False
      self._onClickCallback = None
      self._onLongPressCallback = None
    
    def onClick(self, callback):
      self._onClickCallback = callback

    def onLongPress(self, callback):

      self._onLongPressCallback = callback

    def update(self):
      # Button press detection
      if self.__hasButtonStateChanged() and self.__isButtonPressed():
        self._startTime = ticks_ms()

      # Button long-press detection
      if self.__isButtonPressed() \
      and not self.__hasButtonStateChanged() \
      and ticks_ms() - self._startTime> self._longPressThreshold \
      and self._onLongPressCallback \
      and not self._eventHandled:
        self._eventHandled = True
        self._onLongPressCallback()

      # Button clicked detection
      if self.__hasButtonStateChanged() \
      and not self.__isButtonPressed() \
      and self._onClickCallback \
      and not self._eventHandled:
        self._eventHandled = True
        self._onClickCallback()
      
      # Reset event handled flag
      if self.__hasButtonStateChanged() \
      and not self.__isButtonPressed():
        self._eventHandled = False
      
      self._state = self._pin.value()

    def __hasButtonStateChanged(self):
      return self._state != self._pin.value()
      
    def __isButtonPressed(self):
      return self._pin.value() == self._buttonPressedState

