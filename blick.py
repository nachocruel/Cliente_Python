import RPi.GPIO as GPIO
import time
import threading
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(11, GPIO.IN)

LED=17
onoff=1
ALERT=False
def alertintruder():
	global ALERT, onoff, LED
	while ALERT:
	  try:
		GPIO.output(LED, onoff)
		if(onoff==1):
			onoff=0
		else:
			onoff=1
		time.sleep(1)
	  except:
		 ALERT=False
		 GPIO.output(LED, 0)
		 
def sensorMotion():
  try:
	while(True):
		global ALERT, tr
		i=GPIO.input(11)
		print("input: ", i)
		if(i==1):
			print("intruder detected")
			if(ALERT==False):
				ALERT=True
				tr=threading.Thread(target=alertintruder)
				tr.start()			
		else:
			print("no intruder detected")
			ALERT=False
			GPIO.output(LED, 0)
		time.sleep(2)
  except:
	  ALERT=False
	  GPIO.output(LED, 0)
	  
				
sensorMotion()
		

