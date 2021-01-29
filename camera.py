
from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.start_preview()
for i in range(4):
	camera.capture('/home/pi/Desktop/image%s.jpg' % i)
	sleep(5)
camera.stop_preview()

camera.start_preview()
camera.start_recording('/home/pi/Desktop/video.h264')
sleep(5)
camera.stop_recording()
camera.stop_preview()


camera.resolution = (2592, 1944)
camera.framerate = 15
camera.start_preview()
sleep(5)
camera.capture('/home/pi/Desktop/max.jpg')
camera.stop_preview()
