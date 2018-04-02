from base.http_parser import Http_parser
parser = Http_parser()

class Task(object):
	def __init__(self,callback = None,*args,**kw):
		self.callback = callback
		self.args = args
		self.kw = kw

#Instantly make a response (as soon as quickly, need't wait for some msg)
#including receive, dicide callback and return
class Instant_task(Task): #resp part is included in callback function
	def __init__(self,accepted,callback_index,callback=None,*args,**kw):
		super(Instant_task,self).__init__(callback,*args,**kw)
		self.sock = accepted[0]
		self.addr = accepted[1]
		self.callback_index = callback_index
	
	def get_sock_outer(self,sign):
		def get_sock():
			sign[0] = False
			return [self.addr,self.sock]
		return get_sock
		
		
	def run(self): #read -> parse -> callback
		http = b''
		while True:
			data = self.sock.recv(1024)
			if data:
				http += data
			else:
				break
			if len(data) < 1024:
				break
		info = parser.parse(http)
		Notice = '[*]Received request from: %s:%s ' % self.addr
		Notice += info['url']
		print(Notice)
		splited_url = parser.url_split(info['url'])
		callback,url_params = self.callback_index.url_find(splited_url) 			
		if callback == None:
			'''Write 404 page'''
			callback,url_params = self.callback_index.url_find(['404'])
		info['url_params'] = url_params
		resp_info = callback(**info,get_sock_outer=self.get_sock_outer)
		#↑ Put all parames & get_sock() constructer in outer_callback
		'''
		operate like this, it works:
		def e(a,b):
			pass
		e(**{'a':1},**{'b':2})
		'''
		if resp_info.pop('do_resp') == True:				
			response = parser.pack(**resp_info)
			#print(response)
			self.sock.sendall(response)
			self.sock.close()
			
'''
Each request will trigger an Instant_task.
But, u can take the socket acception out in a 'Message Waiting Queue'
Then retuen 'None' to skip the rest of callback
For example:
request for new msg from a friend
1. If you have it now, just return text to Instant_task.run()
2. If not, use get_sock() in callback so that this can free current worker. 
	When you got the new msg, put {'sock':...,'headers':{...},'text':'...'} 
	('status_code' & 'status_msg' in resp are also avaliable)
	in queue 'resp_Q' like:
	Site = Request_handler()
	...
	...
	Site.put_resp(	
			waiting['ZIM7KASD22SD'], 	#sock
			{							#info
			'headers': #not necessary
				{
					'Server':'Python'
				},
			'text':'Hello, world!'
			}	
		)
Then it will be taken by a worker as a Response_task
'''
class Response_task(Task): #Take a HANGED UP link and only make a response
	def __init__(self,resp_info,*args,**kw):
		super(Response_task,self).__init__(*args,**kw)
		[self.addr,self.sock] = resp_info['sock']
		self.info = resp_info['info']
		#print(self.info)
		
	def run(self):
		response = parser.pack(headers=self.info.pop('headers'),text=self.info.pop('text'),**self.info)
		#print(response)
		self.sock.sendall(response.encode('utf-8'))
		self.sock.close()
		
		
		