
DISPLAY_STATE_CO2   = 0
DISPLAY_STATE_TEMP  = 1
DISPLAY_STATE_HUM   = 2
DISPLAY_STATE_OFF   = 3

class Display:
  def __init__(self, deviceDriver):
    self._deviceDriver = deviceDriver
    self._displayState  = DISPLAY_STATE_OFF
    self._measurements  = [0, 0, 0]
    
  def setMeasurements(self, measurements):
    self._measurements = measurements
    self.refreshDisplay()
    
  def toggleState(self):
    self._displayState = (self._displayState + 1) % 4
    self.refreshDisplay()
    
  def refreshDisplay(self):
    try:
      self._deviceDriver.fill(0)
      if self._displayState == DISPLAY_STATE_CO2:
        self._deviceDriver.text("CO2-ppm", 4, 0)
        self._deviceDriver.text("{:.0f}".format(self._measurements[0]), 12, 24)
      elif self._displayState == DISPLAY_STATE_TEMP:
        self._deviceDriver.text("Temp.", 12, 0)
        self._deviceDriver.text("{:.1f}".format(self._measurements[1]) + " C", 8, 24)
      elif self._displayState == DISPLAY_STATE_HUM:
        self._deviceDriver.text("Humidity", 0, 0)
        self._deviceDriver.text("{:.0f}".format(self._measurements[2]) + "%", 18, 24)
      self._deviceDriver.show()
    except Exception as ex:
      template = "An exception of type {0} occurred. Arguments:\n{1!r}"
      message = template.format(type(ex).__name__, ex.args)
      print(message)
      print("failed to refresh display")



