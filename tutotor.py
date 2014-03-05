import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options
import json
import time
import threading
from uuid import uuid4

#libreria para usar el puerto GPIO
import RPi.GPIO as GPIO

#Libreria para comunicacion I2C con arduino.
import smbus

#Configurando I2C como master
bus = smbus.SMBus(1)
#Asignamos la direccion 0x04 que es la misma direccion del Arduino
address = 0x04

#configurando GPIO
#pines por el numero impreso en la tarjeta, numeracion distribucion fisica 
#GPIO.setmode(GPIO.BOARD)    
#pines por el numero canal de las etiquetas.
GPIO.setmode(GPIO.BCM)

#Configurando el pin de salida
GPIO.setup(11, GPIO.OUT)
GPIO.output(11, False)

#Configurando el pin de entrada
swichtPin = 10

GPIO.setup(swichtPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Interrupcion por hardware
def pinkCall(channel):
    pulsador = Raspberry()
    inputValue = GPIO.input(11)
    
    if(inputValue == True):
        #Apagamos el led desde el pulsador
        GPIO.output(11, False)
        #Se envia el numero 0 al Arduino via I2C
        bus.write_byte(address, 0)
        #Se notifican todos los usuarios via Websockets
        pulsador.notifyCallbacks(0, 'El Led fue apagado por Hardware', -1)

    if(inputValue == False):
        #Encendemos el led desde el pulsador
        GPIO.output(11, True)
        #Se envia el numero 1 al Arduino via I2C
        bus.write_byte(address, 1)
        #Se notifican todos los usuarios via Websockets
        pulsador.notifyCallbacks(1, 'El Led fue encendido por Hardware', -1)

    print('Interrupcion por hardware')


GPIO.add_event_detect(swichtPin, GPIO.RISING, callback=pinkCall, bouncetime=500)

class Raspberry(object):
	callbacks = []
	distancia = 0

	def obDistancia(self):
		distancia = bus.read_byte(address)	
		self.notifyCallbacks(-1, '-1', distancia)
		print('distancia= ', distancia)
			
		
	def register(self, callback):
		self.callbacks.append(callback)

	def unregister(self, callback):
		self.callbacks.remove(callback)

	def ledON(self):
            #Encendemos el Led conectado en el pin 11
            GPIO.output(11, True)
            #Se envia el numero 1 al Arduino via I2C
            bus.write_byte(address, 1)
            #Se notifican todos los usuarios via Websockets
            self.notifyCallbacks(1, "Led Encendido", -1)
	    self.obDistancia()

	def ledOFF(self):
            #Apagamos el Led conectado en el pin 11
            GPIO.output(11, False)
            #Se envia el numero 0 al Arduino via I2C
            bus.write_byte(address, 0)
            #Se notifican todos los usuarios via Websockets
            self.notifyCallbacks(0, "Led Apagado", -1)

	def notifyCallbacks(self, ledStdo, estado, distancia):
		for callback in self.callbacks:
			callback(ledStdo, estado, distancia)

class CuentaDistancia(threading.Thread):
	def run(self):
		d = Raspberry()
		n = 50
		while True:
			d.obDistancia()
			time.sleep(1)

th = CuentaDistancia()
th.daemon = True
th.start()

class RenderHandler(tornado.web.RequestHandler):

	def get(self):
		session = uuid4()
		estado = "...Iniciando"
		distancia = 0
		self.render("index.html", session=session, estado=estado, distancia=distancia)


class LedHandler(tornado.web.RequestHandler):
	def post(self):
		action = self.get_argument('action')
		session = self.get_argument('session')
		
		if not session:
			self.set_status(400)
			return

		if action == 'ledon':
			self.application.raspberry.ledON()
		elif action == 'ledoff':
			self.application.raspberry.ledOFF()
		elif action == 'distancia':
			self.application.raspberry.obDistancia()
		else:
			self.set_status(400)

class RaspberryHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		self.write_message('{"estado":"Conexion abierta"}')
		self.application.raspberry.register(self.callback)	
		print("Conexion abierta ")
	
	def on_close(self): 
		self.application.raspberry.unregister(self.callback)
		print("Conexion Cerrada")

	def on_message(self, message):
		self.write_message('{"estado":"Mensaje Recibido"}')
		print("Mensaje Recibido: {}" .format(message)) 	

	def callback(self, ledStdo, estado, distancia):

		self.write_message(json.dumps({
			"ledStdo": ledStdo,
			"estado": estado,
			"distancia": distancia
			}))

class Application(tornado.web.Application):
	try:
		def __init__(self):
			self.raspberry = Raspberry()
		
			handlers = [
				(r'/', RenderHandler),
				(r'/led', LedHandler),
				(r'/status', RaspberryHandler)
			]
		
			settings = {
				'template_path': 'templates',
				'static_path': 'static'
			}

			tornado.web.Application.__init__(self, handlers, **settings)
	
	except keyboardInterrupt:
		print("No se pudo realizar la Conexion")


if __name__ == '__main__':
	tornado.options.parse_command_line()	
	
	app = Application()
	server = tornado.httpserver.HTTPServer(app)
	server.listen(5000)
	tornado.ioloop.IOLoop.instance().start()