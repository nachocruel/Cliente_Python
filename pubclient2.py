from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import time
import os

pnconfig = PNConfiguration()

pnconfig.publish_key = "pub-c-e5c8e409-367f-4eb2-8d95-0d93e5fdfd8b"
pnconfig.subscribe_key = "sub-c-4c1671dc-347a-11ea-b8ef-b6462cb07a90"
pnconfig.ssl = True

pubnub = PubNub(pnconfig)

def my_publish_callback(envelope, status):
	if not status.is_error():
		pass
		
class MySubscribeCallBack(SubscribeCallback):
	def presence(self, pubnub, presence):
		pass
	def status(self, pubnub, status):
		pass
	def message(self, pubnub, message):
		print(message.timetoken)
		#print(message.message)

pubnub.add_listener(MySubscribeCallBack())
pubnub.subscribe().channels("chan-1").execute()

while True:
	msg = raw_input("Input a message to publish: ")
	if(msg == "exit"): os._exit(1)
	pubnub.publish().channel("chan-1").message(str(msg)).pn_async(my_publish_callback)				
