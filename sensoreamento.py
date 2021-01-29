import RPi.GPIO as GPIO
import time
import datetime
import sys
import Adafruit_DHT
import json
from threading import Thread
import pubclient1
from mongodb import Device
from mongodb import Medicao
from mongodb import SlaveDevice
from mongodb import MasterDevice
from mongodb import connect_to_db
from base64 import b64encode
from uuid import uuid1 as get_uuid1
import logging
import os
from asyncio import get_event_loop

#adafruit sensor ccs811
loop = get_event_loop()
import adafruit_ccs811
import busio
from board import *
#i2c_bus = busio.I2C(SCL, SDA)
#ccs = adafruit_ccs811.CCS811(i2c_bus)

# adafruit sensor bm3-280
#import adafruit_bme280
#bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c_bus)

# config logging
logging.basicConfig()

#configura gpio
#from RPLCD.gpio import CharLCD
hdt22 = 27
hdt11 = 13
trigger = 21
eco = 20
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(hdt22, GPIO.IN)
GPIO.setup(hdt11, GPIO.IN)

GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(eco, GPIO.IN)
GPIO.setup(26, GPIO.OUT)

#globals
humidity_notification = True
temperature_notification = True
device_temperature_notification = True
co2_notification = True
tvoc_notification = True
hiper_notification = True
run = True

#inicia mongoengine
connect_to_db()

# verifica se dispositivo ja foi registrado
if(pubclient1.id_dispositivo == "not configured"):
  print("registrando dispositivo")
  canal = get_uuid1()
  canal = str(canal)
  #pubclient1.enableChannel(canal)
  time.sleep(5)
  device = MasterDevice()
  device.max_temperature = pubclient1.max_temperature
  device.low_humidity = pubclient1.low_humidity
  device.max_gas = pubclient1.max_gas
  device.latitude = pubclient1.latitude
  device.longitude = pubclient1.longitude
  device.id_fire = "nao aplicado"
  device.zona = zona
  device.children = []
  device.codigo_pais = pubclient1.codigo_pais
  device.codigo_estado = pubclient1.codigo_estado
  device.codigo_municipio = pubclient1.codigo_municipio
  device.device_max_temperature = pubclient1.device_max_temperature
  device.save()
  if(device.id):
   config["id_dispositivo"] = str(device.id)
   f = open("./config.json", "w")
   f.write(json.dumps(config))
   f.close()
   pubclient1.send_message('registro', {"acao":0,'canal':canal, "device": config})
else:
  pubclient1.enableChannel(pubclient1.id_dispositivo)



