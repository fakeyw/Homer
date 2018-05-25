from base.tiny_Q import QPOOL
from main.Sockets import Socket_layer
from main.Workers import Worker_thread
from main.Index_for_url import Url_index
from main.Tasks import Instant_task,Response_task
import threading
import time
import re
from base.http_parser import Http_parser
parser = Http_parser()

__LOCK__ = threading.Lock()


'''
The core of every part
Having all sources
with funcs to manage them.
'''
class Homer_owner(object): # <- add some setting here?
	def __init__(self,max_worker=30):
		self.callback_index = Url_index()
		print('[*]Initiating sources...')
		self.Qs = QPOOL() 
		self.resp_Q = self.Qs.createQ(name='resp',max_len=5000)
		self.Socket_layer = Socket_layer()
		self.worker_pool = self.set_worker(max_worker)
		
		
	def run(self,host,port):
		for w in self.worker_pool:
			w.start()
		self.Socket_layer.run(host=host,port=port)
		print('\nReady for service')
		
	def set_worker(self,max_worker):
		print(' Set workers: %s' % max_worker)
		workers = [Worker_thread(self.get_task) for i in range(max_worker)]
		return workers
		
	def register(self,url,**kw): # Get register params
		pattern = re.compile(r'^<(.*)>$')
		splited_url = parser.url_split(url)
		add_param_list = []
		
		for i in splited_url: # record params in url and switch it to '$'
			if pattern.match(i):
				add_param_list.append(i)
				splited_url[splited_url.index(i)] = '$'
	
		def callback_maker(user_callback): # Get user_func and make mixed func
			#'*args','**kw' are for get/post_data,headers,ip,<params> use
			def exposed_callback(*args,**kw):
				do_resp = [True]				#sign, use list so that can change by inner func
				param_list = add_param_list 	#only key
				add_params = kw['url_params'] 	#only value
				param_dict = dict()				#k & v
				for (k,v) in zip(param_list,add_params):
					k = pattern.findall(k)[0]
					param_dict[k] = v
				
				test = 1
				info_dict = dict(
					method = kw['method'],
					get_sock = kw['get_sock_outer'](do_resp), 
					request_headers = kw['headers'],
					args = kw['args'],
					data = kw['data'],
					url_params = param_dict
				)
				
				resp_info = user_callback(**info_dict)
				if resp_info == None:
					resp_info = dict()
				resp_info['do_resp'] = do_resp[0]
				return resp_info

			self.callback_index.register(splited_url,exposed_callback)
		return callback_maker
		
	def put_resp(self,sock,info):
		if 'headers' not in info:
			info['headers'] = {}
		if 'text' not in info:
			info['text'] = ''
		resp_task_info = {'sock':sock,'info':info}
		__LOCK__.acquire()
		self.resp_Q.put(resp_task_info)
		__LOCK__.release()
		
	def get_task(self):
		task = None
		__LOCK__.acquire()
		if not self.resp_Q.is_empty(): #resp first
			resp_info = self.resp_Q.get()
			print('[*]Response task: to %s:%s' % resp_info['sock'][0])
			__LOCK__.release()
			task = Response_task(resp_info)
		else:
			current_accepted = self.Socket_layer.accepted_queue.get()
			__LOCK__.release()
			if current_accepted == None:
				return None
			else:
				task = Instant_task(current_accepted,self.callback_index)
		return task
		
		