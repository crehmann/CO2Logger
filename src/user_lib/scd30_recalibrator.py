import machine
from scd30 import SCD30
from utime import ticks_ms, sleep


CO2PPM_CALIBRATION_VALUE            = 400
CALIBRATION_DURATION_MS             = 120 * 1000
CALIBRATION_MEASUREMENT_INTERVAL_S  = 2
  
class SCD30Recalibrator:

  def __init__(self, scd30, co2_interval_s, buzzer=None):
    self._scd30 = scd30
    self._co2_interval_s = co2_interval_s
    self._buzzer = buzzer
    self._recalibrationTimestamp = None
    
  def recalibrate(self):
    print("starting recalibration")
    self._buzzer.buzz(1, 0.1)
    sleep(5)
    self._recalibrationTimestamp = ticks_ms()
    self._scd30.set_measurement_interval(CALIBRATION_MEASUREMENT_INTERVAL_S)
    
  def update(self):
    if self._recalibrationTimestamp \
    and ticks_ms() - self._recalibrationTimestamp > CALIBRATION_DURATION_MS:
      self._recalibrationTimestamp = None
      sleep(5)
      self._scd30.set_forced_recalibration(CO2PPM_CALIBRATION_VALUE)
      self._scd30.set_measurement_interval(self._co2_interval_s)
      self._buzzer.buzz(2, 0.1)
      print("recalibration finisehd")

