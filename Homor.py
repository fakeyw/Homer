from base.tiny_Q import QPOOL
from base.index import Index
from base.http_parser import Http_parser
import threading
import socket
import time

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
	
	def get_sock_outer(sign):
		def get_sock():
			sign[0] = False
			return self.sock
		
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
		callback,url_params = self.callback_index.url_find(splited_url) 			
		if callback == None:
			'''Write 404 page'''
			callback,url_params = callback_index.url_find(['404'])
		resp_info = callback(**info,**url_params,get_sock_outer=self.get_sock_outer)
		#↑ Put all parames & get_sock() constructer in outer_callback
		'''
		operate like this, it works:
		def e(a,b):
			pass
		e(**{'a':1},**{'b':2})
		'''
		if resp_info.pop('do_resp') == True:				
			response = parser.pack(**resp_info)
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

'''
About user callback standered:
I prefer the decorator like flask, 
but cuz this frame supports asynchronous service
there's something different

Site = Request_handler()
@Site.register('/a/<b>/c',methods=['GET'])
def home(b,**kw):  		# '**xxx' <-here we don't user global var, but need an entrance
	args = kw['args']					#GET data 				dict
	data = kw['data']					#POST data				dict
	req_headers = kw['request_headers']	#request headers		dict
	url_params = kw['url_params']		#Params bind like <p>	dict
	...
	...
	resp = {								#
		'headers':{'User-Agent':'xxxxx',
					...					},
		'text':'xxxxxxxxxxxx'
		}
	return resp
'''
		
class Url_index(Index):
	def __init__(self,*args,**kw):
		super(Url_index,self).__init__(*args,**kw)
		self.stop_layer = 0
		
	def url_find(self,splited_url):
		for i in range(len(splited_url)):
			res = self.find(splited_url[:i+1])
			if res == '*':
				self.stop_layer = i
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
		
	def register(url,methods,**kw): # Get register params
		pattern = re.compile(r'^<.*>$?')
		splited_url = self.parser.url_split(url_str)
		add_param_list = []
		for i in splited_url: # record params in url and switch it to '*'
			if pattern.match(i):
				add_param_list.append(i)
				splited_url[splited_url.index(i)] = '*'
		self.callback_index.register(splited_url,callback)
		def callback_maker(user_callback): # Get user_func and make mixed func
			#'*args','**kw' are for get/post_data,headers,ip,<params> use
			def exposed_callback(*args,**kw):
				do_resp = [True]				#sign, use list so that can change by inner func
				param_list = add_param_list 	#only key
				add_params = kw['url_params'] 	#only value
				param_dict = dict()				#k & v
				for k in param_list and v in add_params:
					param_dict[k] = v
					
				info_dict = dict(
					get_sock = get_sock_outer(do_resp), 
					request_headers = kw['headers'],
					args = kw['args'],
					data = kw['data'],
					params = param_dict
				)
				
				resp_info = user_callback(**info_dict)
				resp_info['do_resp'] = do_resp[0]
				return resp_info
			return exposed_callback
		return callback_maker
		
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
		
	def site_map(self):
		return self.callback_index.tree()
		
		