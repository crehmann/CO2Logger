from utime import ticks_ms
import network
import time 
from umqtt.simple import MQTTClient

STATE_DISCONNECTED          = 0
STATE_WLAN_CONNECTING       = 1
STATE_WLAN_CONNECTED        = 2
STATE_MQTT_CONNECTING       = 3
STATE_MQTT_CONNECTED        = 4
WLAN_CONNECTION_TIMEOUT_MS  = 30 * 1000
MQTT_CONNECTION_TIMEOUT_MS  = 30 * 1000

class ConnectionManager:

  def __init__(self):
    self._wlan = network.WLAN(network.STA_IF)
    self._wlanSsid = None
    self._wlanPassword = None
    self._wlanConnectingTimestamp = None
    self._mqtt = None
    self._mqttConnectingTimestamp = None
    self._state = STATE_DISCONNECTED
    self._data = {}
    
  def configureWlan(self, ssid, password):
    self._wlanSsid = ssid
    self._wlanPassword = password
    
  def configureMqtt(self, mqttClientId, mqttServer, mqttUsername, mqttPassword):
    self._mqtt = MQTTClient(mqttClientId, mqttServer, 0, mqttUsername, mqttPassword)
    
  def initConnection(self):
    if self._state == STATE_DISCONNECTED:
      self.__connectWlan()

  def publish(self, topic, data):
    # keeping only the latest value
    self._data[topic] = data
    self.__flush()
    
  def update(self):
    if self._state > STATE_WLAN_CONNECTING \
    and not self._wlan.isconnected:
      self._state = STATE_DISCONNECTED
      
    if self._state == STATE_WLAN_CONNECTING:
      self.__updateWlanConnectingState()
    if self._state == STATE_WLAN_CONNECTED:
      self.__updateWlanConnectedState()
    if self._state == STATE_MQTT_CONNECTING:
      self.__updateMqttConnectingState()
  
  def __connectWlan(self):
    if self._wlanSsid:
      print("connecting to wlan...")
      self._wlanConnectingTimestamp = ticks_ms()
      self._state = STATE_WLAN_CONNECTING
      try:
        self._wlan.active(True)
        self._wlan.disconnect()
        self._wlan.connect(self._wlanSsid, self._wlanPassword)
      except Exception as ex:
        self.__printException(ex)
      
  def __updateWlanConnectingState(self):
    if ticks_ms() - self._wlanConnectingTimestamp > WLAN_CONNECTION_TIMEOUT_MS:
      print("Could not connect to wlan. Falling back to disconnected state")
      self._state = STATE_DISCONNECTED
    elif self._wlan.isconnected() \
    and not self._wlan.ifconfig()[0]=='0.0.0.0':
      self._state = STATE_WLAN_CONNECTED
      print("wlan connected")
    
  def __updateWlanConnectedState(self):
    if self._mqtt:
      print("connecting to mqtt")
      self._state = STATE_MQTT_CONNECTING
      self._mqttConnectingTimestamp = ticks_ms()
      try:
        self._mqtt.connect()
      except Exception as ex:
        self.__printException(ex)
    
  def __updateMqttConnectingState(self):
    if ticks_ms() - self._mqttConnectingTimestamp > MQTT_CONNECTION_TIMEOUT_MS:
      print("MQTT connection failed.")
      self._state = STATE_WLAN_CONNECTED
    else:
      try:
        self._mqtt.ping()
        self._state = STATE_MQTT_CONNECTED
        self.__flush()
        print("mqtt connection established")
      except Exception as ex:
        self.__printException(ex)
        
  def __flush(self):
    if self._state == STATE_MQTT_CONNECTED:
      try:
        for key in list(self._data):
          self._mqtt.publish(key, self._data[key])
          del self._data[key]
      except Exception as ex:
        self._state = STATE_WLAN_CONNECTED
        self.__printException(ex)
    
  def __printException(self, ex):
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(ex).__name__, ex.args)
    print(message)

