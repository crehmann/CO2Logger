import network
import machine 
import time 
from umqtt.simple import MQTTClient
from machine import I2C, Pin, SoftI2C
from scd30 import SCD30
from ssd1306 import SSD1306_I2C
from user_lib.display import Display
from user_lib.push_button import PushButton
from user_lib.scd30_recalibrator import SCD30Recalibrator
from user_lib.connection_manager import ConnectionManager
from user_lib.buzzer import Buzzer

# #################### Required Packages #############################
# import upip
# upip.install("micropython-scd30")
# upip.install("micropython-umqtt.simple")
# ####################################################################

# ###################### Configuration ###############################

PIN_BUZZER                  = 16
PIN_BUTTON                  = 15
PIN_SCL                     = 5
PIN_SDA                     = 4
CO2_I2C_ADDR                = 0x61
CO2_MEASUREMENT_INTERVAL_S  = 30
CO2_READ_INTERVAL_MS        = 10 * 1000
CO2_ALARM_HIGH              = 1500
CO2_ALARM_LOW               = 1450
OLED_I2C_ADDR               = 0x3c
OLED_WIDTH                  = 64
OLED_HEIGHT                 = 48

WLAN_SSID           = "***********"
WLAN_PASSWORD       = "***********"

MQTT_SERVER         = "192.168.1.2"
MQTT_CLIENT_ID      = "scd30"
MQTT_TOPIC_CO2      = b"/homeassistant/sensors/chemical_SCD30/CO2"
MQTT_TOPIC_TEMP     = b"/homeassistant/sensors/chemical_SCD30/TEMP"
MQTT_TOPIC_HUMI     = b"/homeassistant/sensors/chemical_SCD30/HUMI"
MQTT_USERNAME       = "sensors"
MQTT_PASSWORD       = "***********"
# ####################################################################

class App:
  def __init__(self):
    self._buzzer = Buzzer(PIN_BUZZER)
    self._btn = PushButton(PIN_BUTTON, False)
    self._btn.onClick(lambda: self._display.toggleState())
    self._btn.onLongPress(lambda: self._scd30Recalibrator.recalibrate())
    self._i2c = SoftI2C(scl=Pin(PIN_SCL), sda=Pin(PIN_SDA), freq=10000)
    self._scd30 = SCD30(self._i2c, CO2_I2C_ADDR)
    self._scd30Recalibrator = SCD30Recalibrator(self._scd30, CO2_MEASUREMENT_INTERVAL_S, buzzer=self._buzzer)
    self._display = Display(SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, self._i2c, OLED_I2C_ADDR))
    self._connectionManager = ConnectionManager()
    self._co2AlarmPlayed = False
    self._readTimestamp = 0

  def init(self):
    self._scd30.set_measurement_interval(CO2_MEASUREMENT_INTERVAL_S)
    self._scd30.start_continous_measurement()
    
    self._connectionManager.configureWlan(WLAN_SSID, WLAN_PASSWORD)
    self._connectionManager.configureMqtt(MQTT_CLIENT_ID, MQTT_SERVER, MQTT_USERNAME, MQTT_PASSWORD)
    self._connectionManager.initConnection()
 
  def update(self):
    try:
      self._btn.update()
      self._connectionManager.update()
      
      if time.ticks_ms() - self._readTimestamp > CO2_READ_INTERVAL_MS \
      and self._scd30.get_status_ready() == 1:
        self._readTimestamp = time.ticks_ms()
        measurements = self._scd30.read_measurement()
        print(measurements)
        if(measurements[0] > 0):
          self._connectionManager.publish(MQTT_TOPIC_CO2, str(measurements[0]))
        self._connectionManager.publish(MQTT_TOPIC_TEMP, str(measurements[1]))
        self._connectionManager.publish(MQTT_TOPIC_HUMI, str(measurements[2]))
        self._display.setMeasurements(measurements)
        self.__checkCo2Alarm(measurements[0])

      self._scd30Recalibrator.update()
      
      machine.idle()
    except Exception as ex:
      template = "An exception of type {0} occurred. Arguments:\n{1!r}"
      message = template.format(type(ex).__name__, ex.args)
      print(message)
  
  def __checkCo2Alarm(self, measurement):
    if measurement > CO2_ALARM_HIGH \
    and not self._co2AlarmPlayed:
      self._co2AlarmPlayed = True
      self._buzzer.buzz(4, 0.3)
    elif measurement > CO2_ALARM_LOW:
      self._co2AlarmPlayed = True

app = App()
app.init()
while True: app.update()