#inicia leitura do sensor
def iniLeituraSensor():
 global run, humidity_notification, temperature_notification, device_temperature_notification, co2_notification, tvoc_notification
 try:
  while(run):
    # MEDICAO SENSOR DHT22
    print("SENSOR DHT22")
    umidade1, temperatura1 = Adafruit_DHT.read_retry(22, hdt22)
    pubclient1.last_temperature1 = temperatura1
    pubclient1.last_humidity1 = umidade1
    if(umidade1 != None and temperatura1 != None):
      print("dht22 - ", "temperatura: ", "%.2f"% temperatura1, " umidade: ", "%.2f"% umidade1)
    print("\n")
    
    
    time.sleep(3)
    # MEDICAO SENSOR HDT11
    print("SENSOR HDT11")
    umidade2, temperatura2 = Adafruit_DHT.read_retry(11, hdt11)
    pubclient1.last_temperature2 = temperatura2
    pubclient1.last_humidity2 = umidade2
    if(umidade2 != None and temperatura2 != None):
      print("dht11 - ", "temperatura: ", "%.2f"% temperatura2, " umidade: ", "%.2f"% umidade2)
    print("\n")
    
    '''
    # MEDICAO SENSOR CCS811
    print("SENSOR CCS811")
    co2_1 = ccs.eco2 # medicao co2 ccs811
    tvoc1 = ccs.tvoc # medicao tvoc ccs811
    pubclient1.last_co2 = co2_1
    pubclient1.last_tvoc = tvoc1
    print("ccs811 - ","CO2: ", str(co2_1), " TVOC: ", str(tvoc1))
    time.sleep(3)
    print("\n")'''
    co2_1 = 10
    tvoc1 = 0
    
    # MEDICAO SENSOR BME280
    '''print("SENSOR BME280")
    temperatura3 = bme280.temperature
    umidade3 = bme280.humidity
    pressao1 = bme280.pressure
    pubclient1.last_temperature3 = temperatura3
    pubclient1.last_humidite3 = umidade3
    pubclient1.last_pressure_bme280 = pressao1
    print("bme811 - ", "temperatura: ", "%.2f"% temperatura3, " umidade: ", "%.2f"% umidade3, " pressao: ", "%.2f"% pressao1)
    print("\n")'''
    temperatura3 = 23
    umidade3 = 80
    pressao1 = 9000
    
    # MEDICAO TEMPERATURO RASPBERRY PY
    print("MEDICAO RASPBERRI PY")
    device_temperature = os.popen("vcgencmd measure_temp").readline()
    device_temperature = float(device_temperature[5:len(device_temperature) - 3])
    pubclient1.last_device_temperature_measurement = device_temperature
    print("Temperatura raspberry: ", str(device_temperature))
    print("\n")
    
    # MEDIA DAS MEDICOES
    print("MEDIAS DAS MEDICOES\n")
    temperatura_media = getMedia(temperatura1, temperatura2, temperatura3)
    pubclient1.last_media_temperatura = temperatura_media
    print("temperatura media: %.2f"% temperatura_media)
    umidade_media = getMedia(umidade1, umidade2, None)
    pubclient1.last_media_humidity = umidade_media
    print("umidade media: %.2f"% umidade_media)
    media_co2 = getMedia(co2_1, None, None)
    pubclient1.last_media_co2 = media_co2
    print("CO2 media: %.2f"% media_co2)
    media_tvoc = getMedia(tvoc1, None, None)
    print("TVOC media: %.2f"% media_tvoc)
    pubclient1.last_media_tvco = media_tvoc
    print("\n")
    
    # Checa temperaturas
    tempVer = verificaMedicaoTemperatura(temperatura1, temperatura2, temperatura3, temperatura_media)
    if(tempVer["alert"] == True):
      if(temperature_notification == True):
        print(tempVer["message"])
        temperature_notification = False
        thredTemp= Thread(target=sendNotificatio, args=(temperatura1, temperatura2, temperatura3, temperatura_media, umidade1, umidade2, umidade3, umidade_media, co2_1, tvoc1, pressao1, device_temperature, pubclient1.id_dispositivo, tempVer["message"], False))
        thredTemp.setDaemon(True)
        thredTemp.start()
    
    # Checa Humidades
    humiVer = verificarMedicaoUmidade(umidade1, umidade2, umidade3, umidade_media)
    if(humiVer["alert"] == True):
      if(humidity_notification == True):
        print(humiVer["message"])
        humidity_notification = False
        threadHum = Thread(target=sendNotificatio, args=(temperatura1, temperatura2, temperatura3, temperatura_media, umidade1, umidade2, umidade3, umidade_media, co2_1, tvoc1, pressao1, device_temperature, pubclient1.id_dispositivo, humiVer["message"], False))
        threadHum.setDaemon(True)
        threadHum.start()
    
    # Checa CO2
    co2Ver = verificaMedicaoCO2(co2_1, None, None, media_co2)
    if(co2Ver["alert"] == True):
      if(co2_notification == True):
        print(co2Ver["message"])
        co2_notification = False
        threadCO2 = Thread(target=sendNotificatio, args=(temperatura1, temperatura2, temperatura3, temperatura_media, umidade1, umidade2, umidade3, umidade_media, co2_1, tvoc1, pressao1, device_temperature, pubclient1.id_dispositivo, co2Ver["message"], False))
        threadCO2.setDaemon(True)
        threadCO2.start()
      
    # Checa TVOC
    tvocVer = verificarTVOC(tvoc1, None, None, media_tvoc)
    if(tvocVer["alert"] == True):
      if(tvoc_notification == True):
        print(tvocVer["message"])
        tvoc_notification = False
        threadtvoc = Thread(target=sendNotificatio, args=(temperatura1, temperatura2, temperatura3, temperatura_media, umidade1, umidade2, umidade3, umidade_media, co2_1, tvoc1, pressao1, device_temperature, pubclient1.id_dispositivo, tvocVer["message"], False))
        threadtvoc.setDaemon(True)
        threadtvoc.start()
    
    # Checa temperatura do raspberry
    if(device_temperature != None and device_temperature >= pubclient1.device_max_temperature):
      if(device_temperature_notification == True):
        print("temperatura do computador muito alta")
        device_temperature_notification = False
        deviceThr = Thread(target=sendNotificatio, args=(temperatura1, temperatura2, temperatura3, temperatura_media, umidade1, umidade2, umidade3, umidade_media, co2_1, tvoc1, pressao1, device_temperature, pubclient1.id_dispositivo, "temperatura do computador muito alta", False))
        deviceThr.setDaemon(True)
        deviceThr.start()
      
    time.sleep(5)
 except KeyboardInterrupt:
   print("execucao foi interronpida")
   pubclient1.limpar_listeners()

