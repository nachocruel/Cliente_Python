from mongoengine import *

password='301cronos'
def connect_to_db():
	connect('pfc-2020', host='mongodb://edvan:{}@cluster0-shard-00-00-ujfno.gcp.mongodb.net:27017,cluster0-shard-00-01-ujfno.gcp.mongodb.net:27017,cluster0-shard-00-02-ujfno.gcp.mongodb.net:27017/pfc-2020?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority'.format(password))

# tipo_req=0 Normal
# tipo_req=1 Alerta
class Medicao(Document):
	id_dispositivo = StringField()
	tipo_dispositivo = StringField()
	codigo_pais = StringField()
	codigo_estado = StringField()
	codigo_municipio = StringField()
	temperatura = FloatField()
	temperatura2 = FloatField()
	temperatura3 = FloatField()
	temperatura_media = FloatField()
	device_temperature = FloatField()
	umidade = FloatField()
	umidade2 = FloatField()
	umidade3 = FloatField()
	umidade_media = FloatField()
	pressao = FloatField()
	pressao2 = FloatField()
	pressao3 = FloatField()
	pressao_media = FloatField()
	tvoc = FloatField()
	tvoc2 = FloatField()
	tvoc3 = FloatField()
	tvoc_media = FloatField()
	co2 = FloatField()
	co2_2 = FloatField()
	co2_3 = FloatField()
	co2_media = FloatField()
	device_temperature = FloatField()
	image_url = StringField()
	tipo_req = IntField()
	vid_url = StringField()
	message = StringField()
	horario = StringField()
	image = FileField()
	vid = FileField()
	salve_medicao = BooleanField()	

class Device(Document):
	max_temperature = FloatField(required=True)
	device_max_temperature = FloatField()
	low_humidity = FloatField(required=True)
	max_gas = FloatField(required=True)
	latitude = StringField()
	longitude = StringField()
	id_dispositivo = StringField()
	id_fire = StringField()
	zona = StringField()
	codigo_pais = StringField()
	codigo_estado = StringField()
	codigo_municipio = StringField()
	meta = {'allow_inheritance':True}
	
class MasterDevice(Device):
	children = ListField(Device())
	tipo_dispositivo = StringField(default='MASTER')

class SlaveDevice(Device):
	id_master = StringField(required=False)
	children = ListField(Device())
	tipo_dispositivo = StringField(default='SLAVE')

class Municipio(Document):
	codigo = StringField(default="5208707", unique=True)
	codigo_estado = StringField()
	name = StringField(default="Goiania")
	
class Estado(Document):
	codigo = StringField(default="52", unique=True)
	codigo_pais = StringField(default="55")
	name = StringField(default="Goias")
	municipios = ListField(Municipio())

class Pais(Document):
	codigo = StringField(default="55", unique=True)
	name = StringField(default="Brazil")
	language = StringField(default="pt-BR")
	estados = ListField(Estado())
