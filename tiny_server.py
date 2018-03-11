from base.tiny_Q import QPOOL
from base.index import Index
from base.http_parser import Http_parser
import threading
import socket
import time
import re

__LOCK__ = threading.Lock()
parser = Http_parser()

class Socket_thread(threading.Thread): #Socket not work in main thread
	def __init__(self,socketobj,callback,host="127.0.0.1",port=8989,max_conn=1000,*args,**kw):
		self.host = host
		self.port = port
		self.max_conn = max_conn
		self.socket = socketobj
		self.callback = callback #What to do after accepted
		super(socket_thread,self).__init__(*args,**kw)
		self.__STOP__ = False
		
	def stop(self):
		self.__STOP__ = True
		
	def run(self):
		self.socket.bind((self.host,self.port))
		self.socket.listen(self.max_conn)
		while True:
			sock, addr = s.accept()
			self.callback(sock,addr)	#put into accepted_queue

#Manager of main socket and acceptions 
class Socket_layer(object):
	def __init__(self):
		self.Qs = QPOOL()
		self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.accepted_queue = self.Qs.createQ(name="acq",max_len=1000)
		self.socket_thread = None
		
	def run(self,**kw):
		self.socket_thread = Socket_thread(self.main_socket,self.sock_callback,**kw) #Start main socket
		self.socket_thread.start()
	
	#Give socket thread
	def sock_callback(self,sock,addr):
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
		
		
#layer-3
class Worker_thread(threading.Thread):
	def __init__(self,get_task,interval=0.002):
		self.get_task = get_task
		self.interval = interval
		self.__STOP__ = False
		
	def stop(self):
		self.__STOP__ =True
		
	def run(self):
		while True:
			try:
				current_task = self.get_task() 
				if current_task != None:
					current_task.run()
				else:
					time.sleep(self.interval)
			except Exception as e:
				time.sleep(self.interval)
			finally:
				if self.__STOP__ :
					break
					
class Task(object):
	def __init__(self,callback,*args,**kw):
		self.callback = callback
		self.args = args
		self.kw = kw

#Instantly make a response (as soon as quickly, need't wait for some msg)
#including receive, dicide callback and return
class Instant_task(Task): #resp part is included in callback function
	def __init__(self,accepted,callback_index,callback=None,*args,**kw):
		super(Http_task,self).__init__(callback,*args,**kw)
		self.sock = accepted[0]
		self.addr = accepted[1]
		self.callback_index = callback_index
		
	def run(self): #read -> parse -> callback
		http = b''
		while True:
			data = self.sock.recv(1024)
			if data:
				http += data
			else:
				break
		info = parser.parse(raw_data)
		splited_url = parser.url_split(info['url'])
		callback = self.callback_index.url_find(splited_url) 	#callback是个封装过一层的函数，在外层会有请求参数与获取sock的函数
		resp_info = callback(info)								#触发这一函数会改变外层的一个标识，使返回值中 do_resp = False, 不进行返回操作
		if resp['do_resp']==True:				
			response = parser.pack(headers=resp_info.pop('headers'),text=resp_info.pop('text'),**resp_info)
			self.sock.send(response)
			
'''
Each request will trigger an Instant_task.
But, u can take the socket acception out in a 'Message Waiting Queue'
Then retuen 'None' to skip the rest of callback
For example:
request for new msg from a friend
1. If you have it now, just return text to Instant_task.run()
2. If not, use get_scok() in callback so that this can free current worker. 
	When you got the new msg, put {'sock':...,'headers':{...},'text':'...'} 
	('status_code' & 'status_msg' in resp are also avaliable)
	in queue 'resp_Q' like:
	Site = Request_handler()
	...
	...
	Site.resp_put(	
			waiting['ZIM7KASD22SD'], 	#sock
			{							#info
			'headers':
				{
					'Server':'Python'
				},
			'text':'Hello, world!'
			}	
		)
Then it will be taken by a worker as a Response_task
'''
class Response_task(Task): #Take a HANGED UP link and only make a response
	def __init__(self,resp_info):
		super(Http_task,self).__init__(callback,*args,**kw)
		self.target_sock = resp_info['sock']
		self.info = resp_info['info']
		
	def run(self):
		resp = parser.pack(headers=self.info.pop('headers'),text=self.info.pop('text'),**self.info)
		self.target_sock.send(resp)
		
		
'''writing'''
#support /a/b/<c>/<d> c,d as params like flask		
class Url_index(Index):
	def __init__(self,*args,**kw):
		super(Url_index,self).__init__(*args,**kw)
		self.stop_layer = 0
		
	def url_find(self,splited_url):
		for i in range(len(splited_url)):
			res = self.find(splited_url[:i+1])
			if res == '*':
				stop_layer = i
				break

class Request_handler(object): # <- add some setting here?
	def __init__(self,max_worker=30):
		self.callback_index = Url_index()
		self.Socket_layer = Socket_layer()
		self.worker_pool = set_worker(max_worker)
		self.Qs = QPOOL() 
		self.resp_Q = Qs.createQ(name='resp',max_len=5000)
		self.Socket_layer.run()
		
	def set_worker(self,max_worker):
		workers = [Worker_thread(self.get_task) for i in range(max_worker)]
		return workers
		
	def put_resp(self,sock,info):
		resp_task_info = {'sock':sock,'info':info}
		__LOCK__.acquire()
		self.resp_Q.put(resp_task_info)
		__LOCK__.release()
		
	def get_task(self):
		__LOCK__.acquire()
		if not self.resp_Q.is_empty():
			resp_info = resp_Q.get()
			__LOCK__.release()
			task = Response_task(resp_info)
		else:
			current_accepted = Socket_layer.accepted_queue.get()
			__LOCK__.release()
			task = Http_full_task(current_accepted,self.callback_index)
		
		return task
		
	#url_str like "/aaa/bbb/<ccc>" <ccc> should not be regist but as a param
	#so dict.value = callback [think about how to save the number of <?> params] 
	def register(self,url_str,callback): 
		splited_url = self.parser.url_split(url_str)
		self.callback_index.register(splited_url,callback)
		
	def site_map(self):
		return self.callback_index.tree()
		
		