def verificarMedicaoUmidade(umidade1, umidade2, umidade3, umidade_media):
  if(umidade1 == None or umidade2 == None):
    return {"alert": True, "message": "Um dos sensores não retornou a umidade!"}
  if(umidade1 <= pubclient1.low_humidity or umidade2 <= pubclient1.low_humidity):
    return {"alert": True, "message": "Umidade ambiente muito baixa" }
  if(umidade_media != 0 and (((umidade1 / umidade_media) * 100) <= 50 or ((umidade2 / umidade_media) * 100) <= 50)):
    return {"alert": True, "message": "Um dos sensores apresentou medicao de humidade muito baixa em relacao a media" }
  else:
    return {"alert": False }
    

def verificaMedicaoTemperatura(temperatura1, temperatura2, temperatura3, temperatura_media):
  if(temperatura1 == None or temperatura2 == None or temperatura3 == None):
    return {"alert": True, "message": "Um dos sensores não retornou a temperatura!" }
  if(temperatura1 >= pubclient1.max_temperature or temperatura2 >= pubclient1.max_temperature or temperatura3 >= pubclient1.max_temperature):
    return {"alert": True, "message": "Sensor não retornou a temperatura." }
  if(temperatura_media != 0 and (((temperatura1 / temperatura_media) * 100) <= 50 or ((temperatura2 / temperatura_media) * 100) <= 50 or ((temperatura3 / temperatura_media) * 100) <= 50)):
    return {"alert": True, "message": "Um dos sensores esta apresentando temperatura muito baixa em relacao a media."}
  else:
    return {"alert": False }
    
def verificaMedicaoCO2(co2_1, co2_2, co2_3, media_co2):
  if(co2_1 == None):
    return { "alert": True, "message": "Um dos sensores não retornou a medicao de CO2!" }
  if(co2_1 >= pubclient1.max_gas):
    return { "alert": True, "message": "Um dos sensores detectou elevacao de CO2" }
  if(media_co2 != 0 and ((co2_1 / media_co2) * 100) <= 50):
    return { "alert": True, "message": "Um dos sensores esta apresentado valores muitos baixos em relacao a media de CO2" }
  else:
    return { "alert": False }
    
def verificarTVOC(tvoc1, tvoc2, tvoc3, media_tvoc):
  if(tvoc1 == None):
    return { "alert": True, "message": "Um dos sendores não retornou a medicao de TVOC" }
  if(tvoc1 >= pubclient1.max_tvoc):
    return { "alert": True, "message": "Um dos sensores detectou elevacao de TVOC" }
  else:
    return { "alert": False }
  

def getMedia(medicao1, medicao2, medicao3):
  total = 0
  div = 1
  if(medicao1 != None):
    total = medicao1
  if(medicao2 != None):
    total = total + medicao2
    div = div + 1
  if(medicao3 != None):
    total = total + medicao3
    div = div + 1
  return (total / div)

