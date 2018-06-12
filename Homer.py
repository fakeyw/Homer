import sys
import os
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))

from base.tiny_Q import QPOOL
from main.Sockets import Link_handler
from main.Workers import Worker_handler
from main.Urls import Url_handler
from main.Files import File_handler
import threading
import time
from main.Tasks import Instant_task,Response_task
__LOCK__ = threading.Lock()

class Homer(object):
	def __init__(self,ssl=False,cert=None,key=None):
		print('Welcome to be with Homer!')
		print('Github: https://github.com/fakeyw/Homer')
		print('[*]Initiating sources...')
		self.Qs = QPOOL() 
		self.resp_Q = self.Qs.createQ(name='resp',max_len=5000)
		self.Receiver = Link_handler(ssl,cert,key) #这里应该有一些参数
		self.Consume_factory = Worker_handler(self.get_task) #这里应该有一些参数
		self.Web_index = Url_handler()
	
	def register(self,url,**kw):
		return self.Web_index.Http_register(url,**kw)
		
	def site_map(self):
		return self.Web_index.site_map()
		
	def run(self,host='127.0.0.1',port=8989):
		self.Consume_factory.run()
		self.Receiver.run(host=host,port=port)
		print('\nReady for service')
		print("\nSite map:\n%s\n" % self.site_map())
		
	def get_task(self):
		#pass queue needed in func to caller, temporarily 
		resp_Q = self.resp_Q
		accepted_Q = self.Receiver.accepted_queue
		index = self.Web_index.callback_index
		
		task = None
		__LOCK__.acquire()
		if not resp_Q.is_empty(): #resp first
			resp_info = self.resp_Q.get()
			print('[*]Response task: to %s:%s' % resp_info['sock'][0])
			__LOCK__.release()
			task = Response_task(resp_info)
		else:
			current_accepted = accepted_Q.get()
			__LOCK__.release()
			if current_accepted == None:
				return None
			else:
				task = Instant_task(current_accepted,index)
		return task
		
	def put_resp(self,sock,info):
		if 'headers' not in info:
			info['headers'] = {}
		if 'text' not in info:
			info['text'] = ''
		resp_task_info = {'sock':sock,'info':info}
		__LOCK__.acquire()
		self.resp_Q.put(resp_task_info)
		__LOCK__.release()
		
	def info(self):
		pass
	
	
	
	