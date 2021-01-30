from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from threading import Thread
from mongodb import Device
from mongodb import Medicao
from mongodb import SlaveDevice
from mongodb import MasterDevice
from mongodb import connect_to_db
from base64 import b64encode
from threading import Thread
from asyncio import Lock
import datetime
import json
import time
import os
from asyncio import get_event_loop
import gcp_vision_detect

# picamera
lock = Lock()
from picamera import PiCamera
camera = PiCamera()
loop = get_event_loop()

# configurar pubnob
pnconfig = PNConfiguration()
pnconfig.publish_key = "Chave pubnub publica aqui"
pnconfig.subscribe_key = "Chave de subscrição aqui"
pnconfig.ssl = True
pubnub = PubNub(pnconfig)

#Setting defaut attributes
f = open("./config.json", "r")
config = f.read()
f.close()
config = json.loads(config)
server = config["server"]
max_temperature = config["max_temperature"]
low_humidity = config["low_humidity"]
max_gas = config["max_gas"]
latitude = config["latitude"]
longitude = config["longitude"]
id_dispositivo = config["id_dispositivo"]
tipo_dispositivo = config["tipo_dispositivo"]
zona = config["zona"]
codigo_pais = config["codigo_pais"]
codigo_estado = config["codigo_estado"]
codigo_municipio = config["codigo_municipio"]
device_max_temperature = config["device_max_temperature"]
max_tvoc = config["max_tvoc"]

# Ultimas medicoes

# DHT22
last_temperature1 = 0
last_humidity1 = 0

# DHT11
last_temperature2 = 0
last_humidity2 = 0

# BME280
last_temperature3 = 0
last_humidite3 = 0
last_pressure_bme280 = 0

# CCS811

last_co2 = 0
last_tvoc = 0

# MEDIAS
last_media_temperatura = 0
last_media_humidity = 0
last_media_pressure = 0
last_media_co2 = 0
last_media_tvco = 0

# Dispositivo
last_device_temperature_measurement = 0

# reconfigura variaveis globais
def reset_device_variables(new_max_temp, new_max_gas, new_humidity, new_device_temp, new_latitude, new_longitude, new_tvoc):
  global max_temperature, max_gas, low_humidity, device_max_temperature, latitude, longitude, max_tvoc
  max_temperature = new_max_temp
  max_gas = new_max_gas
  low_humidity = new_humidity
  device_max_temperature = new_device_temp
  latitude = new_latitude
  longitude = new_longitude
  max_tvoc = new_tvoc

def my_publish_callback(envelope, status):
	if not status.is_error():
		pass
		
class MySubscribeCallBack(SubscribeCallback):
    global id_dispositivo
    def presence(self, pubnub, presence):
       pass
    def status(self, pubnub, status):
       pass
    def message(self, pubnub, data):
        payload = data.message
        if(payload["acao"] == 'registro'):
            print('removendo listener: {}'.format(payload["canal"]))		
            remove_listener(payload["canal"])
            f = open("./config.json", "r")
            device = f.read()
            f.close()
            device = json.loads(device)
            print('habilitando: {}'.format(device['id_dispositivo']))
            enableChannel(device['id_dispositivo'])
        elif (payload["acao"] == 'setDeviceConfig'):
           print('setDeviceConfig')
           newConfig = payload['data']
           if(newConfig['_id'] == id_dispositivo):
             f = open("./config.json", "r")
             device = f.read()
             f.close()
             device = json.loads(device)
             device['max_temperature'] = newConfig['max_temperature']
             device['device_max_temperature'] = newConfig['device_max_temperature']
             device['latitude'] = newConfig['latitude']
             device['longitude'] = newConfig['longitude']
             device['low_humidity'] = newConfig['low_humidity']
             device['max_gas'] = newConfig['max_gas']
             device["max_tvoc"] = newConfig["max_tvoc"]
             f = open("./config.json", "w")
             f.write(json.dumps(device))
             f.close()
             reset_device_variables(device['max_temperature'], device['max_gas'], device['low_humidity'], device['device_max_temperature'], device['latitude'], device['longitude'], device["max_tvoc"])
             send_message('chan-2',{"id_dispositivo":newConfig['_id']})
           else:
             print('implementar depois')	 	  
        elif(payload["acao"] == 'lastMeasurement'):
            print('lastMeasurement')
            device = payload['data']
            if(device['_id'] == id_dispositivo):
              today = datetime.datetime.today()
              send_message('chan-3', {'success':True,'id_dispositivo':id_dispositivo, 'last_temperature1': last_temperature1, 'last_temperature2':last_temperature2, "last_temperature3": last_temperature3,"last_media_temperatura":last_media_temperatura, "last_humidity1":last_humidity1, "last_humidity2":last_humidity2, "last_humidite3":last_humidite3, "last_media_humidity":last_media_humidity, "last_co2": last_co2, "last_tvoc":last_tvoc , 'last_device_temperature_measurement':last_device_temperature_measurement, 'data_medicao':today.strftime("%d-%m-%Y %H:%M:%S")})			  
              medicao = Medicao()
              medicao.tipo_req = 0
              medicao.id_dispositivo = id_dispositivo
              medicao.tipo_dispositivo = tipo_dispositivo
              medicao.codigo_pais = codigo_pais
              medicao.codigo_estado = codigo_estado
              medicao.codigo_municipio = codigo_municipio
              medicao.zona = zona
              medicao.temperatura  = last_temperature1
              medicao.temperatura2 = last_temperature2
              medicao.temperatura3 = last_temperature3
              medicao.temperatura_media = last_media_temperatura
              medicao.umidade = last_humidity1
              medicao.umidade2 = last_humidity2
              medicao.umidade3 = last_humidite3
              medicao.umidade_media = last_media_humidity
              medicao.co2 = last_co2
              medicao.tvoc = last_tvoc
              medicao.pressao = last_pressure_bme280
              medicao.device_temperature = last_device_temperature_measurement
              medicao.horario = today.strftime("%d-%m-%Y %H:%M:%S")
              # Rotina que evicta que a camera seja acessado ao mesmo tempo
              while(loop.is_running()):
                time.sleep(5)
                
              task1 = loop.create_task(capturePhoto(medicao, False))
              loop.run_until_complete(task1)
  
              while(loop.is_running()):
                time.sleep(5)
  
              task2 = loop.create_task(recordVideo(medicao))
              loop.run_until_complete(task2)
              # Fim da rotina
              medicao.message = "Leitura normal"
              medicao.save()			  
            else:
              print('implementar depois')
        else:
           print('acao nao encontrada')
								
