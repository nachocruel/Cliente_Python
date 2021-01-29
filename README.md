# Para iniciar.

sudo apt-get update
sudo apt-get install -y build-essential python-pip python-dev python-smbus git

# Instalar AfruitGIO
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
cd Adafruit_Python_GPIO
sudo python setup.py install

# Intalar CircuitPython ccs811

sudo pip3 install adafruit-circuitpython-ccs811

# Instalar AdafruitDHT

git clone https://github.com/adafruit/Adafruit_Python_DHT.git

# Instalar adafruit-circuitpython-bme-280

sudo pip3 install adafruit-circuitpython-bme280

# Instalar MongoEngine

pip3 install mongoengine

# Install pubnub

pip3 install pubnub

# Digitar no terminal: sudo raspi-config
# habilitar i2c, pi camera