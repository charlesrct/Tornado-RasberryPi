import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options
import json
from uuid import uuid4

#libreria para usar el puerto GPIO
import RPi.GPIO as GPIO

#configurando GPIO
#pines por el numero impreso en la tarjeta,numeracion distribucion fisica 
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
        GPIO.output(11, False)
        
        pulsador.notifyCallbacks(0, 'El Led fue apagado por Hardware')

    if(inputValue == False):
        GPIO.output(11, True)
        
        pulsador.notifyCallbacks(1, 'El Led fue encendido por Hardware')

    print('Interrupcion por hardware')


GPIO.add_event_detect(swichtPin, GPIO.RISING, callback=pinkCall, bouncetime=500)

class Raspberry(object):
	callbacks = []

	def register(self, callback):
		self.callbacks.append(callback)

	def unregister(self, callback):
		self.callbacks.remove(callback)

	def ledON(self):
            #Encendemos el Led conectado en el pin 11
            GPIO.output(11, True)
            self.notifyCallbacks(1, "Led Encendido")

	def ledOFF(self):
            #Apagamos el Led conectado en el pin 11
            GPIO.output(11, False)
            self.notifyCallbacks(0, "Led Apagado")

	def notifyCallbacks(self, ledStdo, estado):
		for callback in self.callbacks:
			callback(ledStdo, estado)

class RenderHandler(tornado.web.RequestHandler):

	def get(self):
		session = uuid4()
		estado = "...Iniciando"
		self.render("index.html", session=session, estado=estado)


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

	def callback(self, ledStdo, estado):

		self.write_message(json.dumps({
			"ledStdo": ledStdo,
			"estado": estado
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