def send_message(canal, acao):
 pubnub.publish().channel(canal).message(acao).pn_async(my_publish_callback)	

my_listener = None
canalAtual = None
def enableChannel(canal):
 global my_listener, canalAtual
 canalAtual = canal
 my_listener = MySubscribeCallBack()
 pubnub.add_listener(my_listener)
 pubnub.subscribe().channels(canal).execute()

def remove_listener(canal_remove):
 global my_listener
 if(canal_remove is not None):	
  pubnub.unsubscribe().channels(canal_remove).execute()
 if(my_listener is not None):	
  pubnub.remove_listener(my_listener)

labelsAlert = ['Glass', 'Guitar', 'Headphone', 'Cellphone', 'Tractor', 'Chainsaw', 'Backhoe', 'Fishing net']
async def capturePhoto(medicao, detectLabel):
  async with lock:
    global camera
    print("****************Tirando foto*****************")
    mili = int(round(time.time() * 1000))
    fileName='{id_dispositivo}_{tm}_image.jpg'.format(id_dispositivo=id_dispositivo, tm=mili)
    path_img = './resources/img/{filename}'.format(filename=fileName)
    camera.vflip = True
    camera.start_preview()
    time.sleep(10)
    camera.capture(path_img)
    camera.stop_preview()
    medicao.salve_medicao = True
    if(detectLabel == True):
      medicao.salve_medicao = False
      labels = gcp_vision_detect.getLabelsAnnotation(path_img)
      for label in labels:
         print(label.description)
         if(label.description in labelsAlert):
            print('*******{}*******'.format(label.description))
            medicao.message = medicao.message + " label: " + label.description
            medicao.salve_medicao = True
    
    # Salva imagem caso label seja detectado ou seja de inconsistência de sensores
    if(medicao.salve_medicao == True):
       gcp_vision_detect.upload_blob('pfc-2020', path_img, fileName)
       
    medicao.image_url = fileName
    t=Thread(target=removeFIle, args=(path_img, ))
    t.start()

	  
async def recordVideo(medicao):
   async with lock:
     global camera
     print("***********Gravando video***********")
     mili = int(round(time.time() * 1000))
     h264='{id_dispositivo}_{tm}_video.h264'.format(id_dispositivo=id_dispositivo, tm=mili)
     mp4='{id_dispositivo}_{tm}_video.mp4'.format(id_dispositivo=id_dispositivo, tm=mili)
     path_vid = './resources/vid/{filename}'.format(filename=h264)
     camera.vflip = True
     camera.start_preview()
     camera.start_recording(path_vid)
     time.sleep(15)
     camera.stop_recording()
     camera.stop_preview()
     os.system('MP4Box -fps 30 -add ./resources/vid/{h264} ./resources/vid/{mp4}'.format(h264=h264, mp4=mp4))
     time.sleep(5)
     medicao.vid_url = mp4
     t1=Thread(target=removeFIle, args=(path_vid, ))
     t1.start()
     path_vid = './resources/vid/{filename}'.format(filename=mp4)
     gcp_vision_detect.upload_blob('pfc-2020', path_vid, mp4)
     t2=Thread(target=removeFIle, args=(path_vid, ))
     t2.start()
    
def removeFIle(filePath):
	time.sleep(15)
	os.remove(filePath)
	 	
def limpar_listeners():
   os._exit(1)  	