def sendNotificatio(temperature1, temperature2, temperature3, temperature_media, humidity1, humidity2, humidity3, humidity_media, co2, tvoc, pressao, device_temperature, id_dispositivo, message, detectLabel):
  global temperature_notification, humidity_notification, device_temperature_notification, co2_notification, tvoc_notification, hiper_notification, loop
  medicao = Medicao()
  today = datetime.datetime.today()
  medicao.tipo_req = 1
  medicao.id_dispositivo = pubclient1.id_dispositivo
  medicao.tipo_dispositivo = pubclient1.tipo_dispositivo
  medicao.codigo_pais = pubclient1.codigo_pais
  medicao.codigo_estado = pubclient1.codigo_estado
  medicao.codigo_municipio = pubclient1.codigo_municipio
  medicao.zona = pubclient1.zona
  medicao.temperatura  = temperature1
  medicao.temperatura2 = temperature2
  medicao.temperatura3 = temperature3
  medicao.temperatura_media = temperature_media
  medicao.umidade = humidity1
  medicao.umidade2 = humidity2
  medicao.umidade3 = humidity3
  medicao.umidade_media = humidity_media
  medicao.co2 = co2
  medicao.tvoc = tvoc
  medicao.pressao = pressao
  medicao.device_temperature = device_temperature
  medicao.horario = today.strftime("%d-%m-%Y %H:%M:%S")
  medicao.message = message
  
  # Rotina que evicta que a camera seja acessado ao mesmo tempo
  while(loop.is_running()):
    time.sleep(5)
      
  task1 = loop.create_task(pubclient1.capturePhoto(medicao, detectLabel))
  loop.run_until_complete(task1)
  
  while(loop.is_running()):
    time.sleep(5)
  
  # Captura video somente se dectou label ou for altercao ambiente
  if(medicao.salve_medicao == True):
    task2 = loop.create_task(pubclient1.recordVideo(medicao))
    loop.run_until_complete(task2)
    
  # Fim da rotina salva se necessário
  if(medicao.salve_medicao == True):
     print('****Salvando medicao****')
     medicao.save()
     messageAtual = "Dispositivo: {id_d} \n {msg}".format(id_d=pubclient1.id_dispositivo, msg=message)
     notify = Thread(target=pubclient1.send_message, args=("chan-1", {"acao":"alert", "message":messageAtual}))
     notify.start()

  time.sleep(60 * 20)
  if(temperature_notification == False):
    temperature_notification = True
  if(humidity_notification == False):
    humidity_notification = True
  if(device_temperature_notification == False):
    device_temperature_notification = True
  if(co2_notification == False):
    co2_notification = True
  if(tvoc_notification == False):
    tvoc_notification = True
  if(hiper_notification == False):
    hiper_notification = True


sampling_rate = 20.0
speed_of_sound = 349.10
max_distance = 4.0
max_delta_t = max_distance / speed_of_sound
GPIO.output(trigger, False)
time.sleep(1)

def habilitarHiperSonico():
  global hiper_notification
  start_t = 0
  end_t = 0
  while(True):
    try:
        GPIO.output(trigger, True)
        time.sleep(0.00001)
        GPIO.output(trigger, False)
        
        # aguarda retorno do echo
        while(GPIO.input(eco) == 0):
            start_t = time.time()
        
        # Aguarda volta ao estado False
        while(GPIO.input(eco) == 1 and time.time() - start_t < max_delta_t):
            end_t = time.time()
        
        if(end_t - start_t < max_delta_t):
            delta_t = end_t - start_t
            distance = 100 * (0.5 * delta_t * speed_of_sound)
        else:
            distance = -1
	    
        if(distance != -1 and round(distance, 2) < 30 and hiper_notification == True):
            hiper_notification = False
            t = Thread(target=sendNotificatio, args = (None, None, None, None, None, None, None, None, None, None, None, None, pubclient1.id_dispositivo, "Label não autorizados detectado", True))
            t.setDaemon(True)
            t.start()
	    
        #print(round(distance, 2))
        time.sleep(1/sampling_rate)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("interrompido!")
	
t_hiper = Thread(target=habilitarHiperSonico)
t_hiper.setDaemon(True)
t_hiper.start()
iniLeituraSensor()	
