from base.tiny_Q import QPOOL
import threading
import socket
import ssl
import os
from main.Files import file_check
__LOCK__ = threading.Lock()

class Main_sock(threading.Thread): #Socket not work in main thread
	def __init__(self,socketobj,callback,ssl_open=False,cert=None,key=None,host="127.0.0.1",port=8989,max_conn=1000,*args,**kw):
		print(" Binding %s:%s" % (host,port))
		self.host = host
		self.port = port
		self.max_conn = max_conn
		self.socket = socketobj
		self.callback = callback #How to deal acceptions
		if ssl_open == True:
			exist_c,per_c= file_check(cert)
			exist_k,per_k = file_check(key)
			if exist_c and exist_k and (per_c & per_k & 0b100):
				self.ssl_open = ssl_open
				self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
				self.context.load_cert_chain(certfile=cert,keyfile=key)
				print("[*]SSL mode") 
			else:
				print("Valid cert/key path, SSL launch failed.")
				self.ssl_open = False
		else:
			self.ssl = False
		super(Main_sock,self).__init__(*args,**kw)
		self.__STOP__ = False
		
	def stop(self):
		self.__STOP__ = True
		
	def run(self):
		self.socket.bind((self.host,self.port))
		self.socket.listen(self.max_conn)
		while True:
			sock, addr = self.socket.accept()
			if self.ssl_open == True:
				sock = self.context.wrap_socket(sock, server_side=True)
			self.callback(sock,addr)	#put into accepted_queue

#Manager of main socket and acceptions
class Link_handler(object):
	def __init__(self,ssl=False,cert=None,key=None):
		self.Qs = QPOOL()
		self.accepted_queue = self.Qs.createQ(name="acq",max_len=1000)
		self.main_socket_thread = None
		self.host = None
		self.port = None
		self.ssl_state = {	"ssl_open": ssl,
							"cert":cert,
							"key":key		}
		
	def run(self,**bind):
		main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.main_socket_thread = Main_sock(main_socket,self.save_new_acception,**self.ssl_state,**bind) #Start main socket
		self.main_socket_thread.start()
	
	#callback for main socket, to put the acception in queue
	def save_new_acception(self,sock,addr):
		func=self.accepted_queue.put
		accepted = [sock,addr]
		__LOCK__.acquire()
		func(accepted)
		__LOCK__.release()
		
	def stop(self):
		self.socket_thread.stop()
		
	def get_accepted_sock(self): #give raw socks to next layer
		try:
			sock = self.accepted_queue.get()
			return sock
		except Exception as e:
			return None
			
			
			